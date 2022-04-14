# coding=utf-8
"""告警视频批量下载"""

import requests
import json
import time
import os
from selenium import webdriver


class Main(object):

    def send_post(self, url, data, headers):

        # 解决warning报错，对功能无影响
        requests.packages.urllib3.disable_warnings()

        result = requests.post(url, json=data, headers=headers)  # verify=false跳过https验证
        return json.loads(result.text)

    def send_get(self, url, data, headers):
        # 解决warning报错，对功能无影响
        requests.packages.urllib3.disable_warnings()

        result = requests.get(url=url, json=data, headers=headers, verify=False)
        return result.text

    def run_main(self, method, url=None, data=None, headers=None):
        result = None
        if method == 'post':
            result = self.send_post(url, data, headers)
        elif method == 'get':
            result = self.send_get(url, data, headers)
        else:
            print('methon值错误')
        return result


def down_video(video_url):
    # 打开浏览器
    # 加启动配置
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    # 打开chrome浏览器
    driver = webdriver.Chrome(chrome_options=option)
    # driver = webdriver.Chrome()
    driver.get(video_url)
    time.sleep(15)
    driver.quit()


def login():
    login_url = 'https://ai-api.dianjun.sensoro.vip/api/user/v1/passwordLogin'
    login_data = {"username": "mlxcsophia", "password": "Sensoro20192020", "clientType": 2}

    token = {}
    info = Main().run_main(method='post', url=login_url, data=login_data)

    token['authorization'] = 'Bearer ' + info['data']['token']

    return token


class GetVideo:

    def __init__(self, header):
        self.header = header

    def get_data(self):
        # 国标设备告警
        gb_url = "https://ai-api.dianjun.sensoro.vip/common/gb/alarm/v1/alarmResult/queryAlarmResults"

        at = input("请输入任务类型：\n"
                   "0：全部\n"
                   "1:人工视频报警\n"
                   "2:运动目标检测报警\n"
                   "3:遗留物监测报警\n"
                   "4:物体移除监测报警\n"
                   "5:绊线检测报警\n"
                   "6:入侵检测报警\n"
                   "7:逆行检测报警\n"
                   "8:徘徊检测报警\n"
                   "9:流量统计报警\n"
                   "10:密度检测报警\n"
                   "11:视频异常检测报警\n"
                   "12:快速移动报警\n"
                   "13:行为识别\n"
                   "24:双光谱热成像报警\n"
                   "32:雷达双光谱禁捕预警\n"
                   "33:船只识别报警\n"
                   "34:捕鱼识别报警\n"
                   "35:垃圾桶监测告警\n"
                   "36:烟火监测告警\n"
                   "37:视频质量监测告警\n"
                   "46:遛狗未牵绳\n"
                   "47:高空抛物\n")
        while True:
            if at == '':
                at = input("输入错误，请重新选择：")
                continue
            else:
                break

        alarmtype = ["1",  # 人工视频报警
                     "2",  # 运动目标检测报警
                     "3",  # 遗留物监测报警
                     "4",  # 物体移除监测报警
                     "5",  # 绊线检测报警
                     "6",  # 入侵检测报警
                     "7",  # 逆行检测报警
                     "8",  # 徘徊检测报警
                     "9",  # 流量统计报警
                     "10",  # 密度检测报警
                     "11",  # 视频异常检测报警
                     "12",  # 快速移动报警
                     "13",  # 行为识别
                     "24",  # 双光谱热成像报警
                     "32",  # 雷达双光谱禁捕预警
                     "33",  # 船只识别报警
                     "34",  # 捕鱼识别报警
                     "35",  # 垃圾桶监测告警
                     "36",  # 烟火监测告警
                     "37",  # 视频质量监测告警
                     "46",  # 遛狗未牵绳
                     "47"  # 高空抛物
                     ]
        if at != 0:
            alarmtype = [int(at)]

        # print("接下来请输入正确的时间格式，否则程序可能无法正常执行，如：2013-09-10 23:40:00")
        # startTime = input("录入查询开始时间（y-m-d h:m:s）：")
        # endTime = input("录入查询结束时间时间（y-m-d h:m:s）：")
        startTime = "2022-04-01 00:00:00"
        endTime = "2022-04-10 14:20:00"

        startTime = int(time.mktime(time.strptime(startTime, "%Y-%m-%d %H:%M:%S"))) * 1000
        endTime = int(time.mktime(time.strptime(endTime, "%Y-%m-%d %H:%M:%S"))) * 1000

        gb_data = {"alarmStatus": 1,
                   "gbAlarmMethod": "5",
                   "startTime": startTime,
                   "endTime": endTime,
                   "gbAlarmType": alarmtype,
                   "page": 1,
                   "size": 200}
        # print(gb_data)
        result_alarm = Main().run_main(method="post", url=gb_url, data=gb_data, headers=self.header)
        return result_alarm

    # 获取视频s3地址
    def down_url(self):
        result = self.get_data()
        # print(result)
        # print(type(result['data']['list']))
        data_list = result['data']['list']

        for i in range(len(data_list)):

            channelid = data_list[i]['device']['channelSerial']
            name = data_list[i]['device']['name']
            captureTime = data_list[i]['capture']['captureTime']
            action = data_list[i]['capture']['labels']  # 告警类型

            down_data = {"captureTime": captureTime, "channelId": channelid, "devicePlatType": 2, "name": name}

            down_url = f"https://ai-api.dianjun.sensoro.vip/common/static/v1/video/live.m3u8/{channelid}/hls/download"

            du = Main().run_main(method='post', url=down_url, data=down_data, headers=self.header)

            if du['message'] == '查询时间段内的录像不存在':
                print(1)
                continue
            else:
                down_video(du['data']['objectSignUrl'])

                time.sleep(5)
                update_filename(i, action)


def update_filename(num, action):
    file_list = list(os.walk(os.getcwd()))[0][2]
    for file in file_list:
        if file.split('.')[1] == 'ts' and 'XC' in file.split('.')[0]:
            name = ''
            for s in action:
                name += s
            os.rename(file, file.split('.')[0]+f'_{name}{num}.ts')


if __name__ == '__main__':

    # 登录系统获取token
    # login()

    # 调用一次上方代码获取token
    headers = login()
    # # 获取视频下载地址
    GetVideo(headers).down_url()

