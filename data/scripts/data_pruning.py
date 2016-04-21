import os

__author__ = "abhirevan"

XML_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB/annotations"
DEST_FOLDER = "/home/abhijitcbim/data/PedDetectionIMDB/annotations-xml"


def remove_first_line(filename):
    with open(filename, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(filename, 'w') as fout:
        fout.writelines(data[1:])


if __name__ == '__main__':
    for path, subdirs, files in os.walk(XML_FOLDER):
        for name in files:
            filename = os.path.join(path, name)
            remove_first_line(filename)
