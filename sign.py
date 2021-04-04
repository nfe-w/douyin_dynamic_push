# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Description: 
#
# @Author: yanran.wan
# @Time: 2021/4/4 23:41
import requests

from config import global_config
from logger import logger


class Sign(object):
    signature_server_url = None

    def __init__(self):
        self.signature_server_url = global_config.get_raw('config', 'signature_server_url')

    def get_signature(self):
        # noinspection PyBroadException
        try:
            return requests.get(self.signature_server_url).text
        except Exception:
            logger.error('【获取签名】连接失败')
            return None


sign = Sign()
