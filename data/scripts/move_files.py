import os
import shutil

SRC_FOLDER = "/raid/ashanbhag3/personal/data/images"
DEST_FOLDER = "/raid/ashanbhag3/personal/data/target_images"


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


def move_files(filename):
    file_paths = splitall(filename)
    l = len(file_paths)

    target_file = os.path.join(DEST_FOLDER, (
        file_paths[l - 3] + "_" + file_paths[l - 2] + "_" + file_paths[l - 1]))
    shutil.copy(filename, target_file)


if __name__ == '__main__':

    for path, subdirs, files in os.walk(SRC_FOLDER):
        for name in files:
            filename = os.path.join(path, name)
            move_files(filename)
