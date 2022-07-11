#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
1、将调用算子得到的属性取出并保存至数据库
2、对每个图片的属性进行验证
"""
from sensoro.tools.get_attribute import *
from sensoro.api.openai_sdk_base import *
from sensoro.tools.read_file import *
from sensoro.tools.db import DB
import os
import json

db = DB()


def attribute_tag():
    baidu = BaiduAi(ReadFile.read_config('$.sdk.DianJun..user')[0],
                    ReadFile.read_config('$.sdk.DianJun..password')[0],
                    ReadFile.read_config('$.sdk.DianJun..url')[0])

    path = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/机动车'
    for i in range(6536, 9937):
        image = os.path.join(path, f"{i}.jpeg")
        print(image)
        if os.path.exists(image):
            try:
                response = baidu.base_detect(
                    ReadFile.read_config('$.url_map.v1..full')[0], image, "filepath", enable_multiple=True)

                if 'data' in response:
                    item = response['data']['items']
                    if len(item) == 1:
                        result = GetAttribute().get_attribute('car', item[0])
                        db.execute_sql(f"""insert into algorithm_precision(file_path, type, attribute) 
                        values ('{image}', {3}, '{json.dumps(result, ensure_ascii=False)}')""")
            except Exception as e:
                raise e


if __name__ == '__main__':
    # 数据存储数据库
    attribute_tag()

    db.close()
