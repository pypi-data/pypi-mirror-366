#! /usr/local/bin/python
#-*- coding:utf-8 -*-

"""
@author: weber.juche@gmail.com
@time: 2016/12/5 20:47

Redis客户端订阅封装

"""

import sys

import os
import time
import redis

from weberFuncs import PrintTimeMsg, GetCurrentTime, IsPython3, PrintAndSleep


class CLogCmdRedis(redis.StrictRedis):

    def __init__(self, host='localhost', port=6379,
                 db=0, password=None, socket_timeout=None,
                 **kwarg):
        redis.StrictRedis.__init__(self, host=host, port=port,
                                   db=db, password=password,
                                   socket_timeout=socket_timeout,
                                   **kwarg)
        self.sFullPathRedisLogFN = ''  # 默认为空表示不启用

    def SetFullPathRedisLogFN(self, sFullPathRedisLogFN):
        # 设置记录Redis命令的文件名，空串表示不记录
        self.sFullPathRedisLogFN = sFullPathRedisLogFN

    def execute_command(self, *args, **options):
        oRet = redis.StrictRedis.execute_command(self, *args, **options)
        # PrintTimeMsg('exec(%s)=%s!' % (' '.join(args),str(oRet)) )
        if self.sFullPathRedisLogFN:
            with open(self.sFullPathRedisLogFN, "a") as f:  # 追加模式输出
                lsS = []
                for arg in args:
                    lsS.append(str(arg))
                sLogMsg = 'exec(%s)=%s!' % (' '.join(lsS),str(oRet))
                sS = "[%s]%s\n" % (GetCurrentTime(), sLogMsg)
                f.write(sS)
        return oRet


def GetRedisClient(sRedisParam):
    # try:
    #     import redis
    # except ImportError as e:
    #     import traceback
    #     traceback.print_exc()
    # sRedisParam = '192.168.2.209:6379:6'
    # sRedisParam = '192.168.2.209:6379:6:password'
    redisHOST = '127.0.0.1'
    redisPORT = 6379
    redisDB = 1
    redisPASS = None   # WeiYF.20160414 Redis参数支持密码
    redisTIMEOUT = 120  # WeiYF.20170322 支持超时参数
    lsP = sRedisParam.split(':')
    if len(lsP) >= 2:
        redisHOST = lsP[0]
        redisPORT = int(lsP[1])
        if len(lsP) >= 3:
            redisDB = int(lsP[2])
            if len(lsP) >= 4:
                redisPASS = lsP[3]
                if len(lsP) >= 5:
                    redisTIMEOUT = int(lsP[4])
    oRedis = CLogCmdRedis(host=redisHOST, port=redisPORT, db=redisDB,
                          password=redisPASS,
                          socket_timeout=redisTIMEOUT,  # WeiYF.20160606 新增超时参数
                          decode_responses=True,  # WeiYF.20250731 自动把 bytes 转成 str
                          )
    sRedisParamHint = '%s:%s:%s' % (redisHOST, redisPORT, redisDB)
    PrintTimeMsg("GetRedisClient(%s)ReturnOK..." % sRedisParamHint)
    return oRedis


class CRedisClientBase:

    def __init__(self, sRedisParam=''):
        self.oRedis = GetRedisClient(sRedisParam)

    def __del__(self):
        if self.oRedis:
            self.oRedis.connection_pool.disconnect()
            PrintTimeMsg("CRedisClientBase.disconnect()!!!")

    def TryConnect(self):
        if not self.oRedis:
            self.oRedis = redis.StrictRedis(host=self.redisHOST, port=self.redisPORT,
                                            db=self.redisDB, password=self.redisPASS,
                                            decode_responses=True)
            sMsg = "{%d}TryConnect.connect(%s)..." % (os.getpid(), self.sRedisParamHint)
            PrintTimeMsg(sMsg)


