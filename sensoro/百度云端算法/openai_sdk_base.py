# coding: utf-8
"""
适用范围：
    1、百度云端算法
测试内容：
    1、对象检测数量
    2、对象关联方式
使用环境：
    1、点军环境，因测试环境接口调用需要收费，点军环境百度部署了一套，调用不收费
"""
import time
import datetime
import os
import json
import hmac
import hashlib
import yaml
from openpyxl import Workbook, load_workbook
from hashlib import sha256

import requests
from PIL import Image

import pymysql
from typing import Union

import base64
import cv2

# 读取配置文件
with open(f"{os.getcwd()}/config.yml", "r", encoding="utf-8") as y:
    config = yaml.load(y.read(), Loader=yaml.FullLoader)

file = []   # 记录所有符合规则的图片,全目标使用


# 获取api auth
class BaiAuth(object):
    def __init__(self, user=None, password=None, minute_delta=5 * 60 * 1000):
        self.user = user
        self.password = password

        now = time.time()
        expire = int(round(now * 1000)) + minute_delta * 60 * 1000
        self.expire_time = str(expire)
        self.headers = {}

    @staticmethod
    def to_md5(_str):
        md5 = hashlib.md5()
        md5.update(_str.encode("utf-8"))
        return md5.hexdigest()

    @staticmethod
    def to_json(json_object):
        return json.dumps(json_object, separators=(",", ":"), default=str)

    def generate_auth_headers(self, uri, body):
        """ generate auth params
        :param uri:
        :param body:
        :return:
        """

        node_body_str = self.to_json(body)
        node_body = self.to_md5(node_body_str)

        self.headers = {
            "x-evs-user": self.user,
            "x-evs-expire-date": str(self.expire_time),
            "x-evs-content-md5": node_body,
            "Authorization": None,
            "content-type": "application/json;charset=UTF-8",
            # "From-Env": CntEnvConstant.ANTMAN_BRANCH,
            # "X-TRACE-ID": REQUEST_ID_CONTEXT.get(),
        }
        content = f"{self.user}:{self.password}:{uri}:{self.expire_time}:{node_body}"
        self.headers["Authorization"] = hmac.new(
            key=self.password.encode("utf-8"),
            msg=content.encode("utf-8"),
            digestmod=sha256
        ).hexdigest()
        return self.headers


class BaiduAi:
    def __init__(self, user_id, user_sk, server_addr):

        self.user_id = user_id
        self.user_sk = user_sk
        self.server_addr = server_addr

    # 获取接口auth
    def get_or_create_request_headers(self, url_path, body, minute_delta=5 * 60):
        return BaiAuth(
            user=self.user_id, password=self.user_sk, minute_delta=minute_delta
        ).generate_auth_headers(uri=url_path, body=body)

    # 接口调用
    def _base_request(self, url_path: str, **kwargs):
        """

        :param url_path: 百度api地址
        :return:
        """
        api = self.server_addr + url_path

        headers = self.get_or_create_request_headers(url_path, kwargs)

        # a = datetime.datetime.now()
        r = requests.post(api, json=kwargs, headers=headers)
        # b = datetime.datetime.now()
        # print((b-a).seconds)
        rep = r.json()

        return rep

    # 判断使用文件方式
    def base_detect(self, url_path: str, image: str, image_type, **kwargs):
        """

        :param url_path: 百度api地址
        :param image: 待检测待图片，可以是url，文件系统路径、base64编码后的字符串3中类型
        :param image_type: 图片参数的类型，["filepath", "url", "base64str"]
        :return:
        """
        if image_type == "base64str":
            # 适用于api处理前端页面上传图片b64
            # 需要调用者保证图片格式是jpg
            params = {"image_base64": image}
        elif image_type == "filepath":
            # 适用于处理本地文件系统中的图片
            # png --> jpg
            with open(image, 'rb') as image_file:
                params = {"image_base64": base64.b64encode(image_file.read()).decode()}

        elif image_type == "url":
            params = {"image_url": image}

        params.update(kwargs)
        return self._base_request(url_path=url_path, **params)


