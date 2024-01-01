# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/4/4 21:54

import json
import time
from collections import deque
from urllib import parse

from bs4 import BeautifulSoup

import util
from logger import logger
from push import push
from sign import sign

DYNAMIC_DICT = {}
LIVING_STATUS_DICT = {}
LEN_OF_DEQUE = 10


def query_dynamic(nickname=None, sec_uid=None):
    if nickname is None or sec_uid is None:
        return
    signature = sign.get_signature()
    query_url = 'http://www.iesdouyin.com/web/api/v2/aweme/post?sec_uid={}&count=21&max_cursor=0&aid=1128&_signature={}'.format(sec_uid, signature)
    headers = get_headers()
    response = util.requests_get(query_url, '查询动态状态', headers=headers, use_proxy=True)
    if util.check_response_is_ok(response):
        result = json.loads(str(response.content, 'utf-8'))
        if result['status_code'] != 0:
            logger.error('【查询动态状态】请求返回数据code错误：{code}'.format(code=result['status_code']))
        else:
            aweme_list = result['aweme_list']
            if len(aweme_list) == 0:
                logger.info(f'【查询动态状态】【{nickname}】动态列表为空')
                return

            aweme = aweme_list[0]
            aweme_id = aweme['aweme_id']

            if DYNAMIC_DICT.get(sec_uid, None) is None:
                DYNAMIC_DICT[sec_uid] = deque(maxlen=LEN_OF_DEQUE)
                for index in range(LEN_OF_DEQUE):
                    if index < len(aweme_list):
                        DYNAMIC_DICT[sec_uid].appendleft(aweme_list[index]['aweme_id'])
                logger.info('【查询动态状态】【{nickname}】动态初始化：{queue}'.format(nickname=nickname, queue=DYNAMIC_DICT[sec_uid]))
                return

            if aweme_id not in DYNAMIC_DICT[sec_uid]:
                previous_aweme_id = DYNAMIC_DICT[sec_uid].pop()
                DYNAMIC_DICT[sec_uid].append(previous_aweme_id)
                logger.info('【查询动态状态】【{}】上一条动态id[{}]，本条动态id[{}]'.format(nickname, previous_aweme_id, aweme_id))
                DYNAMIC_DICT[sec_uid].append(aweme_id)
                logger.info(DYNAMIC_DICT[sec_uid])

                try:
                    content = aweme['desc']
                    pic_url = aweme['video']['cover']['url_list'][0]
                    video_url = f'https://www.douyin.com/video/{aweme_id}'
                    logger.info('【查询动态状态】【{nickname}】动态有更新，准备推送：{content}'.format(nickname=nickname, content=content[:30]))
                    push.push_for_douyin_dynamic(nickname, aweme_id, content, pic_url, video_url)
                except AttributeError:
                    logger.error(f'【查询动态状态】dict取值错误，nickname：{nickname}')
                    return


def query_live_status_v2(user_account=None):
    if user_account is None:
        return
    query_url = 'https://live.douyin.com/{}?my_ts={}'.format(user_account, int(time.time()))
    headers = get_headers_for_live()
    response = util.requests_get(query_url, '查询直播状态', headers=headers, use_proxy=True)
    if util.check_response_is_ok(response):
        html_text = response.text
        soup = BeautifulSoup(html_text, "html.parser")
        scripts = soup.findAll('script')
        result = None
        for script in scripts:
            if 'nickname' in script.text:
                script_string = script.string
                unquote_string = parse.unquote(script_string)
                # 截取最外层{}内的内容
                json_string_with_escape = unquote_string[unquote_string.find('{'):unquote_string.rfind('}') + 1]
                # 多层转义的去转义
                json_string = json_string_with_escape.replace("\\\\", "\\").replace("\\\"", '"')
                try:
                    result = json.loads(json_string)
                except TypeError:
                    logger.error('【查询直播状态】json解析错误，user_account：{}'.format(user_account))
                    return None
                break

        if result is None:
            logger.error('【查询直播状态】请求返回数据为空，user_account：{}'.format(user_account))
        else:
            try:
                room_info = result['state']['roomStore']['roomInfo']
                room = room_info.get('room')
                anchor = room_info.get('anchor')
                nickname = anchor['nickname']
            except AttributeError:
                logger.error('【查询直播状态】dict取值错误，user_account：{}'.format(user_account))
                return

            if room is None:
                if LIVING_STATUS_DICT.get(user_account, None) is None:
                    LIVING_STATUS_DICT[user_account] = 'init'
                    logger.info('【查询直播状态】【{uname}】初始化'.format(uname=nickname))
                return

            if room is not None:
                live_status = room.get('status')
                if LIVING_STATUS_DICT.get(user_account, None) is None:
                    LIVING_STATUS_DICT[user_account] = live_status
                    logger.info('【查询直播状态】【{uname}】初始化'.format(uname=nickname))
                    return

                if LIVING_STATUS_DICT.get(user_account, None) != live_status:
                    LIVING_STATUS_DICT[user_account] = live_status

                    if live_status == 2:
                        name = nickname
                        room_title = room['title']
                        room_cover_url = room['cover']['url_list'][0]
                        qrcode_url = room_info['qrcode_url']

                        logger.info('【查询直播状态】【{name}】开播了，准备推送：{room_title}'.format(name=nickname, room_title=room_title))
                        push.push_for_douyin_live(name, query_url, room_title, room_cover_url)


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


def get_headers():
    return {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.iesdouyin.com/',
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
