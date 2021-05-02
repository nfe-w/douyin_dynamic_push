# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/24 19:11

import time

from config import global_config
from logger import logger
from proxy import my_proxy
from query_douyin import query_dynamic
from query_douyin import query_live_status

if __name__ == '__main__':
    enable_dynamic_push = global_config.get_raw('config', 'enable_dynamic_push')
    enable_living_push = global_config.get_raw('config', 'enable_living_push')
    uid_list = global_config.get_raw('config', 'uid_list').replace('\n', '').split(',')
    sec_uid_list = global_config.get_raw('config', 'sec_uid_list').replace('\n', '').split(',')
    room_id_list = global_config.get_raw('config', 'room_id_list').replace('\n', '').split(',')
    intervals_second = global_config.get_raw('config', 'intervals_second')
    intervals_second = int(intervals_second)
    begin_time = global_config.get_raw('config', 'begin_time')
    end_time = global_config.get_raw('config', 'end_time')

    if len(uid_list) != len(sec_uid_list):
        logger.error('uid_list与sec_uid_list数量不相同，请检查配置文件')
        exit(1)

    if begin_time == '':
        begin_time = '00:00'
    if end_time == '':
        end_time = '23:59'

    logger.info('开始检测')
    while True:
        current_time = time.strftime("%H:%M", time.localtime(time.time()))
        if begin_time <= current_time <= end_time:
            my_proxy.current_proxy_ip = my_proxy.get_proxy()
            for i in range(len(uid_list)):
                if enable_dynamic_push == 'true':
                    if uid_list[i] == '' or sec_uid_list[i] == '':
                        continue
                    query_dynamic(uid_list[i], sec_uid_list[i])
            for _ in room_id_list:
                if enable_living_push == 'true':
                    if _ == '':
                        continue
                    query_live_status(_)
        time.sleep(intervals_second)
