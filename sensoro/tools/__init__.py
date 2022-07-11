#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
from typing import *

from jsonpath import jsonpath
from loguru import logger


def extractor(obj: dict, expr: str = '.') -> Any:
    """
    根据表达式提取字典中的value，表达式, . 提取字典所有内容， $.case 提取一级字典case， $.case.data 提取case字典下的data
    :param obj :json/dict类型数据
    :param expr: 表达式, . 提取字典所有内容， $.case 提取一级字典case， $.case.data 提取case字典下的data
    $.0.1 提取字典中的第一个列表中的第二个的值
    """
    try:
        result = jsonpath(obj, expr)
    except Exception as e:
        logger.error(f'{expr} - 提取不到内容，丢给你一个错误！{e}')
        result = expr
    return result
