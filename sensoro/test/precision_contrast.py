# coding=utf-8
"""
1、算法对比测试使用
2、调用不同算法取对应数据
3、对数据进行对比
"""

from sensoro.tools.draw_rectangle import draw_rectangle
from sensoro.tools.recording import *
from sensoro.tools.get_attribute import *
from sensoro.tools.openai_baidu import *
import time
import json
import os


# 1、根据图片类型，获取对应属性，并调用不同对象方法，将属性与标记字段映射存储到数据库
class WholeTarget:
    def __init__(self, db, url: list):
        self.db = db
        # self.baidu = baidu
        self.url = url
        # self.result = {}    # 记录属性及坐标内容，保存至数据库
        self.version = ''   # 记录版本，数据存入数据库时使用

    def whole_target(self):
        data = self.db.execute_sql(f"""
        select id,attribute, file_path,type from algorithm_precision where delete_time is null and type=1""")
        # print(data)
        for im_id, attribute, image, im_type in data:
            if not os.path.exists(image):
                self.db.execute_sql(f"""update algorithm_precision 
                set delete_time='{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}' where id={im_id}""")
                continue

            for num in range(len(self.url)):

                try:
                    response = get_baidu(self.url[num], image, 'filepath')

                    print(json.dumps(response))
                    a = input('11')
                    if 'data' in response:
                        # print(response)
                        item = self.calc_overlap_rate(response['data']['items'], attribute, im_type)
                        if not item:
                            continue

                        # self.result['location'] = item['location']

                        if 'v1' in self.url[num]:
                            self.version = 'v1'
                        elif 'v2' in self.url[num]:
                            self.version = 'v2'
                        # print(item)
                        if im_type == 1:
                            result = GetAttribute().get_attribute('face', item)
                            # self.face(item, im_id)
                        elif im_type == 2:
                            result = GetAttribute().get_attribute('human', item)
                        elif im_type == 3:
                            result = GetAttribute().get_attribute('car', item)
                        else:
                            result = GetAttribute().get_attribute('ele-car', item)
                        self.db.execute_sql(
                            f"""update algorithm_precision 
                            set {self.version}='{json.dumps(result, ensure_ascii=False)}' where id={im_id}""")
                except Exception as e:
                    raise e
                    # print('返回无数据或服务异常', e)
                    # continue
            im_data = self.db.execute_sql(f"""select v1, v2 from algorithm_precision where id={im_id}""")
            for v1, v2 in im_data:
                if not v1 or not v2:
                    self.db.execute_sql(f"""update algorithm_precision 
                    set delete_time='{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}' where id={im_id}""")
                    os.remove(image)

    # 计算与标记坐标重叠率，取重叠最大的
    @staticmethod
    def calc_overlap_rate(items, att, im_type):
        data = []   # 记录对象信息
        for item in items:
            if im_type == 1:
                if item['type'] == 'face':
                    data.append(item)
            elif im_type == 2:
                if item['type'] == 'human':
                    data.append(item)
            elif im_type == 3:
                if item['type'] == 'car':
                    data.append(item)
            else:
                if item['type'] == 'electric-car':
                    data.append(item)

        if len(data) > 1:
            att = json.loads(att)
            location = att['location']
            cross_area = {}
            for table in range(len(data)):
                min_x = min(int(location[0][0]), data[table]['location']['left'])
                min_y = min(int(location[0][1]), data[table]['location']['top'])
                max_x = max(int(location[1][0]), data[table]['location']['left']+data[table]['location']['width'])
                max_y = max(int(location[1][1]), data[table]['location']['top']+data[table]['location']['height'])

                cross_x = location[1][0]-location[0][0] + data[table]['location']['width'] - (max_x-min_x)
                cross_y = location[1][1]-location[0][1] + data[table]['location']['height'] - (max_y-min_y)

                if cross_y < 0 or cross_y < 0:
                    continue
                else:
                    cross_area[table] = cross_x * cross_y
            max_key = 0
            max_value = 0
            for key, value in cross_area.items():
                if value > max_value:
                    max_value = value
                    max_key = key
            # print(max_key, data)
            return data[max_key]

        else:
            return None


