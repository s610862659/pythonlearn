# coding=utf-8
"""
1、通过json文件中的图片url下载图片，并记录相关属性内容
2、算法对比测试使用数据
"""

import requests
import json
import jsonpath
import os
from openpyxl import load_workbook
from DB import *


# 读取json文件并
# 得到对应图片URL下载图片
# 保存图片及属性、坐标到数据库
def read_json(path, db):

    for folder in ['人脸', '人体', '机动车', '非机动车']:
        n = 0   # 每次循环给下载文件取名用
        files = os.listdir(os.path.join(path, folder))
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        for name in files:
            file = os.path.join(os.path.join(path, folder), name)
            obj_list = json.load(open(file, 'r'))

            for obj in obj_list:
                # 图片URL
                html = obj['imagePath'].replace('http://images.awkvector.com', '')
                picture = requests.get(html)

                # 当图片URL资源存在时取属性
                if picture.status_code == 200:
                    if 'svgArr' in obj['Data']:

                        att_obj = obj['Data']['svgArr'][0]['secondaryLabel']

                        # 记录整理过的属性存储数据库中使用
                        attribute = {}

                        for att in att_obj:
                            # print(att['name'], att['value'])
                            if '(必填,单选)' in att['name']:
                                attribute[att['name'].replace('(必填,单选)', '')] = att['value']
                            elif '(非必填,单选)' in att['name']:
                                attribute[att['name'].replace('(非必填,单选)', '')] = att['value']
                            elif '(必填,多选)' in att['name']:
                                attribute[att['name'].replace('(必填,多选)', '')] = att['value']
                            elif '(非必填,多选)' in att['name']:
                                attribute[att['name'].replace('(非必填,多选)', '')] = att['value']
                            else:
                                attribute[att['name']] = att['value']
                        # print(attribute)

                    # 保存图片至本地
                    picture_file = os.path.join(os.path.join(path, folder), f'{folder}{n}.jpeg')
                    open(picture_file, 'wb').write(picture.content)

                    if folder == '人脸':
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {1}, '{json.dumps(attribute, ensure_ascii=False)}')""")
                    elif folder == '人体':
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {2}, '{json.dumps(attribute, ensure_ascii=False)}')""")
                    elif folder == '机动车':
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {3}, '{json.dumps(attribute, ensure_ascii=False)}')""")
                    else:
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {4}, '{json.dumps(attribute, ensure_ascii=False)}')""")
                n += 1


if __name__ == "__main__":

    db = DB()
    read_json("/Users/sunzhaohui/Desktop/SensoroTestData/算法对比测试集", db=db)
    db.close()
