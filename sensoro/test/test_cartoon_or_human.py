#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
测试百度人脸检测：
针对卡通人脸及真实人脸校验准确性
"""
import os
from sensoro.tools import extractor


def test(baidu, url: list, path):

    # 记录v1 v2检测正确数据
    result = {'cartoon': 0, 'human': 0}
    false = {'cartoon': [], 'human': []}
    # print(urls)
    for folder in ['cartoon', 'human']:
        print(folder)
        images = list(os.walk(os.path.join(path, folder)))[0][2]

        for image in sorted(images):

            if image == '.DS_Store':
                continue
            # image = '卡通.jpeg'
            response = baidu.base_detect(
                url_path=url,
                image=os.path.join(path, f"{folder}/{image}"),
                image_type='filepath',
                enable_multiple=True
            )
            # print(response)
            try:
                face_type = extractor(response, '$..face_type')[0]
                # print(face_type['name'])
            except Exception as e:
                print(image, '\t', '无识别', e)
                continue
            print(image, '\t', face_type['name'])
            if folder == 'cartoon':
                if face_type['name'] == 'cartoon':
                    result['cartoon'] += 1
                else:
                    false['cartoon'].append(image)
            elif folder == 'human':
                if face_type['name'] == 'human':
                    result['human'] += 1
                else:
                    false['human'].append(image)
        print()

    print(f"检测结果:\n"
          f"cartoon检测正确数量：\n"
          f"{result['cartoon']}\n"
          f"human检测正确数量：\n"
          f"{result['human']}")

    print(f"错误数据：\n"
          f"cartoon：\n"
          f"{false['cartoon']}\n"
          f"human:"
          f"{false['human']}\n")
