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
        else:
            raise 'error'

        params.update(kwargs)
        return self._base_request(url_path=url_path, **params)


# 对象处理
class DataProcessing:

    def __init__(self, data):
        self.data = data

    # 计算各个对象的值
    def get_num_human_or_face_car(self, image_path):
        lenth = len(self.data['items'])
        # 记录数量
        num = {'human': 0, 'face': 0, 'car': 0, 'electric-car': 0}
        point = {}

        items = self.data['items']
        for i in range(lenth):
            if items[i]['type'] == 'human':

                point['h'+str(items[i]['id'])] = self.get_point(items[i])

                num['human'] += 1

            elif items[i]['type'] == 'face':

                num['face'] += 1

            elif items[i]['type'] == 'car':
                num['car'] += 1
            elif items[i]['type'] == 'electric-car':
                num['electric-car'] += 1
        self.draw_rectangle_by_point(image_path, "/Users/sunzhaohui/Desktop/升哲测试数据/百度云端算法/1.jpg", point, num)
        return num

    # 取坐标
    def get_point(self, item):

        return (
            (int(item['location']['left']), int(item['location']['top'])),
            (
                int(item['location']['left'] + item['location']['width']),
                int(item['location']['top'] + item['location']['height'])
            )
        )

    # 图片标记框，确定是否有重复识别情况
    def draw_rectangle_by_point(self, img_file_path, new_img_file_path, points, nums: dict):

        img = cv2.imread(img_file_path)
        for j in range(nums['human']):
            # print(points['h'+str(j)][0],points['h'+str(j)][1])

            cv2.rectangle(img, points['h'+str(j)][0],
                          points['h'+str(j)][1], (0, 255, 0), 1, 4)
            cv2.putText(img, 'h'+str(j), points['h'+str(j)][0], cv2.FONT_HERSHEY_COMPLEX, fontScale=5, color=(0,0,255), thickness=1)
        cv2.imwrite(new_img_file_path, img)


if __name__ == '__main__':
    url = "/v1/whole/target/detect"
    user = "f4c8620816b74f7a9ccf184ece74117f"
    password = "Sensoro2021A#BaoDingA#365"
    server = "https://openai-api.dianjun.sensoro.vip"

    baidu = BaiduAi(url, user, password, server)

    # 图片类型：url，文件系统路径、base64编码后的字符串，图片参数的类型，["filepath", "url", "base64str"]

    # image = "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fimg95.699pic.c" \
    #         "om%2Fxsj%2F16%2Frp%2Fed.jpg%21%2Ffw%2F700%2Fwatermark%2F" \
    #         "url%2FL3hzai93YXRlcl9kZXRhaWwyLnBuZw%2Falign%2Fsoutheast&ref" \
    #         "er=http%3A%2F%2Fimg95.699pic.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=a" \
    #         "uto?sec=1651055378&t=4ebf99c3d4d4c061bba40437116d50dc"

    # BaiduAi._base_detect(url, image, 'url', min_score=0.6)
    image_list = ["/Users/sunzhaohui/Desktop/升哲测试数据/百度云端算法/人体3.png"]
    # image = "/Users/sunzhaohui/Downloads/合照-5.jpg"
    for i in range(len(image_list)):
        response = baidu.base_detect(url, image_list[i], 'filepath', min_score=0.6, enable_multiple=True)
        # print(response['data'])
        num = DataProcessing(response['data']).get_num_human_or_face_car(image_list[i])

        print(f"第{i + 1}张图各对象数量及关联关系：\n\t 人体:{num['human']},人脸:{num['face']},"
              f"机动车:{num['car']},非机动车{num['electric-car']}")
        print('\t', response['data']['relation_map'])

        # 人体位置坐标
        # location位置信息
        # left  位置相对左边框的坐标
        # top   位置相对上边框的坐标
        # width 宽度
        # height高度



