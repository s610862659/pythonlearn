#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
 sdk : /v1/boat/detect
1、验证船只检测detect_flag参数是否生效，0不走检测，1走检测
    detect_flag =0 的时候, 是否只返回了 reid_feature
2、detect_flag生效的前提下
    验证抠图+detect_flag=0检测到的特征值和场景图+detect_flag=1的检测结果是否一致
    (目前有对场景图抠出的小图的外扩逻辑, 所以可能仍会有误差)， 若不一致特征距离是否在0.1以内
"""

from sensoro.tools.ReadConfig import *
from sensoro.tools.DrawRectangle import draw_rectangle
from sensoro.tools.get_point import get_point
from sensoro.baidu_api.openai_sdk_base import BaiduAi
import math
import os

config = read_config()


def test_flag():

    baidu = BaiduAi(config["sdk"]["pre"]["user"],
                    config["sdk"]["pre"]["password"],
                    config["sdk"]["pre"]["url"])
    path = '/Users/sunzhaohui/Desktop/SensoroTestData/船只检测detect_flag参数验证'
    for folder in sorted(list(os.walk(path))[0][1]):    # 24,26

        print(folder, ':')
        reid = []
        for file in os.listdir(os.path.join(path, folder)):
            # print(reid)
            if '宜昌市渔政' in file:     # 场景图
                if file != '结果' and file != '.DS_Store':
                    try:
                        response = baidu.base_detect(
                            config['url_map']['boat'],
                            os.path.join(os.path.join(path, folder), file),
                            "filepath",
                            detect_flag=1)
                        # print(json.dumps(response))
                    except Exception as e:
                        # raise e
                        print(e, "服务异常！")
                    if response['data']['item_count'] > 1 and folder in ('24', '26'):  # 24,26会检测出多条货船，取客船数据
                        # print(response)
                        for i in range(len(response['data']['items'])):
                            if response['data']['items'][i]['name'] == '客船':
                                point = get_point(response['data']['items'][i]['location'])

                                reid.append(response['data']['items'][i]['reid_feature'])
                    else:
                        point = get_point(response['data']['items'][0]['location'])

                        reid.append(response['data']['items'][0]['reid_feature'])
                        # print(response['data']['items'][0]['reid_feature'])
                    draw_rectangle(os.path.join(os.path.join(path, folder), file), point)

            elif file != '结果' and file != '.DS_Store':  # 抠图

                try:
                    response = baidu.base_detect(
                        config['url_map']['boat'],
                        os.path.join(os.path.join(path, folder), file),
                        "filepath",
                        detect_flag=0)
                    # print(json.dumps(response))
                except Exception as e:
                    # raise e
                    print(e, "服务异常！")
                print(file, response['data']['item_count'])
                reid.append(response['data']['items'][0]['reid_feature'])
        print(len(reid))
        print(calc_distance(reid_a=reid[0], reid_b=reid[1]))


def calc_distance(reid_a, reid_b) -> float:
    return math.sqrt(sum(((reid_a[i] - reid_b[i]) ** 2 for i in range(len(reid_a)))))


if __name__ == '__main__':
    test_flag()
