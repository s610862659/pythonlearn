#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

from sensoro.test.precision_contrast import *
from sensoro.test.test_cartoon_or_human import *
from sensoro.tools.db import DB
from sensoro.tools.read_file import ReadFile
from sensoro.api.openai_sdk_base import BaiduAi

db = DB()

# 定义sdk环境
# 平台-百度点军环境
baidu = BaiduAi(ReadFile.read_config('$.sdk.DianJun..user')[0],
                ReadFile.read_config('$.sdk.DianJun..password')[0],
                ReadFile.read_config('$.sdk.DianJun..url')[0])


# 人车非属性对比测试
def test_precision_contrast():
    # 将图片相关属性保存至数据库
    WholeTarget(db=db,
                baidu=baidu,
                url=ReadFile.read_config('$..full')
                ).whole_target()

    # Contrast(db).run()


# 真实人脸、卡通人脸识别准确性测试
def test_cartoon_or_human():
    # 文件存储路径
    path = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/卡通人脸及真实人脸测试集'
    test(baidu=baidu, url=ReadFile.read_config('$.url_map.v1..full')[0], path=path)


if __name__ == '__main__':

    # 人车非属性对比测试
    test_precision_contrast()

    # 真实/卡通人脸准确性测试
    # test_cartoon_or_human()

    db.close()
