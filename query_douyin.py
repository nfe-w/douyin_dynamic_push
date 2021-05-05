# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/4/4 21:54

import json
import time
from collections import deque

from bs4 import BeautifulSoup

import util
from logger import logger
from push import push
from sign import sign

DYNAMIC_DICT = {}
LIVING_STATUS_DICT = {}
LEN_OF_DEQUE = 10


def query_dynamic(uid=None, sec_uid=None):
    if uid is None or sec_uid is None:
        return
    signature = sign.get_signature()
    query_url = 'http://www.iesdouyin.com/web/api/v2/aweme/post?sec_uid={}&count=21&max_cursor=0&aid=1128&_signature={}'.format(sec_uid, signature)
    headers = get_headers(uid, sec_uid)
    response = util.requests_get(query_url, '查询动态状态', headers=headers, use_proxy=True)
    if util.check_response_is_ok(response):
        result = json.loads(str(response.content, 'utf-8'))
        if result['status_code'] != 0:
            logger.error('【查询动态状态】请求返回数据code错误：{code}'.format(code=result['status_code']))
        else:
            aweme_list = result['aweme_list']
            if len(aweme_list) == 0:
                logger.info('【查询动态状态】【{sec_uid}】动态列表为空'.format(sec_uid=sec_uid))
                return

            aweme = aweme_list[0]
            aweme_id = aweme['aweme_id']
            uid = aweme['author']['uid']
            nickname = aweme['author']['nickname']

            if DYNAMIC_DICT.get(uid, None) is None:
                DYNAMIC_DICT[uid] = deque(maxlen=LEN_OF_DEQUE)
                for index in range(LEN_OF_DEQUE):
                    if index < len(aweme_list):
                        DYNAMIC_DICT[uid].appendleft(aweme_list[index]['aweme_id'])
                logger.info('【查询动态状态】【{nickname}】动态初始化：{queue}'.format(nickname=nickname, queue=DYNAMIC_DICT[uid]))
                return

            if aweme_id not in DYNAMIC_DICT[uid]:
                previous_aweme_id = DYNAMIC_DICT[uid].pop()
                DYNAMIC_DICT[uid].append(previous_aweme_id)
                logger.info('【查询动态状态】【{}】上一条动态id[{}]，本条动态id[{}]'.format(nickname, previous_aweme_id, aweme_id))
                DYNAMIC_DICT[uid].append(aweme_id)
                logger.info(DYNAMIC_DICT[uid])

                aweme_type = aweme['aweme_type']
                if aweme_type not in [4]:
                    logger.info('【查询动态状态】【{nickname}】动态有更新，但不在需要推送的动态类型列表中'.format(nickname=nickname))
                    return

                content = None
                pic_url = None
                video_url = None
                if aweme_type == 4:
                    content = aweme['desc']
                    pic_url = aweme['video']['origin_cover']['url_list'][0]
                    video_url_list = aweme['video']['play_addr']['url_list']
                    for temp in video_url_list:
                        if 'ixigua.com' in temp or 'api.amemv.com' in temp:
                            continue
                        if 'aweme.snssdk.com' in temp or 'douyinvod.com' in temp:
                            video_url = temp
                            break
                logger.info('【查询动态状态】【{nickname}】动态有更新，准备推送：{content}'.format(nickname=nickname, content=content[:30]))
                push.push_for_douyin_dynamic(nickname, aweme_id, content, pic_url, video_url)


def query_live_status(room_id=None):
    if room_id is None:
        return
    query_url = 'https://webcast.amemv.com/webcast/reflow/{}?my_ts={}`'.format(room_id, int(time.time()))
    headers = get_headers_for_live()
    response = util.requests_get(query_url, '查询直播状态', headers=headers, use_proxy=True)
    if util.check_response_is_ok(response):
        html_text = response.text
        soup = BeautifulSoup(html_text, "html.parser")
        result = None
        scripts = soup.findAll('script')
        for script in scripts:
            script_string = script.string
            if script_string is None:
                continue
            if 'window.__INIT_PROPS__ = ' in script_string:
                result_str = script.string.replace('window.__INIT_PROPS__ = ', '')
                try:
                    result = json.loads(result_str).get('/webcast/reflow/:id', None)
                except TypeError:
                    logger.error('【查询直播状态】json解析错误，room_id：{}'.format(room_id))
                    return None
                break
        if result is None:
            logger.error('【查询直播状态】请求返回数据为空，room_id：{}'.format(room_id))
        else:
            if result.get('room', None) is None:
                logger.error('【查询直播状态】请求返回数据中room为空，room_id：{}'.format(room_id))
                return
            name = result['room']['owner']['nickname']
            live_status = result['room']['status']

            if LIVING_STATUS_DICT.get(room_id, None) is None:
                LIVING_STATUS_DICT[room_id] = live_status
                logger.info('【查询直播状态】【{uname}】初始化'.format(uname=name))
                return

            if LIVING_STATUS_DICT.get(room_id, None) != live_status:
                LIVING_STATUS_DICT[room_id] = live_status

                room_title = result['room']['title']
                room_cover_url = result['room']['cover']['url_list'][0]
                room_stream_url = result['room']['stream_url']['hls_pull_url']

                if live_status == 2:
                    logger.info('【查询直播状态】【{name}】开播了，准备推送：{room_title}'.format(name=name, room_title=room_title))
                    push.push_for_douyin_live(name, room_stream_url, room_title, room_cover_url)


def get_headers(uid, sec_uid):
    return {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.iesdouyin.com/share/user/{}?sec_uid={}'.format(uid, sec_uid),
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'x-requested-with': 'XMLHttpRequest',
    }


def get_headers_for_live():
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    }
