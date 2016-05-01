import matplotlib.pyplot as plt
import numpy as np
import os
import xml.etree.cElementTree as ET
import cv2
import sys
import matplotlib.pyplot as plt

XML_FOLDER = "/home/bolt3/git/pedestrian-detector/data/PedestrianImage/data/Annotations"
IM_FOLDER = "/home/bolt3/git/pedestrian-detector/data/PedestrianImage/data/Images"
TEST_FOLDER = "/home/bolt3/git/pedestrian-detector/data/PedestrianImage/data/ImageSets/Main"

def save_list_readable(ip_list, filename):
    with open(filename, 'w') as f:
        for s in ip_list:
            f.write(s + '\n')

def generate_test_case():
    txt_path = os.path.join(TEST_FOLDER, "test.txt")
    with open(txt_path) as f:
        test_cases = {}

        for file_token in f:
            file_token_truncated = file_token.replace("\n", "")
            xml_root = ET.parse(os.path.join(XML_FOLDER,  file_token_truncated + ".xml")).getroot()
            occlusion = xml_root.findall('occ')
            occ_flag = "no_occ"
            scale_flag = "far_scale"
            for object in xml_root.findall('object'):
                class_name = object.find('name').text
                x1 = int(object.find('bndbox/xmin').text)
                y1 = int(object.find('bndbox/ymin').text)
                x2 = int(object.find('bndbox/xmax').text)
                y2 = int(object.find('bndbox/ymax').text)
                areat = abs((x1 - x2) * (y1 - y2))
                vx1 = int(object.find('vbndbox/xmin').text)
                vy1 = int(object.find('vbndbox/ymin').text)
                vx2 = int(object.find('vbndbox/xmax').text)
                vy2 = int(object.find('vbndbox/ymax').text)
                areav = abs((vx1 - vx2) * (vy1 - vy2))

                if areat <= 300:
                    scale_flag = "far_scale"
                elif areat > 300 and areat < 800 and scale_flag != "far_scale":
                    scale_flag = "medium_scale"
                elif areat>=800 and (scale_flag != "far_scale" or scale_flag != "medium_scale"):
                    scale_flag = "near_scale"

                occlusion = int(object.find('occ').text)

                if occlusion == 1:
                    if areat != 0:
                        visible_area = areav/areat;
                        if visible_area <= 0.35 and occ_flag == "no_occ":
                            occ_flag = "partial_occ"
                        elif visible_area > 0.35 and (occ_flag == "no_occ" or occ_flag == "partial_occ"):
                            occ_flag = "heavy_occ"
                    else:
                        occ_flag = "heavy_occ"
                elif (occ_flag != "partial_occ" or occ_flag != "partial_occ"):
                    occ_flag = "no_occ"


            test_cases.setdefault(occ_flag, []).append(file_token_truncated)
            test_cases.setdefault(scale_flag, []).append(file_token_truncated)

        for key, value in test_cases.iteritems():
            save_list_readable(value,os.path.join(TEST_FOLDER, key + ".txt"));
            #print key,value,'\n'

if __name__ == '__main__':
    generate_test_case()



