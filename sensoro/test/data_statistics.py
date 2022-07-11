#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
1、读取数据库algorithm_precision中属性attribute值，统计每个图片属性的值，并将内容写入excel
"""
from sensoro.tools.recording import *
from sensoro.tools.db import DB
import json

db = DB()


class Contrast:

    def __init__(self):
        self.wb = Recording(f'{os.path.abspath("..")}/data/contrast_data.xlsx')

    def contrast(self):
        data = db.execute_sql(
            f"""select id, attribute, type
            from algorithm_precision 
            WHERE delete_time is null""")

        for im_id, att, im_type in data:
            att = json.loads(att)['attribute']

            for key, value in att.items():

                if value in ('', '未知', False):
                    continue
                if im_type == 1:
                    col_value = self.wb.read_excel_for_column('人脸数据', 'B')

                    self._save_excel('人脸数据', col_value, value)
                elif im_type == 2:
                    col_value = self.wb.read_excel_for_column('人体数据', 'B')
                    if key == '随身物品':
                        for item in value:
                            self._save_excel('人体数据', col_value, item)
                    else:
                        self._save_excel('人体数据', col_value, value)

                elif im_type == 3:
                    col_value = self.wb.read_excel_for_column('机动车数据', 'B')

                    if key == '车牌状态':
                        for item in value:
                            self._save_excel('机动车数据', col_value, item)
                    elif key == '车牌号码':
                        if value:
                            self._save_excel('机动车数据', col_value, '车牌号码')
                    else:
                        self._save_excel('机动车数据', col_value, value)
                elif im_type == 4:
                    col_value = self.wb.read_excel_for_column('非机动车数据', 'B')
                    if key == '头部特征':
                        for item in value:
                            self._save_excel('非机动车数据', col_value, item)
                    else:
                        self._save_excel('非机动车数据', col_value, value)

        self.wb.save(f"{os.path.abspath('..')}/data/{'contrast_data.xlsx'}")

    # 数据存储excel
    def _save_excel(self, sheet_name, col_value, value):
        """

        :param sheet_name: excel中sheet名称
        :param col_value: excel中属性描述list
        :param value: 标记的属性值
        :return:
        """

        for i in range(len(col_value)):
            if col_value[i] == value:
                v = self.wb.read_excel_cell(sheet_name, i+1, 3)
                if not v:
                    v = 0
                self.wb.write_excel(sheet_name, i+1, 3, v+1)


if __name__ == '__main__':
    Contrast().contrast()
    db.close()