class DB:
    mysql = config['database']

    def __init__(self):
        """
        初始化数据库连接，并指定查询结果以字典形式返回
        """
        self.connection = pymysql.connect(
            host=self.mysql['host'],
            port=self.mysql['port'],
            user=self.mysql['user'],
            password=self.mysql['password'],
            db=self.mysql['db_name'],
            charset=self.mysql['charset'],
        )

    def execute_sql(self, sql: str) -> Union[dict, None]:
        """
        执行sql语句方法，查询所有结果的sql只会返回一条结果支持select， delete， insert， update
        :param sql: sql语句
        :return: select语句，如果有结果则返回 对应结果字典，delete，insert，update 将返回None
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            # 使用commit解决查询数据概率查错问题
            self.connection.commit()
            return self.verify(result)

    @staticmethod
    def verify(result: dict) -> Union[dict, None]:
        """验证结果能否被json.dumps序列化问题"""
        # 尝试变成字符串，解决datetime无法被json序列化问题
        try:
            json.dumps(result)
        except TypeError:   # TypeError: Object of type datetime is not JSON serializable
            for k, v in result.items():
                if isinstance(v, datetime):
                    result[k] = str[v]
        return result

    def close(self):
        # 关闭数据库连接
        self.connection.close()


# 全目标
class FullTarget:

    def __init__(self, db):
        self.db = db
        self.point = {}     # 记录坐标
        self.item_count = {'human': 0, 'face': 0, 'car': 0, 'electric-car': 0}

    # 数据处理
    def judge_item(self, is_item_count=False, is_relation_map=False):

        for id, image, response in \
                self.db.execute_sql(f'''select id, image, baidu_response 
                            from algorithm where alg_type="full" and is_pass="pass"'''):

            response = json.loads(response)
            print(os.path.split(image)[1])

            for item in response['data']['items']:
                if item['type'] == 'human':

                    if item["score"] < 0.6:     # 当对象置信度小于0.6时，直接抛弃该数据
                        continue

                    self.item_count['human'] += 1
                    self.point['h' + str(item['id'])] = Util.get_point(item)

                    print('h' + str(item['id']) + f'置信度 {item["score"]}')

                    # 显示人体相关属性
                    self.human_attribute(item["attribute"])

                elif item['type'] == 'face':

                    if item["score"] < 0.6:     # 当对象置信度小于0.6时，直接抛弃该数据
                        continue

                    self.item_count['face'] += 1
                    self.point['f' + str(item['id'])] = Util.get_point(item)
                    print('f' + str(item['id']) + f'置信度 {item["score"]}')

                elif item['type'] == 'car':

                    self.item_count['car'] += 1
                    self.point['c' + str(item['id'])] = Util.get_point(item)
                    print('c' + str(item['id']) + f'置信度 {item["score"]}')

                elif item['type'] == 'electric-car':

                    self.item_count['electric-car'] += 1
                    self.point['e' + str(item['id'])] = Util.get_point(item)
                    print('e' + str(item['id']) + f'置信度 {item["score"]}')

            new_image = Util.draw_rectangle_and_insert_db(image, self.point)  # 对图像标记并将新文件位置保存至数据库
            self.db.execute_sql(f'''update algorithm set new_image="{new_image}" where id="{id}"''')

            if is_item_count:
                print(f"对象数量：\n\t人体:{self.item_count['human']},人脸:{self.item_count['face']},"
                      f"机动车:{self.item_count['car']},非机动车{self.item_count['electric-car']}")

            if is_relation_map:
                self.get_relation_map(response['data']['relation_map'])

    # 人体属性
    @staticmethod
    def human_attribute(attribute):
        print(f"人体行为识别相关结果如下：\n"
              f"动作状态：{attribute['action']['name']}\n"
              f"帽子状态：{attribute['headwear']['name']}\n"
              f"眼镜状态：{attribute['glasses']['name']}\n"
              f"口罩状态：{attribute['face_mask']['name']}\n"
              f"吸烟状态：{attribute['smoke']['name']}\n"
              f"手机状态：{attribute['cellphone']['name']}\n"
              f"是否戴手套：{attribute['glove']['name']}\n")

    # 对象关联关系处理
    @staticmethod
    def get_relation_map(relation_map):
        print('对象关联关系：')
        if not relation_map:
            print('对象无关联关系')
        else:
            for relation in relation_map:
                if relation['car_id'] != -1 and relation['human_id'] != -1 and relation['face_id'] != -1:
                    print(f"\t车辆{relation['car_id']} 人体{relation['human_id']} 人脸{relation['face_id']}")

                elif relation['car_id'] != -1 and relation['human_id'] != -1 and relation['face_id'] == -1:
                    print(f"\t车辆{relation['car_id']} 人体{relation['human_id']}")

                elif relation['car_id'] == -1 and relation['human_id'] != -1 and relation['face_id'] != -1:
                    print(f"\t人体{relation['human_id']} 人脸{relation['face_id']}")

                elif relation['car_id'] != -1 and relation['human_id'] == -1 and relation['face_id'] != -1:
                    print(f"\t车辆{relation['car_id']} 人脸{relation['face_id']}")

    # 对象属性，人体、人脸、机动车、非机动车
    @staticmethod
    def get_attribute(item_type, attribute):
        if item_type[0] == 'h':
            attribute
        elif item_type[0] == 'f':
            attribute
        elif item_type[0] == 'c':
            attribute
        else:
            attribute


# 船只识别
class ShipTarget:

    def __init__(self, item, row, sheet):
        self.item = item
        self.point = {}
        self.row = row
        self.sheet = sheet

    def judge_item(self, image):

        path = os.path.split(image)[0]
        name = os.path.split(image)[1]

        print(name)
        size = []
        ship_type = []
        for num in range(len(self.item)):
            self.point['b'+str(num)] = Util.get_point(self.item[num])  # 获取船只坐标位置

            print('b'+str(num) + f',{self.item[num]["name"]}，置信度 {self.item[num]["score"]}')    # 需要置信度时放开

            # 船只类型
            ship_type.append(self.item[num]["name"])
            # 船只大小
            size.append(f"{self.item[num]['location']['width']}*{self.item[num]['location']['height']}")
            # print("船只大小：", f"{self.item[num]['location']['width']}*{self.item[num]['location']['height']}")

        self.ship_in_excel(ship_type, size)

        Util.draw_rectangle_by_point(path, name, self.point)    # 对图像标记并保存

    # 船只类型及大小存入Excel
    def ship_in_excel(self, type, size):

        ship_type = ''
        ship_size = ''
        if self.sheet.cell(self.row, 2).value:
            pass
        else:
            for i in type:
                if ship_type == '':
                    ship_type = i
                else:
                    ship_type += f",{i}"
            self.sheet.cell(self.row, 2).value = ship_type

        if self.sheet.cell(self.row, 4).value:
            pass
        else:
            for i in size:
                if ship_size == '':
                    ship_size = i
                else:
                    ship_size += f",{i}"
            self.sheet.cell(self.row, 4).value = ship_size


# 非法捕鱼
class FishTarget:

    def __init__(self, item):
        self.item = item
        self.point = {}

    def judge_item(self, image):
        path = os.path.split(image)[0]
        name = os.path.split(image)[1]

        print(name)
        for num in range(len(self.item)):
            self.point['f' + str(num)] = Util.get_point(self.item[num])  # 获取船只坐标位置

            print('f' + str(num) + f',{self.item[num]["name"]}，置信度 {self.item[num]["score"]}')  # 需要置信度时放开

        Util.draw_rectangle_by_point(path, name, self.point)  # 对图像标记并保存


# 垃圾桶 - db
class TrashTarget:

    def __init__(self, db):
        self.db = db
        self.point = {}

    def judge_item(self):

        for id, image, response in \
                self.db.execute_sql(f'''select id, image, baidu_response 
                            from algorithm where alg_type="trash" and is_pass="pass"'''):

            response = json.loads(response)
            print(os.path.split(image)[1])
            for num in range(len(response['data']['items'])):

                self.point['t' + str(num)] = Util.get_point(response['data']['items'][num])
                print(f"垃圾桶 t{num} 状态为 {response['data']['items'][num]['desc']}")

            new_image = Util.draw_rectangle_and_insert_db(image, self.point)  # 对图像标记并将新文件位置保存至数据库
            self.db.execute_sql(f'''update algorithm set new_image="{new_image}" where id="{id}"''')


# 一些公共方法
class Util(object):

    @staticmethod
    def draw_rectangle_and_insert_db(image, point):
        img = cv2.imread(image)

        for key, value in point.items():

            if key[0] == 'b':
                color = (0, 255, 0)

            if key[0] == 'h':
                color = (0, 255, 0)

            elif key[0] == 'f':
                color = (0, 0, 255)

            elif key[0] == 'c':
                color = (255, 0, 0)

            elif key[0] == 'e':
                color = (0, 255, 255)
            elif key[0] == 't':
                color = (0, 255, 255)

            cv2.rectangle(img, value[0], value[1], color, 2, 4)
            cv2.putText(img, key, value[0], cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=color, thickness=2)

        new_img_file_path = os.path.split(image)[0] + f"/结果/"
        if not os.path.exists(new_img_file_path):
            os.makedirs(new_img_file_path)

        cv2.imwrite(f"{new_img_file_path}{os.path.split(image)[1]}", img)
        return f"{new_img_file_path}{os.path.split(image)[1]}"

    # 保存接口返回response
    @staticmethod
    def update_response(db, alg_type, url):

        baidu = BaiduAi(config["server"]["dianjun"]["user"],
                        config["server"]["dianjun"]["password"],
                        config["server"]["dianjun"]["url"])
        while True:

            result = db.execute_sql(f'''select id, image from algorithm where alg_type="{alg_type}" and is_pass is NULL''')

            if not result:
                break

            elif result:

                for id, file in result:

                    try:
                        response = baidu.base_detect(url, file, "filepath", enable_multiple=True)

                    except Exception as e:
                        continue

                    baidu_response = json.dumps(response, ensure_ascii=False)

                    try:
                        if response["code"] == 0:
                            if response["data"]["item_count"] > 0:
                                db.execute_sql(
                                    f'''update algorithm set baidu_response='{baidu_response}', is_pass="pass" 
                                    where id="{id}"''')

                            else:
                                db.execute_sql(
                                    f'''update algorithm set baidu_response='{baidu_response}', is_pass="fail" 
                                    where id="{id}"''')

                        elif response['code'] != 0:
                            db.execute_sql(
                                f'''update algorithm set baidu_response='{baidu_response}', is_pass="error" 
                                where id={id};''')

                    except Exception as e:
                        continue

    # 文件插入数据库，并存储图片文件分辨率及大小
    def file_insert_db(self, path, type, db):

        file_list = []
        for f in db.execute_sql(f'''select image from algorithm where alg_type="{type}"'''):
            file_list.append(f[0])

        sql = 'insert into algorithm(image, alg_type, resolution, size) values '

        for root, dirs, files in os.walk(path):
            if '结果' in root:
                continue
            else:
                num = False  # 用来判断插入是否有数据，无则不执行sql

                if '.DS_Store' in files:
                    files.remove('.DS_Store')   # 删除Mac自带的文件
                for n in range(len(files)):
                    file_path = root + files[n]

                    if file_path not in file_list:
                        if files[n].split('.')[1].lower() in ('png', 'jpg', 'jpeg'):
                            num = True
                            resolution_size = self.get_resolution_size_for_db(file_path)
                            if n < len(files)-1:
                                sql += f'''("{file_path}", "{type}", "{resolution_size[0]}", "{resolution_size[1]}"),'''
                            else:
                                sql += f'''("{file_path}", "{type}", "{resolution_size[0]}", "{resolution_size[1]}")'''
                    else:
                        continue
        if num:
            result = db.execute_sql(sql)
            print(result)
        else:
            print("无新增数据，开始调用接口识别数据！")

    @staticmethod
    def get_resolution_size_for_db(path):
        img = Image.open(path)
        resolution = img.size  # 获取文件分辨率

        # 获取文件大小
        try:
            size = os.path.getsize(path)

            # 计算大小
            byte = float(size)
            kb = byte / 1024
            if kb >= 1024:
                m = kb / 1024
                return f"{resolution[0]}*{resolution[1]}", "%.1fm" % m
            else:
                return f"{resolution[0]}*{resolution[1]}", f"{int(kb)}kb"

        except Exception as e:
            raise e

    # 测试集数据写入Excel
    def test_data_insert_excel(self, excel_path, sheet_name, file_path):
        wb = load_workbook(excel_path)
        sheet = wb[sheet_name]
        row = input("请输入Excel开始插入位置：")
        self.file_list(file_path=file_path, whether_excel=1, row=row, sheet=sheet)
        wb.save(config["data_log"])

    # 获取文件大小及分辨率 写入Excel
    @staticmethod
    def get_resolution_size(picture, row, sheet):

        img = Image.open(picture)
        resolution = img.size     # 获取文件分辨率

        sheet.cell(row, 6).value = f"{resolution[0]}*{resolution[1]}"

        # 获取文件大小
        try:
            size = os.path.getsize(picture)

            # 计算大小
            byte = float(size)
            kb = byte/1024
            if kb >= 1024:
                m = kb/1024
                sheet.cell(row, 5).value = "%.1fm" % m
            else:
                sheet.cell(row, 5).value = f"{int(kb)}kb"
        except Exception as e:
            raise e

    @staticmethod
    def update_name(old_file, new_name):
        path = os.path.split(old_file)[0]
        os.rename(old_file, f"{path}/{new_name}")

    # 获取目录下所有符合要求的图片，根据关键字判断是否将名称写入Excel中
    def file_list(self, file_path, relative_path='', whether_excel=0, row=1, sheet=None):     # whether_excel判断是否调用Excel

        all_file = list(os.listdir(f"{file_path}"))

        for f in all_file:
            if "结果" not in f and f != "货船客船":
                path = f"{file_path}{f}"

                if os.path.isfile(path):
                    if f.split('.')[1].lower() == 'png' or f.split('.')[1].lower() == 'jpg' or f.split('.')[1].lower() == 'jpeg':
                        if whether_excel == 1:
                            sheet.cell(row, column=1).value = f"{relative_path}{f}"
                            row += 1
                        else:
                            file.append(path)
                elif os.path.isdir(path):
                    if whether_excel == 1:
                        self.file_list(file_path=f"{path}/", relative_path=f"{f}/", whether_excel=1, row=row, sheet=sheet)
                    else:
                        self.file_list(file_path=f"{path}/")

    # 获取对象坐标
    @staticmethod
    def get_point(item):

        return (
            (int(item['location']['left']), int(item['location']['top'])),
            (
                int(item['location']['left'] + item['location']['width']),
                int(item['location']['top'] + item['location']['height'])
            )
        )

    # 图片标记框
    @staticmethod
    def draw_rectangle_by_point(img_file_path, image_name, point):

        img = cv2.imread(f"{img_file_path}/{image_name}")

        for key, value in point.items():

            if key[0] == 'b':
                color = (0, 255, 0)

            if key[0] == 'h':
                color = (0, 255, 0)

            elif key[0] == 'f':
                color = (0, 0, 255)

            elif key[0] == 'c':
                color = (255, 0, 0)

            elif key[0] == 'e':
                color = (0, 255, 255)

            cv2.rectangle(img, value[0], value[1], color, 2, 4)
            cv2.putText(img, key, value[0], cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=color, thickness=2)

        now_time = datetime.datetime.now()
        new_img_file_path = img_file_path + f"/结果{now_time.year}{now_time.month}{now_time.day}/"
        if not os.path.exists(new_img_file_path):
            os.makedirs(new_img_file_path)

        cv2.imwrite(f"{new_img_file_path}{image_name}", img)


class Run:

    @staticmethod
    def use_api(api_name, url):

        baidu = BaiduAi(config["server"]["dianjun"]["user"],
                        config["server"]["dianjun"]["password"],
                        config["server"]["dianjun"]["url"])

        num = {"all": 0, "yes": 0, "no": 0, "error": 0}  # 记录成功及失败数

        # 根据选择调用的api判断
        # 船只识别
        if api_name == "BOAT_DETECT":

            for row in range(73, 102):      # 按行读取Excel中文件名
                num["all"] += 1
                wb = load_workbook(config["ship_result"])
                sheet = wb.active

                file_name = sheet.cell(row, 1).value

                im = config["file_path"]["ship"]+file_name

                # Excel中写入文件大小及分辨率
                Util().get_resolution_size(picture=im, row=row, sheet=sheet)

                try:
                    response = baidu.base_detect(url, im, 'filepath', enable_multiple=True)

                    if "data" in response:
                        if response["code"] == 0:
                            if response["data"]["item_count"] > 0:

                                num["yes"] += 1

                                sheet.cell(row, column=config["column"]).value = "yes"

                                dp = ShipTarget(response['data']['items'], row, sheet=sheet)
                                dp.judge_item(im)

                            else:
                                num["no"] += 1
                                sheet.cell(row, column=config["column"]).value = "no"
                                print(f'{im} 未识别到对象！')

                        elif response['code'] != 0:
                            num['error'] += 1
                            sheet.cell(row, column=config["column"]).value = "error"
                            print(f'{im} 图片异常！', response)
                    else:
                        print(f'{im} 服务异常！', response)
                    wb.save(config["ship_result"])
                finally:
                    wb.save(config["ship_result"])
                    continue

        # 全目标
        elif api_name == "FULL_TARGET":

            Util().file_list(file_path=config['file_path']['full'])

            for im in file:
                num["all"] += 1
                response = baidu.base_detect(url, im, 'filepath', enable_multiple=True)

                if "data" in response:
                    if response["code"] == 0:
                        if response["data"]["item_count"] > 0:

                            num["yes"] += 1

                            dp = FullTarget(response['data'])
                            dp.judge_item(im)

                        else:
                            num["no"] += 1
                            print(f'{im} 未识别到对象！')

                    elif response['code'] != 0:
                        num['error'] += 1
                        print(f'{im} 图片异常！', response)
                else:
                    print(f'{im} 服务异常！', response)

        # 非法捕鱼
        elif api_name == "FISHING_DETECT":
            Util().file_list(file_path=config['file_path']['fish'])

            for im in file:

                num["all"] += 1
                response = baidu.base_detect(url, im, 'filepath', enable_multiple=True)
                # print(response)
                if "data" in response:
                    if response["code"] == 0:
                        if response["data"]["item_count"] > 0:
                            num["yes"] += 1
                            dp = FishTarget(response['data']['items'])
                            dp.judge_item(im)

                        else:
                            num["no"] += 1
                            print(f'{im} 未识别到对象！')

                    elif response['code'] != 0:
                        num['error'] += 1
                        print(f'{im} 图片异常！', response)
                else:
                    print(f'{im} 服务异常！', response)

        print(f"图片总数：{num['all']}\n成功识别数：{num['yes']}\n未识别到目标数：{num['no']}\n接口异常数：{num['error']}")

        print('all files are processed!', time.strftime('%Y-%m-%d %H:%M:%S'))

    def run(self):

        db = DB()

        while True:
            api = input("请选择调用的api\n1、全目标\n2、船只识别：\n3、非法捕鱼\n4、垃圾桶检测\n")
            if api not in ("1", "2", "3", "4"):
                print("选择错误！")
                continue
            else:
                break

        if api == "1":  # 全目标

            # 1、数据库中保存所有文件
            Util().file_insert_db(config['file_path']['full'], type='full', db=db)

            # 2、调用对应接口并将返回的response保存至数据库
            Util().update_response(db, 'full', config["url_map"]["FULL_TARGET"])

            FullTarget(db).judge_item()

        elif api == "2":    # 船只识别

            # 船只数据写入Excel
            # Util().test_data_insert_excel(config["ship_result"], 'boat', config['file_path']['ship'])

            self.use_api("BOAT_DETECT", config["url_map"]["BOAT_DETECT"])

        elif api == "3":    # 非法捕鱼
            # 捕鱼数据写入Excel
            # Util().test_data_insert_excel(config["data_log"], "fishing_detect", config["data_log"])

            self.use_api("FISHING_DETECT", config["url_map"]["FISHING_DETECT"])

        elif api == "4":    # 垃圾桶检测

            # 数据库中保存文件及路径，type文件适用算法类型  full：全目标,fishing：非法捕鱼,boat：船只,trash：垃圾桶
            Util().file_insert_db(config["file_path"]["trash"], type='trash', db=db)

            Util().update_response(db, "trash", config["url_map"]["trash_status_detect"])

            TrashTarget(db).judge_item()

        db.close()


if __name__ == '__main__':

    print('file processing started！', time.strftime('%Y-%m-%d %H:%M:%S'))

    Run().run()

    # BaiduAi._base_detect(url, image, 'url', min_score=0.6)


