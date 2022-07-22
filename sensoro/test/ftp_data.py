#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
连接ftp服务器并通过ftp上传或下载图片
host: ams-test-ftp.sensoro.com
port: 2121
user: sensoro
passwd: Sensoro2019
"""
from ftplib import FTP
import os


def ftp_connect(host, username, password):
    ftp = FTP()

    # 服务器ip和端口
    ftp.connect(host, 2121)

    # 登录
    ftp.login(username, password)

    return ftp


# 本地上传文件到ftp
def upload_file(ftp, localpath, remotepath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary(remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()


if __name__ == '__main__':
    # ftp = ftp_connect('ams-test-ftp.sensoro.com', 'sensoro', 'Sensoro2019')
    path = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/人脸聚类测试集'

    for dirs in list(os.walk(path))[0]:
        print(dirs)

    # upload_file(ftp)
