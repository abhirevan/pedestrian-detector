import matplotlib.pyplot as plt
import numpy as np
import os
import xml.etree.cElementTree as ET
import cv2
import sys
import matplotlib.pyplot as plt

XML_FOLDER = "/home/bolt3/git/pedestrian-detector/data/PedestrianImage/data/Annotations"
IM_FOLDER = "/home/bolt3/git/pedestrian-detector/data/PedestrianImage/data/Images"
PROPOSAL_FOLDER = "/home/bolt3/git/pedestrian-detector/data/PedestrianImage/results/Semantic/Main"
AN_IM_FOLDER = "/home/bolt3/data/PedDetectionIMDB/annote_images_xml"
RESULTS_AN_IM_FOLDER = "/home/bolt3/data/PedDetectionIMDB/annote_images_results"


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
        return "royalblue"
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
            threshhold = 0.8
            with open(txt_path) as f:
                class_name = "person"
                if txt_path.find("person") != -1:
                     if txt_path.find("person-fa") != -1:
                         class_name = "person-fa"
                         threshhold = 0.89
                     elif txt_path.find("person?") != -1:
                         class_name = "person?"
                         threshhold = 0.90
                     else:
                         class_name = "person"
                         threshhold = 0.79
                elif txt_path.find("people") != -1:
                    class_name = "people"
                    threshhold = 0.83

                for proposal in f:
                    proposal_arr = proposal.split();
                    proposal_arr.extend([class_name])
                    all_proposals.setdefault(proposal_arr[0], []).append(proposal_arr)
            i = 0
            for key, value in all_proposals.iteritems():
                im = cv2.imread(os.path.join(IM_FOLDER, (key + '.jpg')))
                im = im[:, :, (2, 1, 0)]
                fig, ax = plt.subplots(figsize=(12, 12))
                ax.imshow(im, aspect='equal')
                xml_root = ET.parse(os.path.join(XML_FOLDER, key + ".xml")).getroot()
                for object in xml_root.findall('object'):
                    class_name = object.find('name').text
                    if class_name == proposal[6]:
                        x1 = int(object.find('bndbox/xmin').text)
                        y1 = int(object.find('bndbox/ymin').text)
                        x2 = int(object.find('bndbox/xmax').text)
                        y2 = int(object.find('bndbox/ymax').text)
                        color = "maroon"
                        ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                                   edgecolor=color, linewidth=2))
                    plt.axis('off')

                for proposal in value:
                    if float(proposal[1]) > threshhold:
                        color = "royalblue"
                        x1 = int(float(proposal[2]))
                        y1 = int(float(proposal[3]))
                        x2 = int(float(proposal[4]))
                        y2 = int(float(proposal[5]))
                        ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                                   edgecolor=color, linewidth=2))
                        ax.text(x1, y1, proposal[1], color="white", bbox=dict(facecolor=color, edgecolor=color))
                        plt.axis('off')


                plt.savefig(os.path.join(RESULTS_AN_IM_FOLDER, (class_name+"/"+key + "_"+proposal[6]+"_pred_th.jpg")))

                plt.tight_layout()
                plt.close()
                if i%150 == 0 and i !=0:
                    break
                    #name = raw_input("?")
                    #print name
                i+=1


if __name__ == '__main__':
    #generate_annoted_truth(XML_FOLDER)
    generate_annotated_result(PROPOSAL_FOLDER+"/comp4_886d55dd-9c07-4158-be79-72785eeea501_det_test_person.txt")

    #people - 83
    #person-fa -89
    #person? - 90
    #person - 79


