#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/27 16:10 
# @Author : Scott
# @Software: PyCharm
import os

SECRET_KEY = os.environ.get('SECRET_KEY_PUMCH') or 'f\xf9\x05\xa9_an\xec\x5d*\x29\xd4\xc4.\x91\\N\xecO\xf4\xfaVr\xf1'
SALT_KEY = os.environ.get('SALT_KEY_PUMCH') or 'welcome to pumch 2025.'

CSRF_ENABLED = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_RECORD_QUERIES = True

# 日志文件路径
LOGFILE_PATH = os.path.join(os.getcwd(), 'logs')
# 用户的游戏数据
USER_GAME_DATA = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'user_game_data')

WX_APP_ID = 'wx4af101973469ff70'
WX_APP_SECRET = '32bd429ead93a022b54e8609ec7a22da'
WX_LOGIN_URL = 'https://api.weixin.qq.com/sns/jscode2session'

BAIDU_AI_API_KEY = 'xjJt8cTFOAZIw13kPYWX39wH'
BAIDU_AI_SECRET_KEY = '1eBdyMVfJwG99Ge5t9P2J27eOwsGHwor'