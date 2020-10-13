from ctypes import *
import math
import numpy as np
import random
from PIL import Image 
Image.Image.tostring = Image.Image.tobytes

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    

# lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0)
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    return res


def save_predict(img,r):
    # #get detected image
    _, ax = plt.subplots(1)
    image = mpimg.imread(img)
    ax.imshow(image)
    for k in range(len(r)):
        width = r[k][2][2]
        height = r[k][2][3]
        center_x = r[k][2][0]
        center_y = r[k][2][1]
        bottomLeft_x = center_x - width/2
        bottomLeft_y = center_y - height/2

        rect = patches.Rectangle((bottomLeft_x, bottomLeft_y), width,
                                 height, linewidth=1, edgecolor='r', facecolor='none')

        ax.add_patch(rect)

    imagepath = './static/' + img.replace('/','_')
    plt.show(block=False)
    plt.savefig(imagepath)
    plt.close('all') 



if __name__ == "__main__":
    img = "1cx5auhwra3t1k3jnks1t.png"
    # img = "3b2vkjv0y7cmlkwiytsl4.png"
    # img = '3cvt27ag74mpjje68jo9l.png'
    # img = "3euc2ifmwwppp6pjj8ymkr.png"

    net = load_net("./cfg/tiny-yolo-obj.cfg", 
        "./weights/tiny-yolo-obj_900.weights", 0)
    meta = load_meta("./cfg/detector.data")
    r = detect(net, meta, img)
    print(r)


    # #get detected image
    fig,ax = plt.subplots(1)
    image = mpimg.imread(img)
    ax.imshow(image)
    for k in range(len(r)):
        width =  r[k][2][2]
        height = r[k][2][3]
        center_x = r[k][2][0]
        center_y = r[k][2][1]
        bottomLeft_x = center_x - width/2
        bottomLeft_y = center_y - height/2
        print(bottomLeft_x)
        print(bottomLeft_y)
        rect = patches.Rectangle((bottomLeft_x, bottomLeft_y), width, height, linewidth=1, edgecolor='r',facecolor='none')

        ax.add_patch(rect)

    imagepath = './static/' + img
    # plt.show()
    plt.savefig(imagepath)
        

