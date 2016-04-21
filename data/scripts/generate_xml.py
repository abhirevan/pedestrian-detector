import os
import pandas as pd
import xml.etree.cElementTree as ET

XML_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB/annotations"
DEST_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB/annotations_xml"
ROOT_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB"


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def save_list_readable(ip_list, filename):
    with open(filename, 'w') as f:
        for s in ip_list:
            f.write(s + '\n')


def load_list_readable(filename):
    with open(filename, 'r') as f:
        return [line.rstrip('\n') for line in f]


def get_unique_name(filename):
    file_paths = splitall(filename)
    l = len(file_paths)

    target_file = os.path.join(DEST_FOLDER, (
        file_paths[l - 3] + "_" + file_paths[l - 2] + "_" + file_paths[l - 1]))
    return target_file


VOC_XML = "format/voc_xml.xml"
VOC_OBJECT_XML = "format/voc_object_xml.xml"


class VocXml(object):
    def __init__(self, voc_xml_dict):
        self.__pageDocTree = ET.parse(VOC_XML)
        root = self.__pageDocTree.getroot()
        # update the __pageDocTree element
        for key, val in voc_xml_dict.iteritems():
            root.find(key).text = val

    def add_object(self, obj_dict):
        objectTree = ET.parse(VOC_OBJECT_XML)

        root = objectTree.getroot()
        # Update the xtree
        for key, val in obj_dict.iteritems():
            root.find(key).text = val
        self.__pageDocTree.getroot().append(root)

    def add_objects(self, obj_dicts):
        for i in range(len(obj_dicts)):
            self.add_object(obj_dicts[i])

    def save_xml(self, filename):
        self.__pageDocTree.write(filename)


def convert_to_xml(folder):
    columns = ["lbl", "bb_x", "bb_y", "bb_w", "bb_h", "occ", "bbv_x", "bbv_y", "bbv_w", "bbv_h", "ign", "ang"]
    i = 0
    for path, subdirs, files in os.walk(folder):
        for name in files:
            i += 1
            txt_file = os.path.join(path, name)
            filename,_=os.path.splitext(txt_file)
            filename +=".xml"
            # print txt_file
            if os.stat(txt_file).st_size != 0:
                target_name = get_unique_name(filename)
                voc_dict = {}
                voc_dict['filename'] = target_name
                voc_dict['size/width'] = "480"
                voc_dict['size/height'] = "640"
                voc_dict['size/depth'] = "3"
                voc_xml = VocXml(voc_dict)
                df = pd.read_csv(txt_file, header=None, sep=r"\s+", names=columns)
                for index, row in df.iterrows():
                    obj_dict = {}
                    obj_dict['name'] = row['lbl']
                    obj_dict['bndbox/xmin'] = str(row['bb_x'])
                    obj_dict['bndbox/ymin'] = str(row['bb_y'])
                    obj_dict['bndbox/xmax'] = str(row['bb_x'] + row['bb_w'])
                    obj_dict['bndbox/ymax'] = str(row['bb_y'] + row['bb_h'])
                    obj_dict['vbndbox/xmin'] = str(row['bbv_x'])
                    obj_dict['vbndbox/ymin'] = str(row['bbv_y'])
                    obj_dict['vbndbox/xmax'] = str(row['bbv_x'] + row['bbv_w'])
                    obj_dict['vbndbox/ymax'] = str(row['bbv_y'] + row['bbv_h'])
                    obj_dict['occ'] = str(row['occ'])
                    obj_dict['ign'] = str(row['ign'])
                    obj_dict['ang'] = str(row['ang'])
                    voc_xml.add_object(obj_dict)
                voc_xml.save_xml(os.path.join(DEST_FOLDER, target_name))
            if i % 100 == 0:
                print ".",
            if i % 1000 == 0:
                print i, " done"


def convert_to_csv(folder):
    df_final = pd.DataFrame()
    columns = ["lbl", "bb_x", "bb_y", "bb_w", "bb_h", "occ", "bbv_x", "bbv_y", "bbv_w", "bbv_h", "ign", "ang"]
    empty_files = []
    i = 0
    for path, subdirs, files in os.walk(folder):
        for name in files:
            i += 1
            txt_file = os.path.join(path, name)
            # print txt_file

            if os.stat(txt_file).st_size == 0:
                empty_files.append(get_unique_name(txt_file))
            else:
                df = pd.read_csv(txt_file, header=None, sep=r"\s+", names=columns)
                df["fname"] = get_unique_name(txt_file)
                df_final = df_final.append(df)
            if i % 100 == 0:
                print ".",
            if i % 1000 == 0:
                print i, " done"

    df_final.to_csv(os.path.join(ROOT_FOLDER, "annotations.csv"))
    save_list_readable(empty_files, os.path.join(ROOT_FOLDER, "empty_files.txt"))


if __name__ == '__main__':
    convert_to_csv(XML_FOLDER)
    convert_to_xml(XML_FOLDER)
