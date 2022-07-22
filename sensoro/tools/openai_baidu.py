#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
from sensoro.api.openai_sdk_base import *
from sensoro.tools.read_file import ReadFile
import os


def get_baidu(url: str, image: str, image_type: str):
    baidu = BaiduAi(ReadFile.read_config('$.sdk.DianJun..user')[0],
                    ReadFile.read_config('$.sdk.DianJun..password')[0],
                    ReadFile.read_config('$.sdk.DianJun..url')[0])

    try:
        # enable_multiple:指定大图模式，全目标检测输出所有目标，默认false，即小图模式
        result = baidu.base_detect(url, image, image_type, enable_multiple=True)

        return result
    except Exception as e:
        raise e


if __name__ == '__main__':
    path = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/人脸聚类测试集'

    dirs = list(os.walk(path))[0][1]
    face_error = {}
    face_mach = {}
    for folder in dirs:
        face_error[folder] = []
        face_mach[folder] = []
        files = os.listdir(os.path.join(path, folder))
        if '.DS_Store' in files:
            files.remove('.DS_Store')

        for file in files:
            r = get_baidu(ReadFile.read_config('$.url_map.v2..full')[0],
                          os.path.join(os.path.join(path, folder), file),
                          'filepath')
            # print(response)
            if 'data' in r:
                items = r['data']['items']
                face = 0
                for i in items:
                    if i['type'] == 'face':
                        face += 1
                if face == 1:
                    print(file, '通过')
                elif face > 1:
                    print(file, '检测出多张人脸')
                elif face == 0:
                    face_error[folder].append(file)
                    print(file, '未检测到人脸')
            else:
                face_error[folder].append(file)
                print(file, '无法检测出人脸')
        if not face_error[folder]:
            face_error.pop(folder)
    print(face_error)
