# coding=utf-8

import requests
import json


class Main(object):

    @staticmethod
    def send_post(url, data, header):

        # 解决warning报错，对功能无影响
        requests.packages.urllib3.disable_warnings()

        result = requests.post(url, json=data, headers=header)  # verify=false跳过https验证
        return json.loads(result.text)

    @staticmethod
    def send_get(url, data, header):
        # 解决warning报错，对功能无影响
        requests.packages.urllib3.disable_warnings()

        result = requests.get(url=url, json=data, headers=header, verify=False)
        return json.loads(result.text)

    def run_main(self, method, url=None, data=None, header=None):
        result = None
        if method == 'post':
            result = self.send_post(url, data, header)
        elif method == 'get':
            result = self.send_get(url, data, header)
        else:
            print('methon值错误')
        return result


def login(login_url, login_data):

    token = {}
    info = Main().run_main(method='post', url=login_url, data=login_data)

    token['authorization'] = 'Bearer ' + info['data']['token']

    return token
