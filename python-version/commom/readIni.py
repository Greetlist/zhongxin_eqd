# coding: utf-8
import os
import configparser
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# 封装读取ini文件
class ReadInt:
    def __init__(self,file="conf\data.ini"):
        self.cf = configparser.ConfigParser()
        self.cf.read(os.path.join(path,file))

    # 返回配置信息
    def getIni(self,section,option):
        return self.cf.get(section,option)

    # # 获取所有的section
    # def get_section(self):
    #     return self.cf.sections()
    #
    # # 根据section获取所有的option
    # def get_option(self,section):
    #     return self.cf.items(section)



