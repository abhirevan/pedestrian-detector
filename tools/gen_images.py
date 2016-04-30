import matplotlib.pyplot as plt
import numpy as np
import os
import xml.etree.cElementTree as ET
import cv2
import sys
import matplotlib.pyplot as plt

XML_FOLDER = "/home/abhijitcbim/git/pedestrian-detector/data/PedestrianImage/data/Annotations"
IM_FOLDER = "/home/abhijitcbim/git/pedestrian-detector/data/PedestrianImage/data/Images"
PROPOSAL_FOLDER = "/home/abhijitcbim/git/pedestrian-detector/data/PedestrianImage/results/Semantic/Main"
AN_IM_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB/annote_images_xml"
RESULTS_AN_IM_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB/annote_images_results"


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

def get_result_class_color(class_name):
    if class_name == 'person':
        return "aqua"
    elif class_name == 'people':
        return "maroon"
    elif class_name == 'person-fa':
        return "limegreen"
    elif class_name == 'person?':
        return "violet"
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

def generate_annotated_result(txt):
    #for txt in os.listdir(folder):
        if txt.endswith(".txt"):
            txt_path =os.path.join(PROPOSAL_FOLDER, txt)
            all_proposals = {}
            with open(txt_path) as f:
                class_name = "person"
                if txt_path.find("person") != -1:
                     if txt_path.find("person-fa") != -1:
                         class_name = "person-fa"
                     elif txt_path.find("person?") != -1:
                         class_name = "person?"
                elif txt_path.find("people") != -1:
                    class_name = "people"

                for proposal in f:
                    proposal_arr = proposal.split();
                    proposal_arr.extend([class_name])
                    all_proposals.setdefault(proposal_arr[0], []).append(proposal_arr)
            
            for key, value in all_proposals.iteritems():
                xml_root = ET.parse(os.path.join(XML_FOLDER, key+".xml")).getroot()
                im = cv2.imread(os.path.join(IM_FOLDER, (key + '.jpg')))
                im = im[:, :, (2, 1, 0)]
                fig, ax = plt.subplots(figsize=(12, 12))
                ax.imshow(im, aspect='equal')
                for proposal in value:
                    color = get_result_class_color(proposal[6])
                    x1 = int(float(proposal[2]))
                    y1 = int(float(proposal[3]))
                    x2 = int(float(proposal[4]))
                    y2 = int(float(proposal[5]))
                    ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                               edgecolor=color, linewidth=2))
                    plt.axis('off')
                plt.savefig(os.path.join(RESULTS_AN_IM_FOLDER, (key + "_"+proposal[6]+"_pred.jpg")))

                im = cv2.imread(os.path.join(IM_FOLDER, (key + '.jpg')))
                im = im[:, :, (2, 1, 0)]
                fig, ax = plt.subplots(figsize=(12, 12))
                ax.imshow(im, aspect='equal')
                for object in xml_root.findall('object'):
                    class_name = object.find('name').text
                    if class_name == proposal[6]:
                        x1 = int(object.find('bndbox/xmin').text)
                        y1 = int(object.find('bndbox/ymin').text)
                        x2 = int(object.find('bndbox/xmax').text)
                        y2 = int(object.find('bndbox/ymax').text)
                        color = get_class_color(class_name)
                        ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                                   edgecolor=color, linewidth=2))
                    plt.axis('off')
                plt.savefig(os.path.join(RESULTS_AN_IM_FOLDER, (key + "_"+proposal[6]+"_th.jpg")))

                plt.tight_layout()
                # plt.show()
                
                plt.close()
                name = raw_input("?")
                print name


if __name__ == '__main__':
    #generate_annoted_truth(XML_FOLDER)
    generate_annotated_result(PROPOSAL_FOLDER+"/comp4_03f9a797-fb69-4760-86b3-048f0924b364_det_test_people.txt")