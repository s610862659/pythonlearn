#!/usr/bin/env/python3
# -*- coding:utf-8 -*-


def target(baidu, url: str, image: str, image_type: str, **kwargs):
    try:
        response = baidu.base_detect(url, image, image_type, kwargs)
        return response
    except Exception as e:
        raise e