class CRedisSubscribe(CRedisClientBase):

    def __init__(self, sRedisParam=''):
        CRedisClientBase.__init__(self, sRedisParam)
        self.oPubSub = None
        self.bLoopRunFlag = True  # WeiYF.20150514 循环运行标记，为False时退出订阅循环

    def __del__(self):
        if self.oPubSub:
            self.oPubSub.close()
        CRedisClientBase.__del__(self)

    def SubscribeAndLoop(self, sSubKey, ftCallBack, iTimeOutSeconds=60, ftCBTimeOut=None):
        self.oPubSub = None
        iLoopCnt = 0
        tmLastGetMsg = 0
        tmLastTimeOut = time.time()  # 订阅后首次超时也退出
        while self.bLoopRunFlag:
            if not self.oPubSub:
                self.TryConnect()
                self.oPubSub = self.oRedis.pubsub()
                if '*' in sSubKey:
                    self.oPubSub.psubscribe(sSubKey)
                else:
                    self.oPubSub.subscribe(sSubKey)
                sMsg = 'Subscribe(%s)' % str(sSubKey)
                # LogCriticalMsg(sMsg)
                PrintTimeMsg('oPubSub.' + sMsg + '...')
            if not self.oPubSub.connection:
                PrintTimeMsg('oPubSub.connection=None...')
                if self.oPubSub:
                    self.oPubSub.close()
                    self.oPubSub = None
                time.sleep(0.001)  # be nice to the system :)
                continue
            iLoopCnt += 1
            # msg = ''
            try:
                # if self.oPubSub and self.oPubSub.connection:
                # WeiYF.20150608 应该是不判断链接状态，才会出异常
                # WeiYF.20150609 经测试，不判断链接状态，不会出异常
                msg = self.oPubSub.get_message()  # No Block 不阻塞
            except Exception as e:
                PrintTimeMsg('oPubSub.Exception.e=(%s)Continue...' % (str(e)))
                if self.oPubSub:
                    self.oPubSub.close()
                    self.oPubSub = None
                time.sleep(0.001)  # be nice to the system :)
                continue
            if msg:
                # PrintTimeMsg('oPubSub.msg=%s=' % msg)
                sType = msg.get('type', '')
                if sType == 'subscribe':
                    PrintTimeMsg('oPubSub.SubscribeReturn=(%s)' % str(msg))
                elif sType == 'message' or sType == 'pmessage':
                    # PrintTimeMsg("SubscribeAndLoop.iLoopCnt=%s,msg=%s=" % (iLoopCnt, msg))
                    sChannel = msg.get('channel', b'')
                    sData = msg.get('data', b'')
                    # PrintTimeMsg(f"SubscribeAndLoop.type(sChannel)={type(sChannel)},type(sData)={type(sData)}=")
                    if sData:  # and type(sData) == str
                        # PrintTimeMsg("SubscribeAndLoop.iLoopCnt=%s,RcvData=(%s)" % (iLoopCnt,str(sData)) )
                        # if IsPython3() and sData is bytes:
                        #     # sData = sData.decode('utf8')
                        #     pass
                        #     # PrintTimeMsg("SubscribeAndLoop.iLoopCnt=%s,sData=(%s)" % (iLoopCnt, sData))
                        # else:
                        #     sData = str(sData)
                        # if IsPython3():
                        #     sChannel = sChannel.decode('utf8')
                        if sChannel is bytes:
                            sChannel = sChannel.decode('unicode_escape')  # bytes -> str
                        if sData is bytes:
                            sData = sData.decode('unicode_escape')  # bytes -> str
                        ftCallBack(sChannel, sData)
                        tmLastTimeOut = time.time()
                    else:
                        PrintTimeMsg("SubscribeAndLoop.iLoopCnt=%s,Receive=(%s)" % (iLoopCnt, str(msg)))
                time.sleep(0.01)  # be nice to the system :)
                continue
            else:
                if ftCBTimeOut and time.time() - tmLastTimeOut > iTimeOutSeconds:
                    # 超时回调 #and tmLastTimeOut>0
                    # 调用 ftCBTimeOut 首次也要调用，否则会出现没有数据情况下吊死
                    ftCBTimeOut()
                    tmLastTimeOut = time.time()
                if time.time() - tmLastGetMsg > 60:  # 60秒主动检查一次
                    if sSubKey is str and sSubKey.startswith('LIST_'):
                        # 若是列表型，则主动去查询列表
                        lsData = self.oRedis.lrange(sSubKey, 0, 0)  # 取第一个
                        if len(lsData) >= 1:
                            sData = lsData[0]
                            PrintTimeMsg("SubscribeAndLoop.iLoopCnt=%s,GetData=(%s)" % (iLoopCnt, str(sData)))
                            ftCallBack('@LIST', sData)
                            tmLastTimeOut = time.time()
                            tmLastGetMsg = tmLastTimeOut
                sleepSeconds = 0.1  # 0.01
                time.sleep(sleepSeconds)  # be nice to the system :)


