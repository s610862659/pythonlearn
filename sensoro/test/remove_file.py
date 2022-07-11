#!/usr/bin/env/python3
# -*- coding=utf-8 -*-
"""
1、人车非关联测试集筛选数据时使用
2、判断是否仅有一辆车 以及 有相关人脸或人体数据
"""
from sensoro.api.openai_sdk_base import *
from sensoro.tools.db import *
from sensoro.tools.read_file import ReadFile
from sensoro.tools import extractor
import os

db = DB()


def remove_file1(path, image_type):

    baidu = BaiduAi(ReadFile.read_config('$.sdk.DianJun..user')[0],
                    ReadFile.read_config('$.sdk.DianJun..password')[0],
                    ReadFile.read_config('$.sdk.DianJun..url')[0])

    image_list = list(os.walk(path))[0][2]
    # print(image_list)
    for image in image_list:
        file = os.path.join(path, image)
        if image != '.DS_Store':
            response = baidu.base_detect(ReadFile.read_config('$.url_map.v1..full')[0], file, 'filepath')
            if 'data' in response:
                obj_type = extractor(response, '$..type')

                num = 0     # 记录机动车/非机动车数量的数量
                if image_type == 'human':
                    face_num = 0
                    for i in obj_type:
                        if i == 'human':
                            num += 1
                        elif i == 'face':
                            face_num += 1
                    if face_num != 1:
                        print(image)
                        os.remove(file)
                else:
                    for i in obj_type:
                        if i == image_type:
                            num += 1
                if num != 1:
                    print(image)
                    os.remove(file)


# 数据库中删除数据
def remove_file2():
    data = db.execute_sql(f"""select id, file_path from algorithm_precision 
    where type=3 and id<24169 and (v2 is null or v1 is null or day='')""")
    print(data)
    for im_id, file_path in data:
        db.execute_sql(f"""update algorithm_precision set delete_time='2022-07-04 16:00:00'""")
        os.remove(file_path)


if __name__ == '__main__':
    # path = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/人车非关联测试集/人体'
    # remove_file1(path, 'human')        # electric-car

    remove_file2()
