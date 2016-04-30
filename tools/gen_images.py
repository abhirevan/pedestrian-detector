import matplotlib.pyplot as plt
import numpy as np
import os
import xml.etree.cElementTree as ET
import cv2
import sys
import matplotlib.pyplot as plt

XML_FOLDER = "/home/abhijitcbim/git/pedestrian-detector/data/PedestrianImage/data/Annotations"
IM_FOLDER = "/home/abhijitcbim/git/pedestrian-detector/data/PedestrianImage/data/Images"
AN_IM_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB/annote_images"


def get_class_color(class_name):
    if class_name == 'person':
        return "blue"
    elif class_name == 'people':
        return "red"
    elif class_name == 'person-fa':
        return "green"
    elif class_name == 'person?':
        return "purple"
    else:
        print "ERROR!"
        sys.exit(1)


def generate_annoted_truth(folder):
    i = 0
    for xml in os.listdir(folder):
        if i % 1000 == 0:
            print ",",
        i += 1
        if xml.endswith(".xml"):
            shotname, _ = os.path.splitext(xml)
        xml_root = ET.parse(os.path.join(XML_FOLDER, xml)).getroot()
        im = cv2.imread(os.path.join(IM_FOLDER, (shotname + '.jpg')))
        im = im[:, :, (2, 1, 0)]
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.imshow(im, aspect='equal')
        for object in xml_root.findall('object'):
            class_name = object.find('name').text
            x1 = int(object.find('bndbox/xmin').text)
            y1 = int(object.find('bndbox/ymin').text)
            x2 = int(object.find('bndbox/xmax').text)
            y2 = int(object.find('bndbox/ymax').text)
            # print x1,y1,x2,y2
            vx1 = int(object.find('vbndbox/xmin').text)
            vy1 = int(object.find('vbndbox/ymin').text)
            vx2 = int(object.find('vbndbox/xmax').text)
            vy2 = int(object.find('vbndbox/ymax').text)
            # print vx1,vy1,vx2,vy2
            color = get_class_color(class_name)
            ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                       edgecolor=color, linewidth=2))
            plt.axis('off')
        plt.tight_layout()
        # plt.show()
        plt.savefig(os.path.join(AN_IM_FOLDER, (shotname + ".jpg")))
        plt.close()


if __name__ == '__main__':
    generate_annoted_truth(XML_FOLDER)
