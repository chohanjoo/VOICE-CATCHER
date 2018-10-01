from collections import OrderedDict

import cv2
import numpy as np

facial_features_cordinates = {}

# define a dictionary that maps the indexes of the facial
# landmarks to specific face regions
FACIAL_LANDMARKS_INDEXES = OrderedDict([
   ("Mouth", (48, 68)),
])

def shape_to_numpy_array(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coordinates = np.zeros((68, 2), dtype=dtype)

    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coordinates[i] = (shape.part(i).x, shape.part(i).y)

    # return the list of (x, y)-coordinates
    return coordinates


def visualize_facial_landmarks(image, shape, index, lippoint, colors=None, alpha=0.75):
    # create two copies of the input image -- one for the
    # overlay and one for the final output image
    overlay = image.copy()
    output = image.copy()

    # 입술 각 지점의 y값을 저장하기 위한 list 변수
    height = []

    # 입술 각 지점의 x값을 저장하기 위한 list 변수
    weight = []


    # loop over the facial landmark regions individually
    for (i, name) in enumerate(FACIAL_LANDMARKS_INDEXES.keys()):
        # grab the (x, y)-coordinates associated with the
        # face landmark
        (j, k) = FACIAL_LANDMARKS_INDEXES[name]
        pts = shape[j:k]
        for ps in pts:
            height.append(ps[1])
            weight.append(ps[0])

        #입술 정보가 기존에 등록된 정보면 해당 index값으로 가서 값 변경
        if len(lippoint) > index:
            lippoint[index] = pts
        #새로운 입술정보가 입력됬을 때 lippoint에 추가
        else:
            lippoint.append(pts)


    # return the output image
    return output


def bitOperation(frame,hpos, vpos, bubble):
    if type(bubble) != type(None):
        rows, cols, channels = bubble.shape
        roi = frame[vpos:rows + vpos, hpos:cols + hpos]

        img2gray = cv2.cvtColor(bubble, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

        img2_fg = cv2.bitwise_and(bubble, roi, mask=mask)

        dst = cv2.add(img1_bg, img2_fg)
        frame[vpos:rows + vpos, hpos:cols + hpos] = dst

def bitOperation2(frame,hpos, vpos, bubble):
    if type(bubble) != type(None):
        rows, cols, channels = bubble.shape
        roi = frame[vpos:rows + vpos, hpos:cols + hpos]

        img2gray = cv2.cvtColor(bubble, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        img2_fg = cv2.bitwise_and(bubble, bubble, mask=mask)

        dst = cv2.add(img1_bg, img2_fg)
        frame[vpos:rows + vpos, hpos:cols + hpos] = dst
