#!/usr/bin/env python

# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""Test a Fast R-CNN network on an image database."""

import _init_paths
from fast_rcnn.test import test_net
from fast_rcnn.config import cfg, cfg_from_file, cfg_from_list
from datasets.factory import get_imdb
import caffe
import argparse
import pprint
import time, os, sys
import pandas as pd


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


def run_test_net(gpu_id, caffemodel, prototxt, imdb_name, cfg_file):
    if cfg_file is not None:
        cfg_from_file(cfg_file)

    cfg.GPU_ID = gpu_id

    print('Using config:')
    pprint.pprint(cfg)

    while not os.path.exists(caffemodel):
        print('Waiting for {} to exist...'.format(caffemodel))
        time.sleep(10)

    caffe.set_mode_gpu()
    caffe.set_device(gpu_id)
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)
    net.name = os.path.splitext(os.path.basename(caffemodel))[0]

    imdb = get_imdb(imdb_name)
    if not cfg.TEST.HAS_RPN:
        imdb.set_proposal_method(cfg.TEST.PROPOSAL_METHOD)

    n, _ = os.path.splitext(caffemodel)
    paths = splitall(n)

    proposal_prefix = paths[-1]

    return test_net(net, imdb, max_per_image=100, vis=False, proposal_prefix=proposal_prefix)


def run_test_nets(gpu_id, caffemodel, imdbs, prototxt, cfg_file, res_file):
    df_results = pd.DataFrame()
    for imdb in imdbs:
        results = run_test_net(gpu_id, caffemodel, prototxt, imdb, cfg_file)
        for result in results:
            result['file'] = caffemodel
            result['imdb'] = imdb
        df_results = df_results.append(results, ignore_index=True)

    df_results.to_csv(res_file)


if __name__ == '__main__':
    gpu_id = 0
    caffemodel = "output/faster_rcnn_end2end/train/backup/resnet_faster_rcnn_iter_200000.caffemodel"
    imdbs = ['ped_far_scale', 'ped_medium_scale', 'ped_near_scale', 'ped_no_occ',
             'ped_partial_occ', 'ped_heavy_occ']
    prototxt = "models/pascal_voc/RESNET/faster_rcnn_end2end/test.prototxt"
    cfg_file = "experiments/cfgs/faster_rcnn_end2end.yml"
    res_file = "/home/bolt3/results/Resnet50_cases_1.csv"
    run_test_nets(gpu_id, caffemodel, imdbs, prototxt, cfg_file, res_file)

    # run_test_net(gpu_id,caffemodel, prototxt, imdb_name, cfg_file)
