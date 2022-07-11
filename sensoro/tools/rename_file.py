#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
import os
import json
import jieba

path = "/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/机动车"

file_list = list(os.walk(path))[0][2]
# print(file_list)
num = 0
for i in range(1, 5708):
    # num = i
    if f'{i}.jpg' in file_list:
        # while True:
        #     if f'{num}.jpg' in file_list:
        #         num += 1
        #         continue
        #     else:
        #         os.rename(os.path.join(path, f'{i}.jpg'), os.path.join(path, f"{num+4229}.jpeg"))
        #         break
        os.rename(os.path.join(path, f'{i}.jpg'), os.path.join(path, f"{i + 4229}.jpeg"))
