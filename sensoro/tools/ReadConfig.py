import os
import yaml


def read_config():
    # 读取配置文件
    with open(f"{os.path.abspath('..')}/config.yml", "r", encoding="utf-8") as y:
        config = yaml.load(y.read(), Loader=yaml.FullLoader)
    return config
