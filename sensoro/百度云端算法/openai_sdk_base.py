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

import base64
import cv2

y = open(f"{os.getcwd()}/config.yml")     # 读取yaml文件配置
config = yaml.load(y, Loader=yaml.SafeLoader)

file = []   # 记录所有符合规则的图片,全目标、捕鱼识别使用


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
        # self.label_map = {
        #     1: "摩托车",
        #     2: "电动摩托车",
        #     3: "电动自行车",
        #     4: "自行车",
        #     5: "儿童脚踏车",
        #     6: "手推车（婴儿车、轮椅、小推车、拉杆车）",
        #     7: "滑板车",
        # }

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

        r = requests.post(api, json=kwargs, headers=headers)

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


# 全目标
class FullTarget:

    def __init__(self, item):
        self.item = item
        self.point = {}     # 记录坐标
        self.attribute = {}     # 记录属性，待补充
        self.item_count = {'human': 0, 'face': 0, 'car': 0, 'electric-car': 0}

    def judge_item(self, image):

        path = os.path.split(image)[0]
        name = os.path.split(image)[1]

        print(name)

        for item_type in self.item["items"]:

            if item_type['type'] == 'human':

                self.item_count['human'] += 1
                self.point['h' + str(item_type['id'])] = Util.get_point(item_type)  # 获取坐标位置
                # self.attribute['h' + str(item_type['id'])] = item_type['attribute']
                print('h' + str(item_type['id']) + f'置信度 {item_type["score"]}')

            elif item_type['type'] == 'face':

                self.item_count['face'] += 1
                self.point['f' + str(item_type['id'])] = Util.get_point(item_type)
                print('f' + str(item_type['id']) + f'置信度 {item_type["score"]}')

            elif item_type['type'] == 'car':

                self.item_count['car'] += 1
                self.point['c' + str(item_type['id'])] = Util.get_point(item_type)
                print('c' + str(item_type['id']) + f'置信度 {item_type["score"]}')

            elif item_type['type'] == 'electric-car':

                self.item_count['electric-car'] += 1
                self.point['e' + str(item_type['id'])] = Util.get_point(item_type)
                print('e' + str(item_type['id']) + f'置信度 {item_type["score"]}')

        print(f"对象数量：\n\t人体:{self.item_count['human']},人脸:{self.item_count['face']},"
              f"机动车:{self.item_count['car']},非机动车{self.item_count['electric-car']}")

        Util.get_relation_map(self.item['relation_map'])

        Util.draw_rectangle_by_point(path, name, self.point)    # 对图像标记并保存

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
            Util().excel_insert(self.row, 2, ship_type, self.sheet)

        if self.sheet.cell(self.row, 4).value:
            pass
        else:
            for i in size:
                if ship_size == '':
                    ship_size = i
                else:
                    ship_size += f",{i}"
            Util().excel_insert(self.row, 4, ship_size, self.sheet)


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


class Util:

    # Excel中写入内容
    @staticmethod
    def excel_insert(row, column, value, sheet):
        # wb = Workbook()

        sheet.cell(row, column).value = value

    # 获取文件大小及分辨率 写入Excel
    def get_resolution_size(self, picture, row, sheet):

        img = Image.open(picture)
        resolution = img.size     # 获取文件分辨率

        self.excel_insert(row, 6, f"{resolution[0]}*{resolution[1]}", sheet)

        # 获取文件大小
        try:
            size = os.path.getsize(picture)

            # 计算大小
            byte = float(size)
            kb = byte/1024
            if kb >= 1024:
                m = kb/1024
                self.excel_insert(row, 5, "%.1fm" % m, sheet)
            else:
                self.excel_insert(row, 5, f"{int(kb)}kb", sheet)
        except Exception as e:
            raise e

    @staticmethod
    def update_name(old_file, new_name):
        path = os.path.split(old_file)[0]
        os.rename(old_file, f"{path}/{new_name}")

    # 获取目录下所有符合要求的图片，根据关键字判断是否将名称写入Excel中
    def file_list(self, file_path, relative_path='', whether_excel=0):     # whether_excel判断是否调用Excel

        all_file = list(os.listdir(f"{file_path}"))

        for f in all_file:
            if "结果" not in f and f != "货船客船":
                path = f"{file_path}{f}"

                if os.path.isfile(path):
                    if f.split('.')[1].lower() == 'png' or f.split('.')[1].lower() == 'jpg' or f.split('.')[1].lower() == 'jpeg':
                        if whether_excel == 1:
                            self.excel_insert(config["num"], 1, f"{relative_path}{f}")
                            config["num"] += 1
                        else:
                            file.append(path)
                elif os.path.isdir(path):
                    if whether_excel == 1:
                        self.file_list(file_path=f"{path}/", relative_path=f"{f}/", whether_excel=1)
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


class Run:

    @staticmethod
    def use_api(api_name, url):

        baidu = BaiduAi(config["user"], config["password"], config["server"])

        num = {"all": 0, "yes": 0, "no": 0, "error": 0}  # 记录成功及失败数

        # 根据选择调用的api判断
        # 船只识别
        if api_name == "BOAT_DETECT":

            # now_time = datetime.datetime.now()  # 获取当前时间

            # sheet.cell(1, column=config["column"]).value \
            #     = f"{now_time.year}{now_time.month}{now_time.day}"  # 每次执行结果行

            num["all"] = 461

            for row in range(82, 462):      # 按行读取Excel中文件名

                wb = load_workbook(config["ship_result"])
                sheet = wb.active

                file_name = sheet.cell(row, 1).value

                im = config["file_path"]["ship"]+file_name

                # Excel中写入文件大小及分辨率
                Util().get_resolution_size(picture=im, row=row, sheet=sheet)

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

        api = input("请选择调用的api\n1、全目标\n2、船只识别：\n3、非法捕鱼\n")
        while True:
            if api not in ("1", "2", "3"):
                api = input("选择错误，请重新选择api\n1、全目标\n2、船只识别\n3、非法捕鱼\n：")
            else:
                break
        if api == "1":
            self.use_api("FULL_TARGET", config["url_map"]["FULL_TARGET"])

        elif api == "2":
            self.use_api("BOAT_DETECT", config["url_map"]["BOAT_DETECT"])

        elif api == "3":
            self.use_api("FISHING_DETECT", config["url_map"]["FISHING_DETECT"])


if __name__ == '__main__':

    print('file processing started！', time.strftime('%Y-%m-%d %H:%M:%S'))

    # wb = load_workbook(config["ship_result"])
    # sheet = wb.active
    # Util().file_list(file_path=config['file_path']['ship'], whether_excel=1)  # 写入文件时使用
    # wb.save(config["ship_result"])

    Run().run()

    # BaiduAi._base_detect(url, image, 'url', min_score=0.6)


