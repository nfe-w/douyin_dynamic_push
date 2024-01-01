# douyin_dynamic_push

## 声明:

- 本仓库发布的`douyin_dynamic_push`项目中涉及的任何脚本，仅用于测试和学习研究，禁止用于商业用途
- `nfe-w` 对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害
- 以任何方式查看此项目的人或直接或间接使用`douyin_dynamic_push`项目的任何脚本的使用者都应仔细阅读此声明
- `douyin_dynamic_push` 保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或`douyin_dynamic_push`项目，则视为已接受此免责声明
- 本项目遵循`MIT LICENSE`协议，如果本声明与`MIT LICENSE`协议有冲突之处，以本声明为准

## 简介

定时检测指定作者的动态，如果发生变化进行推送

## Docker

```sh
# 构建镜像
docker build -t nfew/douyin_dynamic_push:latest .

# 启动容器
docker run -d -v ~/config_douyin.ini:/mnt/config_douyin.ini --name douyin_dynamic_push nfew/douyin_dynamic_push:latest
```

## 运行环境

- [Python 3](https://www.python.org/)

## 使用教程

#### 1. 填写config_douyin.ini配置信息

(1)`config`下的参数

- `signature_server_url`为签名服务器url，参考 https://github.com/coder-fly/douyin-signature
- `username_list`为需要扫描的作者名称列表，使用英文逗号分隔，必填（接口现在不返回作者信息了，重新获取还挺麻烦的，自己填上凑合用先）
- `sec_uid_list`为需要扫描的作者sec_uid列表，使用英文逗号分隔，需与username_list对应，必填（网页版抖音打开用户首页，url获取，例如 https://www.douyin.com/user/MS4wLjABAAAAGeiluJjizroSmPhcNdlsS0b7M0rxi5ygfrtqdByE0FCYi__j0fS_E52uGaF7ujpn）
- `user_account_list`为用于检测开播状态的抖音号列表，使用英文逗号分隔
- `intervals_second`为扫描间隔秒数，不建议过于频繁，必填
- `begin_time`为扫描开始时间，非必填，不支持跨日期
- `end_time`为扫描停止时间，非必填，不支持跨日期

(2)`proxy_pool`下的参数

- `enable`是否启用ip池
- `proxy_pool_url`为ip池地址，如果启用ip池，则必填，参考 https://github.com/jhao104/proxy_pool

(3)`push_serverChan`下的参数

- `enable`是否启用serverChan推送
- `serverChan_SCKEY`如果启用该推送，则必填，参考 http://sc.ftqq.com/3.version

(4)`push_serverChan_turbo`下的参数

- `enable`是否启用serverChan_Turbo推送
- `serverChan_SendKey`如果启用该推送，则必填，参考 https://sct.ftqq.com

(5)`push_wechat`下的参数

- `enable`是否启用微信推送
- `corp_id`企业id，如果启用该推送，则必填
- `agent_id`应用id，如果启用该推送，则必填
- `corp_secret`应用Secret，如果启用该推送，则必填

(6)`push_dingtalk`下的参数

- `enable`是否启用钉钉bot推送
- `access_token`机器人access_token，如果启用该推送，则必填

#### 2.安装第三方库

`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

#### 3.启动脚本

`nohup python3 -u main.py >& douyin_dynamic_push.log &`
