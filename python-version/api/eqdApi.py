# coding: utf-8
import requests
from common import getData
from common.log import Log

lg = Log(__name__).getLog()


class Api:
    def __init__(self, USER_ID=getData.getUsername(), contract_id=getData.getContract_id()):
        # 获取url，文件data.ini保存配置参数，通过readIni()公共方法读取ini文件配置信息，通过getData获取具体配置信息
        self.host = getData.getHost()
        # 获取用户id
        self.USER_ID = USER_ID
        # 获取用户密码
        self.USER_PWD = getData.getPassword()
        # 获取合约id
        self.contract_id = contract_id
        # 获取登录成功后返回的Bearer + " " + token
        self.Authorization = self.login()

    # 登录接口，获取token
    def login(self):
        url = self.host + "/public/login"
        head = {"USER_ID": self.USER_ID,
                "USER_PWD": self.USER_PWD}
        res = requests.post(url=url, headers=head)
        return "Bearer" + " " + res.json()["RESULTSET"][0]["AUTHORIZATION"]

    # 获取合约信息，得到合约id后放入conf/data.ini文件中，实现参数化，方便后续接口调用
    def get_party_info(self):
        url = self.host + "/eqd/public/get_party_info"
        head = {"USER_ID": self.USER_ID,
                "Authorization": self.Authorization}
        res = requests.post(url=url, headers=head)
        lg.info(res.text)
        return res

    # 当日指令查询
    def get_swap_order(self):
        url = self.host + "/eqd/public/get_swap_order"
        head = {"USER_ID": self.USER_ID,
                "Authorization": self.Authorization}
        data = {"CONTRACT_ID": self.contract_id,
                "Page_Ndx": 1,
                "Page_Size": 20}
        res = requests.post(url=url, headers=head, json=data)
        lg.info(res.text)
        return res

    # 查询当日持仓
    def get_swap_position(self):
        url = self.host + "/eqd/public/get_swap_position"
        head = {"USER_ID": self.USER_ID,
                "Authorization": self.Authorization}
        data = {"CONTRACT_ID": self.contract_id,
                "PAGE_NUM": "1",
                "PAGE_SIZE": "20"}
        res = requests.post(url=url, headers=head, json=data)
        lg.info(res.text)
        return res

    # 约券申请提交
    def  put_quota_set_order(self):
        url = self.host + "/eqd/public/put_quota_set_order"
        head = {"USER_ID": self.USER_ID,
                "Authorization": self.Authorization,
                "SYS_ID":"C",
                "STATION":"PC:172.0.0.1:00-00-00-00-00-00:00000000000000E0:zhang.xc:TF655AY91GHRVL:BFEBFBFF000306A9:C:FAT32:80"}
        data = {"ASSET_TYPE":"SPT_S",
                "CASH_ACCT_ID":"01000510620",
                "CCY_CODE":"CNY",
                "CONTRACT_ID":self.contract_id,
                "EVENT_TYPE":"50",
                "EXT_INFO":"NULL",
                "INST_CODE":"000001",
                "LOAN_RATE":"6",
                "MARKET_TYPE":"XSHE",
                "ORDER_COUNT":"10000",
                "REMARK":"beizhu",
                "REQ_DATE":"2022-11-25",
                "REQ_ID":"",
                "REQ_TIME":"2022-11-25",
                "SYS_ID":"0",
                "TRADE_DATE":"2022-11-25",
                "TRADE_TYPE":"10"}
        res = requests.post(url=url, headers=head, json=data)
        lg.info(res.text)
        return res

    # 约券申请查询
    def get_quota_order_list(self):
        url = self.host + "/eqd/public/get_quota_order_list"
        head = {"USER_ID": self.USER_ID,
                "Authorization": self.Authorization,
                "SYS_ID": "C",
                "STATION": "PC:172.0.0.1:00-00-00-00-00-00:00000000000000E0:zhang.xc:TF655AY91GHRVL:BFEBFBFF000306A9"
                           ":C:FAT32:80"}
        data = {"CONTRACT_ID": self.contract_id,
                "INST_CODE": "",
                "ORDER_STATUS": "",
                "TRADE_DATE":"null"}
        res = requests.post(url=url, headers=head, json=data)
        lg.info(res.text)
        return res

    # 券池查询
    def get_quota_summary_list(self):
        url = self.host + "/eqd/public/get_quota_summary_list"
        head = {"USER_ID": self.USER_ID,
                "Authorization": self.Authorization,
                "SYS_ID":"C",
                "STATION":"PC:172.0.0.1:00-00-00-00-00-00:00000000000000E0:zhang.xc:TF655AY91GHRVL:BFEBFBFF000306A9:C"
                          ":FAT32:80"}
        res = requests.post(url=url, headers=head)
        lg.info(res.text)
        return res

    # 黑名单查询接口
    def get_eqd_blacklist_fast(self):
        url = self.host + "/eqd/public/get_eqd_blacklist_fast"
        head = {"Authorization": self.Authorization}
        res = requests.post(url=url, headers=head)
        lg.info(res.text)
        return res


# 主函数，执行入口
if __name__ == '__main__':
    op = Api()
    op.get_party_info()
    op.get_swap_order()
    op.get_swap_position()
    op.put_quota_set_order()
    op.get_quota_order_list()
    op.get_quota_summary_list()
    op.get_eqd_blacklist_fast()


