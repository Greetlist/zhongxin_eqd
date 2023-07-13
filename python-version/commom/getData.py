# coding: utf-8
from common.readIni import ReadInt
from common.log import Log
re = ReadInt()


# 获取url
def getHost():
    host = re.getIni("MESSAGE", "host")
    return host


# 获取用户名
def getUsername():
    username = re.getIni("MESSAGE", "username")
    return username


# 获取密码
def getPassword():
    password = re.getIni("MESSAGE", "password")
    return password


def getContract_id():
    contract_id = re.getIni("MESSAGE", "contract_id")
    return contract_id


def getLog_level():
    log_level = re.getIni("MESSAGE", "log_level")
    return log_level

def getLog():
    lg = Log().getLog()
    return lg
