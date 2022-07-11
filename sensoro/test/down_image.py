#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
通过研发提供的人车非json文件获取对应url并将图片下载至指定文件夹
"""
from jsonpath import jsonpath
import json
import os
import requests
import time


# 读取json文件,并下载图片
def read_json_and_down_image(file, expr):
    path = os.path.split(file)[0]
    obj = json.load(open(file, 'r'))
    url_list = jsonpath(obj=obj, expr=expr)     # jsonpath方法模糊匹配所有符合条件的字段集内容
    # print(url_list)
    for n in range(len(url_list)):
        # print(1)
        if n >= 0:
            while True:
                try:
                    image = requests.get(url_list[n])
                    if image.status_code == 200:
                        # 多个json文件时使用
                        # image_file = f"{path}/{os.path.split(file)[1].split('.')[0]}-{n}.jpg"

                        image_file = f"{path}/{n}.jpg"
                        open(image_file, 'wb').write(image.content)
                    break
                except Exception as e:
                    # raise e
                    print(e)
                    continue


def get_json_file(path, expr):
    root, dirs, files = list(os.walk(path))[0]
    for file in files:
        if file == '.DS_Store':
            continue
        elif 'json' in file:
            read_json_and_down_image(os.path.join(root, file), expr)

    for folder in dirs:
        get_json_file(os.path.join(root, folder), expr)


if __name__ == '__main__':
    get_json_file('/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/人车非关联测试集/人体', '$..imageUrl')


