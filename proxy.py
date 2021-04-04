# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/4/1 14:20

import requests

from config import global_config
from logger import logger


class Proxy(object):
    enable = None
    proxy_pool_url = None

    current_proxy_ip = None

    def __init__(self):
        self.enable = global_config.get_raw('proxy_pool', 'enable')
        self.proxy_pool_url = global_config.get_raw('proxy_pool', 'proxy_pool_url')

    def get_proxy(self):
        if self.enable != 'true':
            return None

        retry_count = 10
        timeout = 2
        while retry_count > 0:
            # noinspection PyBroadException
            try:
                ip_pool_response = requests.get(self.proxy_pool_url + "/get")
            except Exception:
                logger.error('【ip池】连接失败')
                return None

            proxy_ip = ip_pool_response.json().get("proxy", None)
            if proxy_ip is None:
                logger.info('【ip池】当前为空池')
                return None

            # noinspection PyBroadException
            try:
                response = requests.get('https://www.iesdouyin.com/web/api/v2/aweme/post', proxies={"http": "http://{}".format(proxy_ip)},
                                        timeout=timeout)
                if response.status_code == requests.codes.OK:
                    logger.info('【ip池】获取ip成功: {}'.format(proxy_ip))
                    return proxy_ip
            except ConnectionRefusedError:
                retry_count -= 1
                self.delete_proxy(proxy_ip)
            except Exception:
                retry_count -= 1
        logger.info('【ip池】尝试10次均未获取到有效ip'.format(retry_count))
        return None

    def delete_proxy(self, proxy_ip):
        requests.get(self.proxy_pool_url + "/delete/?proxy={}".format(proxy_ip))
        logger.info('【ip池】移除ip: {}'.format(proxy_ip))


my_proxy = Proxy()
