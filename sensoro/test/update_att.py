#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
更新已标记图片的属性内容
"""
from sensoro.tools.db import DB
import os
import json

db = DB()


def update_att():
    data = db.execute_sql(f"""select id, file_path, attribute, v1, console_attribute from algorithm_precision 
    where type=1 and delete_time is null""")

    for im_id, file, attribute, v1, console_attribute in data:
        att = json.loads(attribute)
        print('\n',im_id, list(os.path.split(file))[1], '\n', att['attribute']['年龄段'])
        # print(console_attribute)

        v1 = json.loads(v1)
        print(v1['attribute']['年龄段'])
        # print(console_attribute)
        if console_attribute:
            att_console = json.loads(console_attribute)

            print(att_console['attributes']['age']['value'])

        a = input("输入年龄段：")

        if a:
            att['attribute']['年龄段'] = a
            db.execute_sql(f"""update algorithm_precision
            set attribute='{json.dumps(att, ensure_ascii=False)}' where id={im_id}""")
        else:
            print(att['attribute']['年龄段'])
            continue


if __name__ == '__main__':
    update_att()
