"""
旷世人脸api调用测试
api-key:HD0uDIWsosTAVpXZXTOcgAF-2xIFfQxZ
url:https://api-cn.faceplusplus.com/facepp/v3/detect
"""
from sensoro.tools.db import DB
import requests
import json
from time import sleep

db = DB()


def test_console():
    http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
    api_key = 'HD0uDIWsosTAVpXZXTOcgAF-2xIFfQxZ'
    api_secret = 'CAUisENvYeJje7a15-rJtyzc7uCpuxzl'
    data = {
        'api_key': api_key,
        'api_secret': api_secret,
        'return_landmark': 0,
        'return_attributes': 'gender,age,smiling,headpose,facequality,blur,eyestatus,'
                             'emotion,beauty,mouthstatus,eyegaze,skinstatus,nose_occlusion,'
                             'chin_occlusion,face_occlusion'
        # 'image_file': image_file
    }

    item = db.execute_sql(f"""select id, file_path, attribute
    from algorithm_precision 
    where type=1 and delete_time is null and id>6082""")

    for im_id, file, att in item:
        # image_file = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/人脸/人脸9.jpeg'
        sleep(2)
        files = {'image_file': open(file, 'rb')}

        response = requests.post(http_url, data=data, files=files)
        response = json.loads(response.text)
        # print(response)

        face_att = calc_overlap_rate(response['faces'], att)
        print(face_att)
        db.execute_sql(f"""update algorithm_precision
        set console_attribute='{json.dumps(face_att, ensure_ascii=False)}' where id={im_id}""")


# 计算与标记坐标重叠率，取重叠最大的
def calc_overlap_rate(faces, att):
    data = []   # 记录对象信息
    for face in faces:
        data.append(face)

    if len(data) > 0:
        att = json.loads(att)
        location = att['location']
        # print(location)
        cross_area = {}
        for table in range(len(data)):
            min_x = min(int(location[0][0]), data[table]['face_rectangle']['left'])
            min_y = min(int(location[0][1]), data[table]['face_rectangle']['top'])
            max_x = max(int(location[1][0]), data[table]['face_rectangle']['left']+data[table]['face_rectangle']['width'])
            max_y = max(int(location[1][1]), data[table]['face_rectangle']['top']+data[table]['face_rectangle']['height'])

            cross_x = location[1][0]-location[0][0] + data[table]['face_rectangle']['width'] - (max_x-min_x)
            cross_y = location[1][1]-location[0][1] + data[table]['face_rectangle']['height'] - (max_y-min_y)

            if cross_y < 0 or cross_y < 0:
                continue
            else:
                cross_area[table] = cross_x * cross_y
        max_key = 0
        max_value = 0
        for key, value in cross_area.items():
            if value > max_value:
                max_value = value
                max_key = key
        # print(max_key, data)
        data[max_key].pop('face_token', None)
        data[max_key]['location'] = data[max_key]['face_rectangle']
        data[max_key].pop('face_rectangle', None)
        return data[max_key]

    else:
        return None


if __name__ == '__main__':
    test_console()
    db.close()