# 2、对比数据
class Contrast:

    def __init__(self, db):
        self.db = db
        self.wb = Recording(f'{os.getcwd()}/data/contrast_data.xlsx')

        # 记录异常的数据id
        self.false_id = {'face': [], 'human': [], 'car': [], 'ele-car': []}

    # 对比属性内容，并将结果数据写入指定参数self.data，并将数据写入Excel中
    def _contrast(self, version, is_draw=0):  # is_draw判断是否标记图片，1标记，0不标记
        data = self.db.execute_sql(
            f"""select id, file_path, attribute, {version}, type, day 
            from algorithm_precision 
            WHERE delete_time is null and v1 is not null and v2 is not null and id < 19712""")

        for im_id, image, att, result, im_type, day in data:
            att = json.loads(att)['attribute']
            result = json.loads(result)

            for key, value in att.items():

                if is_draw == 1:
                    self._draw_picture(image, result['location'], version)

                if key in ('时间段', 'location'):
                    continue

                # if value == '':
                #     value = '未知'
                # if not value:
                #     value.append('未知')
                if value in ('', '未知', False):
                    continue
                if im_type == 1:
                    col_value = self.wb.read_excel_for_column('人脸比对数据分析', 'B')

                    if key == '帽子':
                        continue
                    elif value == result[key]:
                        self._save_excel('人脸比对数据分析', version, col_value, day, value, True)
                    else:
                        self._save_excel('人脸比对数据分析', version, col_value, day, value, False)
                        self.false_id['face'].append(f"{key}{im_id}")
                elif im_type == 2:
                    col_value = self.wb.read_excel_for_column('人体比对数据分析', 'B')
                    if key == '随身物品':
                        for item in value:
                            if item in result[key]:
                                self._save_excel('人体比对数据分析', version, col_value, day, item, True)

                            else:
                                self._save_excel('人体比对数据分析', version, col_value, day, item, False)
                                self.false_id['human'].append(f"{key}{im_id}")

                    elif key == '行为':
                        if value in ('看手机', '未使用手机', '打手机'):
                            if result['是否用手机'] == value:
                                self._save_excel('人体比对数据分析', version, col_value, day, value, True)
                            else:
                                self._save_excel('人体比对数据分析', version, col_value, day, value, False)
                                self.false_id['human'].append(f"{'是否用手机'}{im_id}")

                        elif value in ('未吸烟', '吸烟'):
                            if value == result['是否吸烟']:
                                self._save_excel('人体比对数据分析', version, col_value, day, value, True)
                            else:
                                self._save_excel('人体比对数据分析', version, col_value, day, value, False)
                                self.false_id['human'].append(f"{'是否吸烟'}{im_id}")

                    elif value == result[key]:
                        self._save_excel('人体比对数据分析', version, col_value, day, value, True)

                    else:
                        self._save_excel('人体比对数据分析', version, col_value, day, value, False)
                        self.false_id['human'].append(f"{key}{im_id}")
                elif im_type == 3:

                    col_value = self.wb.read_excel_for_column('机动车比对数据分析', 'B')
                    if key in ('机动车类型', '副驾驶员是否打电话'):
                        continue
                    elif key == '车牌状态':
                        for item in value:
                            if item in result[key]:
                                self._save_excel('机动车比对数据分析', version, col_value, day, item, True)
                            else:
                                self._save_excel('机动车比对数据分析', version, col_value, day, item, False)
                                self.false_id['car'].append(f"{'车牌状态'}{im_id}")
                    elif key == '车牌号码':
                        if value == result[key]:
                            self._save_excel('机动车比对数据分析', version, col_value, day, '车牌号码', True)
                        else:
                            self._save_excel('机动车比对数据分析', version, col_value, day, '车牌号码', False)
                            self.false_id['car'].append(f"{'车牌号码'}{im_id}")
                    elif value == result[key]:
                        self._save_excel('机动车比对数据分析', version, col_value, day, value, True)
                    else:
                        self._save_excel('机动车比对数据分析', version, col_value, day, value, False)
                        self.false_id['car'].append(f"{key}{im_id}")
                elif im_type == 4:
                    col_value = self.wb.read_excel_for_column('非机动车比对数据分析', 'B')
                    if key in ('性别', '年龄段', '上身纹理'):
                        continue
                    elif key == '头部特征':
                        for item in value:
                            if item in result[key]:
                                self._save_excel('非机动车比对数据分析', version, col_value, day, item, True)
                            else:
                                self._save_excel('非机动车比对数据分析', version, col_value, day, item, False)
                                self.false_id['ele-car'].append(f"{key}{im_id}")

                    elif value == result[key]:
                        self._save_excel('非机动车比对数据分析', version, col_value, day, value, True)
                    else:
                        self._save_excel('非机动车比对数据分析', version, col_value, day, value, False)
                        self.false_id['ele-car'].append(f"{key}{im_id}")

        self.wb.save(f"{os.getcwd()}/data/{'contrast_data.xlsx'}")

    # 数据存储excel
    def _save_excel(self, sheet_name, version, col_value, day, value, status):
        """

        :param sheet_name: excel中sheet名称
        :param version: 接口类型，如：百度v1 、 v2
        :param col_value: excel中属性描述list
        :param day: 白天 or 夜间
        :param value: 标记的属性值
        :param status: 属性值是否与标记属性值相等，True、False
        :return:
        """

        for i in range(len(col_value)):
            if col_value[i] == value:
                if day == '白天':
                    if version == 'v1':
                        if status:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 11)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 11, v + 1)
                        else:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 12)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 12, v + 1)
                    elif version == 'v2':
                        if status:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 13)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 13, v + 1)
                        else:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 14)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 14, v + 1)
                elif day == '夜间':
                    if version == 'v1':
                        if status:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 15)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 15, v + 1)
                        else:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 16)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 16, v + 1)
                    elif version == 'v2':
                        if status:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 17)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 17, v + 1)
                        else:
                            v = self.wb.read_excel_cell(sheet_name, i + 1, 18)
                            if not v:
                                v = 0
                            self.wb.write_excel(sheet_name, i + 1, 18, v + 1)

    @staticmethod
    def _draw_picture(image, location, version):
        location = ((location['left'], location['top']),
                    (location['left']+location['width'], location['top']+location['height']))
        draw_rectangle(image, location, version)

    # 执行方法，分别调用contrast处理多个算法属性结果判断
    def run(self):
        self._contrast('v1', is_draw=0)
        self._contrast('v2', is_draw=0)


