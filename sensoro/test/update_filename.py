#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
1、针对人脸聚类测试集，将文件夹及内文件按personId命名，如：P1:P1_1、P1_2
"""
import os

path = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/人脸聚类测试集'
dirs = list(os.walk(path))[0][1]

for name in dirs:
    num = 1
    files = os.listdir(os.path.join(path, name))
    # print(files)
    if '.DS_Store' in files:
        files.remove('.DS_Store')
    for file in files:
        os.rename(os.path.join(os.path.join(path, name), file), os.path.join(os.path.join(path, name), f'{name}_{num}.jpg'))
        num += 1

