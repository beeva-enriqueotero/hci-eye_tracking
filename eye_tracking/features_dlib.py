# -*- coding: utf-8 -*-
"""
Extract face features with dlib.

pip package: dlib
deb packages: libboost-python-dev, cmake
Based in: http://dlib.net/face_landmark_detection.py.html

Facial shape predictor: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
"""

import csv
import os
import dlib
from skimage import io


class Features01(object):
    def __init__(self, predictor_path ):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)


    def extract_features(self, img):
        retval = None
        faces = self.detector(img, 1)
        if faces:
            biggest_face = max(faces,key=lambda x:x.area())
            landmarks = self.predictor(img, biggest_face)
            if landmarks:
                retval = {
                    'face.x': biggest_face.left(),
                    'face.y': biggest_face.top(),
                    'face.width': biggest_face.width(),
                    'face.height': biggest_face.height(),
                }
                for i,point in enumerate(landmarks.parts()):
                    retval['{}.x'.format(i)] = point.x
                    retval['{}.y'.format(i)] = point.y
            else:
                retval = -2
        else:
            retval = -1
        return retval



if __name__=="__main__":
    import config
    from utils import Data

    # Create destination path
    if os.path.exists(config.PATH_DATA_DLIB):
        print("Folder {} exists, no need to generate dataset.".format(config.PATH_DATA_DLIB))
        exit()
    os.makedirs(config.PATH_DATA_DLIB)
    features = Features01(config.PATH_DLIB_MODEL)
    data = Data(config.PATH_DATA_RAW)
    i = 0
    with open(config.PATH_DATA_DLIB_CSV,'wb') as fd:
        for datum in data.iterate():
            img_path = datum['img_path']
            img = io.imread(img_path)
            f = features.extract_features(img)
            if f == -1:  # No face
                print "[WARNING] '{}' FACE NOT FOUND".format(img_path)
            elif f == -2:  # No landmarks
                print "[WARNING] '{}' LANDMARKS NOT FOUND".format(img_path)
            else:  # Everything correct
                f['img'] = '/'.join(img_path.split('/')[-2:])
                if i==0:
                    csv_writer = csv.DictWriter(fd, fieldnames=f.keys())
                    csv_writer.writeheader()
                if f:
                    csv_writer.writerow(f)
                i+=1
                print i
