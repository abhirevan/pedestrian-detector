import cPickle
import numpy as np
import os
import scipy.sparse
import uuid
import xml.etree.ElementTree as ET

from datasets.imdb import imdb

from voc_eval import voc_eval

__author__ = "abhirevan"


class PedestrianDataset(imdb):
    def __init__(self, image_set, devkit_path):
        imdb.__init__(self, image_set)
        self._image_set = image_set
        self._devkit_path = devkit_path
        print "self._devkit_path:", self._devkit_path
        self._data_path = os.path.join(self._devkit_path, 'data')
        self._classes = ('__background__', 'person', 'people', 'person-fa', 'person?')
        self._class_to_ind = dict(zip(self.classes, xrange(self.num_classes)))
        self._image_ext = '.jpg'
        self._image_index = self._load_image_set_index()
        self._salt = str(uuid.uuid4())
        self._comp_id = 'comp4'
        # PASCAL specific config options
        self.config = {'cleanup': True,
                       'use_salt': True,
                       'use_diff': False,
                       'matlab_eval': False,
                       'rpn_file': None,
                       'min_size': 2}
        assert os.path.exists(self._devkit_path), \
            'VOCdevkit path does not exist: {}'.format(self._devkit_path)
        assert os.path.exists(self._data_path), \
            'Path does not exist: {}'.format(self._data_path)

    def image_path_at(self, i):
        """
        Return the absolute path to image i in the image sequence.
        """
        return self.image_path_from_index(self._image_index[i])

    def image_path_from_index(self, index):
        """
        Construct an image path from the image's "index" identifier.
        """
        image_path = os.path.join(self._data_path, 'Images',
                                  index + self._image_ext)
        assert os.path.exists(image_path), \
            'Path does not exist: {}'.format(image_path)
        return image_path

    def _load_image_set_index(self):
        """
        Load the indexes listed in this dataset's image set file.
        """
        # Example path to image set file:
        # self._devkit_path + /VOCdevkit2007/VOC2007/ImageSets/Main/val.txt
        image_set_file = os.path.join(self._data_path, 'ImageSets', 'Main',
                                      self._image_set + '.txt')
        assert os.path.exists(image_set_file), \
            'Path does not exist: {}'.format(image_set_file)
        with open(image_set_file) as f:
            image_index = [x.strip() for x in f.readlines()]
        return image_index

    def gt_roidb(self):
        """
        Return the database of ground-truth regions of interest.


        This function loads/saves from/to a cache file to speed up future calls.
        """
        cache_file = os.path.join(self.cache_path, self.name + '_gt_roidb.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as fid:
                roidb = cPickle.load(fid)
            print '{} gt roidb loaded from {}'.format(self.name, cache_file)
            return roidb

        gt_roidb = [self._load_ped_annotation(index)
                    for index in self.image_index]
        with open(cache_file, 'wb') as fid:
            cPickle.dump(gt_roidb, fid, cPickle.HIGHEST_PROTOCOL)
        print 'wrote gt roidb to {}'.format(cache_file)
        return gt_roidb

    def _load_ped_annotation(self, index):
        """
        Load image and bounding boxes info from XML file in the PASCAL VOC
        format.
        """
        filename = os.path.join(self._data_path, 'Annotations', index + '.xml')
        tree = ET.parse(filename)
        objs = tree.findall('object')

        table_objs = []
        for obj in objs:
            if obj.find('name').text in self._classes:
                table_objs.append(obj)
        num_objs = len(table_objs)

        # boxes = np.zeros((num_objs, 4), dtype=np.uint16)
        boxes = np.zeros((num_objs, 4), dtype=np.uint16)
        gt_classes = np.zeros(num_objs, dtype=np.int32)
        overlaps = np.zeros((num_objs, self.num_classes), dtype=np.float32)
        # "Seg" area for pascal is just the box area
        seg_areas = np.zeros(num_objs, dtype=np.float32)

        # Load object bounding boxes into a data frame.
        for ix, obj in enumerate(objs):
            bbox = obj.find('bndbox')
            # Make pixel indexes 0-based
            x1 = float(bbox.find('xmin').text)
            y1 = float(bbox.find('ymin').text)
            x2 = float(bbox.find('xmax').text)
            y2 = float(bbox.find('ymax').text)
            cls = self._class_to_ind[obj.find('name').text.lower().strip()]
            boxes[ix, :] = [x1, y1, x2, y2]
            gt_classes[ix] = cls
            overlaps[ix, cls] = 1.0
            seg_areas[ix] = (x2 - x1 + 1) * (y2 - y1 + 1)
        overlaps = scipy.sparse.csr_matrix(overlaps)

        return {'boxes': boxes,
                'gt_classes': gt_classes,
                'gt_overlaps': overlaps,
                'flipped': False,
                'seg_areas': seg_areas}

    def _get_comp_id(self):
        return self._comp_id + '_' + self._salt

    def _set_comp_id(self, comp_id):
        self._comp_id = comp_id

    def _get_ped_results_file_template(self):
        filename = self._get_comp_id() + '_det_' + self._image_set + '_{:s}.txt'
        path = os.path.join(
            self._devkit_path,
            'results',
            'Semantic',
            'Main',
            filename)
        return path

    def _get_voc_results_file_template(self):
        # VOCdevkit/results/VOC2007/Main/<comp_id>_det_test_aeroplane.txt
        filename = self._get_comp_id() + '_det_' + self._image_set + '_{:s}.txt'
        path = os.path.join(
            self._devkit_path,
            'results',
            'Semantic',
            'Main',
            filename)
        return path

    def _write_ped_results_file(self, all_boxes):
        for cls_ind, cls in enumerate(self.classes):
            if cls == '__background__':
                continue
            print 'Writing {} VOC results file'.format(cls)
            filename = self._get_ped_results_file_template().format(cls)
            with open(filename, 'wt') as f:
                for im_ind, index in enumerate(self.image_index):
                    dets = all_boxes[cls_ind][im_ind]
                    if dets == []:  # cannot use 'if not dets' due to numpy to boolean conversion problem
                        continue
                    for k in xrange(dets.shape[0]):
                        f.write('{:s} {:.5f} {:.1f} {:.1f} {:.1f} {:.1f}\n'.
                                format(index, dets[k, -1], dets[k, 0], dets[k, 1], dets[k, 2], dets[k, 3]))

    def _do_python_eval(self, output_dir='output'):
        # annopath = os.path.join(self._devkit_path, 'VOC' + self._year, 'Annotations', '{:s}.xml')
        annopath = os.path.join(self._data_path, 'Annotations', '{:s}.xml')
        # imagesetfile = os.path.join(self._devkit_path, 'VOC' + self._year, 'ImageSets', 'Main',
        #                            self._image_set + '.txt')
        imagesetfile = os.path.join(self._data_path, 'ImageSets', 'Main', self._image_set + '.txt')
        cachedir = os.path.join(self._devkit_path, 'annotations_cache')
        aps = []
        # The PASCAL VOC metric changed in 2010
        use_07_metric = True  # if int(self._year) < 2010 else False
        print 'VOC07 metric? ' + ('Yes' if use_07_metric else 'No')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        results = []
        for i, cls in enumerate(self._classes):
            if cls == '__background__':
                continue
            filename = self._get_voc_results_file_template().format(cls)
            rec, prec, ap = voc_eval(
                filename, annopath, imagesetfile, cls, cachedir, ovthresh=0.5,
                use_07_metric=use_07_metric)
            aps += [ap]
            result = {}
            result['cls'] = cls
            result['rec'] = rec
            result['prec'] = prec
            result['ap'] = ap
            results.append(result)
            print('AP for {} = {:.4f}'.format(cls, ap))
            with open(os.path.join(output_dir, cls + '_pr.pkl'), 'w') as f:
                cPickle.dump({'rec': rec, 'prec': prec, 'ap': ap}, f)
        print('Mean AP = {:.4f}'.format(np.mean(aps)))
        print('~~~~~~~~')
        print('Results:')
        for ap in aps:
            print('{:.3f}'.format(ap))
        print('{:.3f}'.format(np.mean(aps)))
        print('~~~~~~~~')
        return results

    def evaluate_detections(self, all_boxes, output_dir, proposal_prefix=None):
        self._write_ped_results_file(all_boxes)
        results = self._do_python_eval(output_dir)
        if self.config['matlab_eval']:
            self._do_matlab_eval(output_dir)

        for cls in self._classes:
            if cls == '__background__':
                continue
            filename = self._get_voc_results_file_template().format(cls)
            print filename
        return results
