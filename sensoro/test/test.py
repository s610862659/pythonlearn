from sensoro.tools.db import *
import json
from jsonpath import jsonpath

db = DB()


def att():
    data = db.execute_sql(f"""select attribute from algorithm_precision 
    where type=3 and id<24169 and delete_time is not null """)

    car = {}  # 记录属性数量
    # print(data)

    for item in data:
        item = json.loads(item[0])
        att = item['attribute']
        if att['机动车类型'] in car:
            car[att['机动车类型']] += 1
        else:
            car[att['机动车类型']] = 1

    print(car)

    for i in car.keys():
        print(i)

    print()

    for j in car.values():
        print(j)


def update_filepath():
    data = db.execute_sql(f"""select id, file_path, type from algorithm_precision 
        where type in (1,2,4) and delete_time is not null """)

    for im_id, obj, im_type in data:
        # print(os.path.split(filepath))
        name = os.path.split(obj)[1]
        # print(name)
        if im_type == 1:
            new_path = os.path.join(
                os.path.join('/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/', '人脸'), name)
        elif im_type == 2:
            new_path = os.path.join(
                os.path.join('/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/', '人体'), name)
        elif im_type == 4:
            new_path = os.path.join(
                os.path.join('/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/', '非机动车'), name)

        db.execute_sql(f"""update algorithm_precision set file_path='{new_path}' where id={im_id}""")


if __name__ == '__main__':
    # /Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/机动车/机动车4089.jpeg
    # '/Users/sunzhaohui/Desktop/SensoroTestData/算法对比测试集/人体/人体4276.jpeg
    # update_filepath()
    att()
