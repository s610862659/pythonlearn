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
import os
import json
import hmac
import hashlib
from hashlib import sha256

import requests

import base64
import cv2


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
    def __init__(self, url_map, user_id, user_sk, server_addr):

        self.url_map = url_map
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
    def base_detect(self, url_path: str, image_name: str, image_type, **kwargs):
        """

        :param url_path: 百度api地址
        :param image: 待检测待图片，可以是url，文件系统路径、base64编码后的字符串3中类型
        :param image_type: 图片参数的类型，["filepath", "url", "base64str"]
        :return:
        """
        image = file_path + image_name
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


# 对象处理
class DataProcessing:

    def __init__(self, item, key):
        self.item = item
        self.key = key  # 记录调用的接口类型
        self.point = {}     # 记录坐标
        self.attribute = {}     # 记录属性，待补充
        self.item_count = {'human': 0, 'face': 0, 'car': 0, 'electric-car': 0}

    def judge_item(self, image_name, attribute_yes=0):

        image = file_path + image_name

        if self.key == 'FULL_TARGET':   # 全目标检测
            for item_type in self.item:

                if item_type['type'] == 'human':

                    self.item_count['human'] += 1
                    self.point['h' + str(item_type['id'])] = self.get_point(item_type)  # 获取坐标位置
                    # self.attribute['h' + str(item_type['id'])] = item_type['attribute']
                    # print('h' + str(item_type['id']) + f'置信度 {item_type["score"]}')

                elif item_type['type'] == 'face':

                    self.item_count['face'] += 1
                    self.point['f' + str(item_type['id'])] = self.get_point(item_type)
                    # print('f' + str(item_type['id']) + f'置信度 {item_type["score"]}')

                elif item_type['type'] == 'car':

                    self.item_count['car'] += 1
                    self.point['c' + str(item_type['id'])] = self.get_point(item_type)
                    # print('c' + str(item_type['id']) + f'置信度 {item_type["score"]}')

                elif item_type['type'] == 'electric-car':

                    self.item_count['electric-car'] += 1
                    self.point['e' + str(item_type['id'])] = self.get_point(item_type)
                    # print('e' + str(item_type['id']) + f'置信度 {item_type["score"]}')

            print(f"{image_name} 对象数量：\n\t人体:{self.item_count['human']},人脸:{self.item_count['face']},"
                  f"机动车:{self.item_count['car']},非机动车{self.item_count['electric-car']}")

        elif self.key == 'BOAT_DETECT':

            # print(f"{image_name}")

            for num in range(len(self.item)):
                self.point['b'+str(num)] = self.get_point(self.item[num])  # 获取船只坐标位置

                # print('b'+str(num) + f'名称{self.item[num]["name"]}，置信度 {self.item[num]["score"]}')    # 需要置信度时放开

        self.draw_rectangle_by_point(image, image_name)    # 对图像标记并保存

    # 取对象坐标
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
    def draw_rectangle_by_point(self, img_file_path, image_name):

        img = cv2.imread(img_file_path)

        if self.key == 'FULL_TARGET':
            for key, value in self.point.items():
                if key[0] == 'h':
                    cv2.rectangle(img, value[0], value[1], (0, 255, 0), 2, 4)
                    cv2.putText(img, key, value[0], cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=(0, 255, 0), thickness=2)
                elif key[0] == 'f':
                    cv2.rectangle(img, value[0], value[1], (0, 0, 255), 2, 4)
                    cv2.putText(img, key, value[0], cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=(0, 0, 255), thickness=2)
                elif key[0] == 'c':
                    cv2.rectangle(img, value[0], value[1], (255, 0, 0), 2, 4)
                    cv2.putText(img, key, value[0], cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=(255, 0, 0), thickness=2)
                elif key[0] == 'e':
                    cv2.rectangle(img, value[0], value[1], (0, 255, 255), 2, 4)
                    cv2.putText(img, key, value[0], cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=(0, 255, 255), thickness=2)
        elif self.key == 'BOAT_DETECT':
            for key, value in self.point.items():
                cv2.rectangle(img, value[0], value[1], (0, 255, 0), 2, 4)
                cv2.putText(img, key, value[0], cv2.FONT_HERSHEY_COMPLEX, fontScale=2, color=(0, 255, 0),
                            thickness=2)

        new_img_file_path = file_path + "结果/"
        if not os.path.exists(new_img_file_path):
            os.makedirs(new_img_file_path)
        cv2.imwrite(new_img_file_path+image_name, img)

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


# 对象关联关系处理
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


def image_list(path):
    # file_list = os.listdir(path)
    file_list = list(os.walk(path))

    file_name = []

    for file in file_list[0][2]:
        if file.split('.')[1] == 'png' or file.split('.')[1] == 'jpg' or file.split('.')[1] == 'jpeg':
            file_name.append(file)
    return file_name


def run():

    url_map = dict(
        FULL_TARGET="/v1/whole/target/detect",  # 全目标

        # BOAT_DETECT="/v1/boat/detect",  # 船只识别
    )

    user = "f4c8620816b74f7a9ccf184ece74117f"
    password = "Sensoro2021A#BaoDingA#365"
    server = "https://openai-api.dianjun.sensoro.vip"

    baidu = BaiduAi(url_map['FULL_TARGET'], user, password, server)

    for im in image_list(file_path):

        for key, value in url_map.items():

            response = baidu.base_detect(value, im, 'filepath', enable_multiple=True)

            if 'data' in response and response['code'] == 0:

                if response['data']['item_count']>0:
                    # items保存对象不同属性信息
                    # print(response['data']['items'])
                    dp = DataProcessing(response['data']['items'], key)
                    dp.judge_item(im, attribute_yes=0)  # attribute_yes是否返回每个对象属性值，0不返回，1返回;key记录当前使用接口

                    if key == 'FULL_TARGET':
                        # relation_map下保存关联关系list
                        get_relation_map(response['data']['relation_map'])
                else:
                    print(f'{im} 未识别到对象！')
                    continue
            else:
                if response['code'] != 0:
                    print(f'{im} 图片异常！', response)
                else:
                    print(f'{im} 未识别到对象！')
                continue
    print('all files are processed!', time.strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    file_path = os.getcwd() + '/图片/'
    # file_path = '/Users/sunzhaohui/Desktop/升哲测试数据/'
    print('file processing started！', time.strftime('%Y-%m-%d %H:%M:%S'))
    run()

    # 图片类型：url，文件系统路径、base64编码后的字符串，图片参数的类型，["filepath", "url", "base64str"]

    # image = "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fimg95.699pic.c" \
    #         "om%2Fxsj%2F16%2Frp%2Fed.jpg%21%2Ffw%2F700%2Fwatermark%2F" \
    #         "url%2FL3hzai93YXRlcl9kZXRhaWwyLnBuZw%2Falign%2Fsoutheast&ref" \
    #         "er=http%3A%2F%2Fimg95.699pic.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=a" \
    #         "uto?sec=1651055378&t=4ebf99c3d4d4c061bba40437116d50dc"

    # BaiduAi._base_detect(url, image, 'url', min_score=0.6)




        # 人体位置坐标
        # location位置信息
        # left  位置相对左边框的坐标
        # top   位置相对上边框的坐标
        # width 宽度
        # height高度

