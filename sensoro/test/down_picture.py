# coding=utf-8
"""
1、通过json文件中的图片url下载图片
2、有相关属性则记录，无则不记录
3、判断是否需要保存至数据库
"""

import requests
import json
import os
from sensoro.tools.db import DB


# 读取json文件并
# 得到对应图片URL下载图片
# 保存图片及属性、坐标到数据库
def read_json(path, db):

    for folder in ['人脸', '人体', '非机动车', '机动车']:
        n = 0   # 每次循环给下载文件取名用
        files = os.listdir(os.path.join(path, folder))

        if '.DS_Store' in files:
            files.remove('.DS_Store')
        for name in files:
            if '.jpeg' in name:
                continue
            file = os.path.join(os.path.join(path, folder), name)
            # file = '/Users/sunzhaohui/Desktop/SensoroTestData/算法对比测试集/人脸/202107011712_export_json_0513人脸标注测试.json'
            obj_list = json.load(open(file, 'r'))

            for obj in obj_list:
                # 图片URL
                html = obj['imagePath'].replace('http://images.awkvector.com', '')
                picture = requests.get(html)

                # 当图片URL资源存在时取属性
                if picture.status_code == 200:
                    # print(obj)

                    if 'svgArr' in obj['Data']:

                        # 记录整理过的属性及坐标存储数据库中使用
                        data = {'attribute': {}}

                        for att in obj['Data']['svgArr'][0]['secondaryLabel']:
                            # print(att['name'], att['value'])
                            if '(必填,单选)' in att['name']:
                                data['attribute'][att['name'].replace('(必填,单选)', '')] = att['value']
                            elif '(非必填,单选)' in att['name']:
                                data['attribute'][att['name'].replace('(非必填,单选)', '')] = att['value']
                            elif '(必填,多选)' in att['name']:
                                data['attribute'][att['name'].replace('(必填,多选)', '')] = att['value']
                            elif '(非必填,多选)' in att['name']:
                                data['attribute'][att['name'].replace('(非必填,多选)', '')] = att['value']
                            elif '(非必填)' in att['name']:
                                data['attribute'][att['name'].replace('(非必填)', '')] = att['value']
                            elif '(必填)' in att['name']:
                                data['attribute'][att['name'].replace('(必填)', '')] = att['value']
                            else:
                                data['attribute'][att['name']] = att['value']

                        svg = obj['Data']['svgArr'][0]['data']
                        min_x = min(svg[0]['x'], svg[1]['x'], svg[2]['x'], svg[3]['x'])
                        min_y = min(svg[0]['y'], svg[1]['y'], svg[2]['y'], svg[3]['y'])
                        max_x = max(svg[0]['x'], svg[1]['x'], svg[2]['x'], svg[3]['x'])
                        max_y = max(svg[0]['y'], svg[1]['y'], svg[2]['y'], svg[3]['y'])

                        data['location'] = ((int(min_x), int(min_y)), (int(max_x), int(max_y)))
                        # print(data)

                    # 保存图片至本地
                    picture_file = os.path.join(os.path.join(path, folder), f'{folder}{n}.jpeg')
                    open(picture_file, 'wb').write(picture.content)

                    if folder == '人脸':
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {1}, '{json.dumps(data, ensure_ascii=False)}')""")
                    elif folder == '人体':
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {2}, '{json.dumps(data, ensure_ascii=False)}')""")
                    elif folder == '机动车':
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {3}, '{json.dumps(data, ensure_ascii=False)}')""")
                    else:
                        db.execute_sql(f"""
                        insert into algorithm_precision(file_path, type, attribute) 
                        values ('{picture_file}', {4}, '{json.dumps(data, ensure_ascii=False)}')""")
                n += 1


def update_day():   # 更新时间段
    data = db.execute_sql(
        f"""select id, attribute from algorithm_precision""")

    for im_id, att in data:  # 洗数据
        att = json.loads(att)['attribute']
        day = att['时间段']
        db.execute_sql(
            f"""update algorithm_precision set day='{day}' where id={im_id}""")


if __name__ == "__main__":

    db = DB()
    # read_json("/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/", db=db)
    update_day()

    # data = db.execute_sql(f"""select id, attribute from algorithm_precision where type=3""")
    # for id, att in data:
    #     # print(att)
    #     att = json.loads(att)['attribute']
    #     # print(att)
    #     if '车牌号码(非必填)' in att:
    #         att['车牌号码'] = att.pop('车牌号码(非必填)')
    #
    #         db.execute_sql(f"""update algorithm_precision
    #         set attribute='{json.dumps(att, ensure_ascii=False)}' where id={id}""")
    #     if '是否吸烟' in att:
    #         pass
    #         print('是否吸烟', att['是否吸烟'])

    db.close()
