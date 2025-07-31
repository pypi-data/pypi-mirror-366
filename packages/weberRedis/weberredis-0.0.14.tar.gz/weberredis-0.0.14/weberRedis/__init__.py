#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""    
    2015/10/14  WeiYanfeng
    公共函数 包

~~~~~~~~~~~~~~~~~~~~~~~~
共函数 包
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install redis

"""
# WeiYF.20170605 经测试，Python3引用当前目录下的源码文件，文件名前要加`.`点号
# 同时这样的写法也可以在Python2.7下使用。

from .CRedisSubscribe import GetRedisClient,CRedisSubscribe,RedisPipeWatchExec
from .CAutoConnectRedis import CAutoConnectRedis

