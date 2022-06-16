# coding=utf-8

import pymysql
import datetime
from typing import Union
import json
from sensoro.tools.ReadConfig import *


class DB:
    mysql = read_config()['database']

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



