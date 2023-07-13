# coding: utf-8
import logging
import time
import os
from common import getData


class Log(object):
    def __init__(self, logger=None):
        # 创建一个logger日志器
        self.logger = logging.getLogger(logger)
        # 日志级别参数化
        log_level = getData.getLog_level()

        # 设计日志器输出级别
        if log_level == "DEBUG" or log_level == "debug":
            setLev = logging.DEBUG
        elif log_level == "INFO" or log_level == "info":
            setLev = logging.INFO
        elif log_level == "WARN" or log_level == "warn" or log_level == "WARNING" or log_level == "warning":
            setLev = logging.WARN
        elif log_level == "ERROR" or log_level == "error":
            setLev = logging.ERROR
        else:
            print("log_level : 输入错误")
        self.logger.setLevel(setLev)

        # 定义日志存储文件名
        self.log_time = time.strftime("%Y_%m_%d")
        self.path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.log_path = os.path.join(self.path, "log")
        self.log_name = self.log_path + "\\" + self.log_time + "test.log"

        # 创建文件处理器，写入日志
        fh = logging.FileHandler(self.log_name, "a", encoding="utf-8")

        # 创建控制台处理器，输出到控制台
        sh = logging.StreamHandler()

        # 创建格式器
        formatter = logging.Formatter(
            "[%(asctime)s] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s]%(message)s")

        # 控制台及文件处理器添加格式器
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)

        # 控制台及文件处理器添加级别
        fh.setLevel(setLev)
        sh.setLevel(setLev)

        # 添加控制台处理器、添加文件处理器
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

        # 关闭流
        fh.close()
        sh.close()

    def getLog(self):
        return self.logger

