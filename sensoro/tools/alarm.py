# coding=utf-8
"""
功能：告警视频下载
"""

import time
import os
import yaml
from selenium import webdriver

from login import *

y = open("./config.yml")     # 读取yaml文件配置
config = yaml.load(y, Loader=yaml.SafeLoader)


# 下载告警视频
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

        alarm_type = ["1",  # 人工视频报警
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
            alarm_type = [int(at)]

        # print("接下来请输入正确的时间格式，否则程序可能无法正常执行，如：2013-09-10 23:40:00")
        # start_time = input("录入查询开始时间（y-m-d h:m:s）：")
        # end_time = input("录入查询结束时间时间（y-m-d h:m:s）：")

        start_time = int(time.mktime(config['time']['startTime'].timetuple())) * 1000
        end_time = int(time.mktime(config['time']['endTime'].timetuple())) * 1000

        gb_data = {"alarmStatus": 1,
                   "gbAlarmMethod": "5",
                   "startTime": start_time,
                   "endTime": end_time,
                   "gbAlarmType": alarm_type,
                   "page": 1,
                   "size": config['size']}
        # print(gb_data)
        result_alarm = Main().run_main(method="post", url=gb_url, data=gb_data, header=self.header)
        return result_alarm

    # 获取视频s3地址
    def down_url(self):
        result = self.get_data()
        # print(result)
        # print(type(result['data']['list']))
        data_list = result['data']['list']

        for i in range(len(data_list)):

            channel_id = data_list[i]['device']['channelSerial']
            name = data_list[i]['device']['name']
            capture_time = data_list[i]['capture']['captureTime']
            action = data_list[i]['capture']['labels']  # 告警类型

            down_url_get = f"https://ai-api.dianjun.sensoro.vip/common/static/v1/video/live.m3u8/" \
                           f"{channel_id}/captureVideo?captureTime={capture_time}&" \
                           f"devicePlatType=2&channelId={channel_id}"

            du = Main().run_main(method='get', url=down_url_get, data='', header=self.header)

            if 'list' in du['data']:
                if du['data']['list']:

                    self.down_video(du['data']['list'][0]['downloadUrl'])

                else:

                    # 实际就算调用该接口，返回值也与上方调用接口返回一致，此内容是为了避免s3中有视频，但未返回
                    down_data = {"captureTime": capture_time, "channelId": channel_id, "devicePlatType": 2, "name": name}

                    down_url_post = f"https://ai-api.dianjun.sensoro.vip/common/static/v1/video/live.m3u8/{channel_id}/hls/download"
                    du = Main().run_main(method='post', url=down_url_post, data=down_data, header=self.header)
                    # print(du)

                    if du['message'] == '查询时间段内的录像不存在':
                        print('查询时间段内的录像不存在')
                        continue
                    else:
                        print(2)
                        self.down_video(du['data']['objectSignUrl'])
            else:
                print('服务异常', du)

            time.sleep(5)
            self.update_filename(action)

    @staticmethod
    def update_filename(action):
        file_list = list(os.walk(os.getcwd()))[0][2]
        for file in file_list:
            if file.split('.')[1] == 'ts' \
                    and '有人钓鱼' not in file.split('.')[0] and '网鱼' not in file.split('.')[0]:

                name = ''
                for s in action:
                    if s == '钓鱼':
                        s = '有人钓鱼'
                    name += s
                os.rename(file, file.split('.')[0]+f'_{name}.ts')

    @staticmethod
    def down_video(video_url):
        # 打开浏览器
        # 加启动配置
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        # 打开chrome浏览器
        driver = webdriver.Chrome(chrome_options=option)
        # driver = webdriver.Chrome()
        driver.get(video_url)
        time.sleep(10)
        driver.quit()


if __name__ == '__main__':

    url = config['server']['test']['url']
    data = {"username": config['server']['test']['user'],
            "password": config['server']['test']['password'],
            "clientType": 2}

    # 登录系统获取token
    # login()

    # 调用一次上方代码获取token
    headers = login(url, data)

    # 获取视频下载地址，并下载视频
    # GetVideo(headers).down_url()

    # 人员布控打通门禁



