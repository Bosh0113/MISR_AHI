import numpy as np
from cv2 import cv2

cloudmask_dict = {}


def read_cm(date):
    date = str(date)
    try:
        with open('/data01/GEO/AHI_CloudMask/{}/AHIcm.v0.{}.dat'.format(date[:6],date),'rb') as fp:
            cloudmask = np.frombuffer(fp.read(),dtype='<f4').reshape(6000,6000)
    except:
        cloudmask = np.zeros((6000,6000))
    cloudmask = cv2.resize(np.array(cloudmask,dtype='float32'),(12000,12000),interpolation=cv2.INTER_NEAREST)
    cloudmask_dict[date] = cloudmask
    return (date, cloudmask)