# 打印结果
def print_result(v1_true, v1_false, v2_true, v2_false):
    # print(v1[0], v2[0], v1[1], v2[1])
    print('v1 face true')
    for k, v in v1_true['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 face false')
    for k, v in v1_false['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 face true')
    for k, v in v2_true['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 face false')
    for k, v in v2_false['face'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 human true')
    for k, v in v1_true['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 human false')
    for k, v in v1_false['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 human true')
    for k, v in v2_true['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 human false')
    for k, v in v2_false['human'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 car true')
    for k, v in v1_true['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 car false')
    for k, v in v1_false['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 car true')
    for k, v in v2_true['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 car false')
    for k, v in v2_false['car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 ele true')
    for k, v in v1_true['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v1 ele false')
    for k, v in v1_false['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 ele true')
    for k, v in v2_true['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()

    print('v2 ele false')
    print(v2_false)
    for k, v in v2_false['ele-car'].items():
        print(k)
        for k1, v1 in v.items():
            print(k1, v1)
        print()


# 取v1正确，v2异常的数据
def v_false(v1_false_id, v2_false_id):
    # print(v1_false_id)
    for i in v2_false_id['human']:

        if '年龄段' in i and (i not in v1_false_id['human']):
            print(i)


if __name__ == '__main__':
    pass
    # db = DB()
    # 调用接口并整理对应属性
    # WholeTarget('/v1/whole/target/detect', version='v1').whole_target()
    # WholeTarget('/v2/whole/target/detect', version='v2').whole_target()

    # v1_true, v1_false, v1_false_id = Contrast().contrast(version='v1', is_draw=1)
    # v2_true, v2_false, v2_false_id = Contrast().contrast(version='v2', is_draw=1)

    # print_result(v1_true, v1_false, v2_true, v2_false)

    # 取v1正确，v2错误的数据
    # v_false(v1_false_id, v2_false_id)

    # data = db.execute_sql(f"""
    #     select id, file_path from algorithm_precision
    #     where (v1 is null or v2 is null) and delete_time is null and type=1""")
    #
    # for im_id, file in data:
    #     # print(file)
    #     print(os.path.split(file)[1])1

    # db.close()
