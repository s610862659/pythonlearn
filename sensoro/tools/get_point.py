#!/usr/bin/env/ python3
# -*- coding:utf-8 -*-


def get_point(location):
    return (
        (int(location['left']), int(location['top'])),
        (
            int(location['left'] + location['width']),
            int(location['top'] + location['height'])
        )
    )
