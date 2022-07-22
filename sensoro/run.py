#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

from sensoro.test.precision_contrast import *
from sensoro.test.test_cartoon_or_human import *
from sensoro.test.human_car_related import *
from sensoro.tools.db import DB
from sensoro.tools.read_file import ReadFile
from sensoro.api.openai_sdk_base import BaiduAi

db = DB()


# 人车非属性对比测试
def test_precision_contrast():
    # 将图片相关属性保存至数据库
    WholeTarget(db=db,
                url=ReadFile.read_config('$..full')
                ).whole_target()

    # Contrast(db).run()


# 人车非关联
def test_human_car_related():
    human_car_related()


# 真实人脸、卡通人脸识别准确性测试
def test_cartoon_or_human():
    # 文件存储路径
    path = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/卡通人脸及真实人脸测试集'
    test(url=ReadFile.read_config('$.url_map.v1..full')[0], path=path)


if __name__ == '__main__':

    # 人车非属性对比测试
    # test_precision_contrast()

    # 人车非关联
    test_human_car_related()

    # 真实/卡通人脸准确性测试
    # test_cartoon_or_human()

    db.close()
