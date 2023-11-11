#!/bin/bash

if [ ! -f /mnt/config_douyin.ini ]; then
  echo 'Error: /mnt/config_douyin.ini file not found. Please mount the /mnt/config_douyin.ini file and try again.'
  exit 1
fi

cp -f /mnt/config_douyin.ini /app/config_douyin.ini
python -u main.py
