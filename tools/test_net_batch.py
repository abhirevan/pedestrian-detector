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


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Test a Fast R-CNN network pipeline')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU id to use',
                        default=0, type=int, required=True)
    parser.add_argument('--dir', dest='dir',
                        help='Directory of the model files',
                        default="", type=str, required=True)
    parser.add_argument('--models', dest='model_files',
                        help='Text file with names of models',
                        default=None, type=str, required=True)
    parser.add_argument('--prototxt', dest='prototxt',
                        help='prototxt', default=None, type=str, required=True)
    parser.add_argument('--imdb', dest='imdb_name',
                        help='dataset to test',
                        default='ped_test_small', type=str, required=True)
    parser.add_argument('--cfg', dest='cfg_file',
                        help='cfg',
                        default='experiments/cfgs/faster_rcnn_end2end.yml', type=str)
    parser.add_argument('--res', dest='res_file',
                        help='result file',
                        default='', type=str,required=True)
    args = parser.parse_args()
    return args


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

    return test_net(net, imdb, max_per_image=100, vis=False)


def run_test_nets(gpu_id, dir, model_files, prototxt, imdb_name, cfg_file,res_file):
    models = [line.rstrip('\n') for line in open(os.path.join(dir, model_files))]
    df_results = pd.DataFrame()
    for model in models:
        results = run_test_net(gpu_id, os.path.join(dir, model), prototxt, imdb_name, cfg_file)
        for result in results:
            result['file'] = model
        df_results = df_results.append(results,ignore_index =True)

    df_results.to_csv(os.path.join(dir, res_file))


if __name__ == '__main__':
    # args = parse_args()
    gpu_id = 0
    # dir = '/home/abhijitcbim/git/pedestrian-detector/output/faster_rcnn_end2end/train/backup'
    # model_files = 'test.txt'


    args = parse_args()

    print('Called with args:')
    print(args)

    run_test_nets(args.gpu_id, args.dir, args.model_files, args.prototxt, args.imdb_name, args.cfg_file,args.res_file)

    # run_test_net(gpu_id,caffemodel, prototxt, imdb_name, cfg_file)
