from sensoro.tools.db import *
import json
from jsonpath import jsonpath
from sensoro.api.openai_sdk_base import *


def test_target(image, url):
    baidu = BaiduAi(ReadFile.read_config('$.sdk.DianJun..user')[0],
                    ReadFile.read_config('$.sdk.DianJun..password')[0],
                    ReadFile.read_config('$.sdk.DianJun..url')[0])

    response = baidu.base_detect(
        url, image, "filepath", enable_multiple=True)

    print(response)


if __name__ == '__main__':

    image = '/Users/sunzhaohui/Desktop/升哲资料/SensoroTestData/属性对比测试集/人脸/人脸365.jpeg'
    test_target(image, '/v2/whole/target/detect')
