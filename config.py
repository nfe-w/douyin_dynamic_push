# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2021/3/21 11:40

import configparser
import os

from logger import logger


class Config(object):
    def __init__(self, config_file='config_douyin.ini'):
        self._path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError("No such file: config_douyin.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8-sig')
        self._configRaw = configparser.RawConfigParser()
        self._configRaw.read(self._path, encoding='utf-8-sig')

    def get(self, section, name):
        logger.info('加载配置{}下的{}'.format(section, name))
        return self._config.get(section, name)

    def get_raw(self, section, name):
        logger.info('加载配置{}下的{}'.format(section, name))
        return self._configRaw.get(section, name)


global_config = Config()
