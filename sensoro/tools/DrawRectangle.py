"""
标记图片
"""

import cv2
import os


def draw_rectangle(image, point, name=''):
    img = cv2.imread(image)

    if isinstance(point, dict):
        for key, value in point.items():

            if key[0] == 'b':
                color = (255, 255, 0)

            elif key[0] == 'h':
                color = (0, 255, 0)

            elif key[0] == 'f':
                color = (0, 0, 255)

            elif key[0] == 'c':
                color = (255, 0, 0)

            elif key[0] == 'e':
                color = (0, 255, 255)

            cv2.rectangle(img, value[0], value[1], color, 2, 4)
            cv2.putText(img, key, (value[0][0], value[0][1] + 30), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    else:
        cv2.rectangle(img, point[0], point[1], (0, 255, 255), 2, 4)

    new_img_file_path = os.path.split(image)[0] + f"/结果/"
    if not os.path.exists(new_img_file_path):
        os.makedirs(new_img_file_path)

    cv2.imwrite(f"{new_img_file_path}{name}{os.path.split(image)[1]}", img)