def mainCRedisSubscribe():
    # o = CRedisSubscribe()
    o = CRedisSubscribe('localside:6379:5')

    def cbPrint(sChannel, sData):
        PrintTimeMsg("cbPrint.sChannel=%s,sData=%s=" % (sChannel, sData))
    # o.SubscribeAndLoop('ME:TEST',cbPrint)
    o.SubscribeAndLoop('*', cbPrint)

# ------------------------------


def RedisPipeWatchExec(oRedis, lsWatchKeys, ftCallBackGet, ftCallBackSet, bVerbose=True):
    with oRedis.pipeline() as pipe:
        iLoopCnt = 0
        while True:
            iLoopCnt += 1
            try:
                # put a WATCH on the key that holds our sequence value
                pipe.watch(*lsWatchKeys)
                # after WATCHing, the pipeline is put into immediate execution
                # mode until we tell it to start buffering commands again.
                # this allows us to get the current value of our sequence
                # # current_value = pipe.get('OUR-SEQUENCE-KEY')
                # # next_value = int(current_value) + 1
                if not ftCallBackGet(pipe):
                    PrintTimeMsg('RedisPipeWatchExec.#%d.ftCallBackGet()=Error!' % iLoopCnt)
                    return False, 'GetError'
                # now we can put the pipeline back into buffered mode with MULTI
                pipe.multi()
                # # pipe.set('OUR-SEQUENCE-KEY', next_value)
                if ftCallBackSet(pipe):
                    # and finally, execute the pipeline (the set command)
                    oRet = pipe.execute()
                    if bVerbose:
                        PrintTimeMsg('RedisPipeWatchExec.#%d.execute().OUT=%s!' % (iLoopCnt, str(oRet)))
                    return True, oRet
                PrintTimeMsg('RedisPipeWatchExec.#%d.Discard!' % iLoopCnt)
                pipe.reset()
                return False, 'Discard'
                # if a WatchError wasn't raised during execution, everything
                # we just did happened atomically.
                # # break
            except redis.WatchError as e:
                # another client must have changed 'OUR-SEQUENCE-KEY' between
                # the time we started WATCHing it and the pipeline's execution.
                # our best bet is to just retry.
                PrintTimeMsg('RedisPipeWatchExec.#%d.WatchError=(%s)=Continue!' % (iLoopCnt, str(e)))
                if iLoopCnt > 5:
                    PrintTimeMsg('RedisPipeWatchExec.iLoopCnt=(%d)>5!' % iLoopCnt)
                    return False, 'LoopOut'
                continue
            except Exception as e:
                PrintTimeMsg('RedisPipeWatchExec.#%d.Exception=(%s)=Discard!' % (iLoopCnt, str(e)))
                pipe.reset()
                return False, 'Exception'


def mainRedisPipeWatchExec():
    r = redis.Redis(host='localhost', port=6379)

    def fGet(p):
        print(p.get('num'))
        return True
        # return False

    def fSet(p):
        p.set('key1', 'value1')
        p.incr('num')
        print(p.command_stack)
        p.pipeline_execute_command('SET', 'key2', 'value2')
        # p.pipeline_execute_command('SET key3 value3')
        print(p.command_stack)
        time.sleep(5)
        return True
        # return False
    RedisPipeWatchExec(r, ['key1', 'num'], fGet, fSet)


# -------------------------------
if __name__ == '__main__':
    mainCRedisSubscribe()
    # mainRedisPipeWatchExec()
