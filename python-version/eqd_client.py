import argh
import sys
import os
import requests
import configparser
import pandas as pd

class EQDClient:
    def __init__(self, config_file="conf/account.ini"):
        self.config = configparser.ConfigParser()
        self.loan_cols = ["AvailableCount", "LoadRate", "Sid", "ExchangeID", "FinanceType", "TradeDate", "ShortName", "SecurityName"]
        self.loan_col_map = {
            "RT_AVA_COUNT":"AvailableCount",
            "LOAN_RATE": "LoadRate",
            "INST_CODE": "Sid",
            "MARKET_TYPE": "ExchangeID",
            "ASSET_TYPE": "FinanceType",
            "TRADE_DATE":"TradeDate",
            "SHORTNAMEPY":"ShortName",
            "SECURITY_NAME":"SecurityName",
        }

        self.blacklist_cols = ["ControlLevel", "Sid", "ExchangeId", "FinanceType", "TradeType", "SecurityName"]
        self.blacklist_col_map = {
            "CONTROL_LEVEL": "ControlLevel",
            "INST_CODE": "Sid", 
            "MARKET_TYPE": "ExchangeID",
            "ASSET_TYPE": "FinanceType",
            "TRADE_TYPE": "TradeType",
            "INST_CODE_NAME": "SecurityName",
        }

        if os.path.exists(config_file):
            self.config.read(config_file)
        else:
            print("config_file: [{}] not exists".format(config_file))
            sys.exit(1)

    def init(self):
        self.login()

    def login(self):
        url = self.config.get("ACCOUNT", "host") + "/public/login"
        head = {
            "USER_ID": self.config.get("ACCOUNT", "username"),
            "USER_PWD": self.config.get("ACCOUNT", "password"),
        }
        print(head)
        res = requests.post(url=url, headers=head)
        print(res.json())
        self.auth_code = res.json()["RESULTSET"][0]["AUTHORIZATION"]

    def query_pool(self):
        url = self.config.get("ACCOUNT", "host") + "/eqd/public/get_quota_summary_list"
        head = {
            "USER_ID": self.config.get("ACCOUNT", "username"),
            "Authorization": "Bearer " + self.auth_code,
            "SYS_ID": "C",
            "STATION": "PC:192.168.104.12:00-00-00-00-00-00:00000000000000E0:zhang.xc:TF655AY91GHRVL:BFEBFBFF000306A9:C:FAT32:80"
        }
        res = requests.post(url=url, headers=head)
        ret_json = res.json()
        self.dump_result(ret_json, "loan_list.csv")

    def query_blacklist(self):
        url = self.config.get("ACCOUNT", "host") + "/eqd/public/get_eqd_blacklist_fast"
        head = {
            "Authorization": "Bearer " + self.auth_code,
        }
        res = requests.post(url=url, headers=head)
        ret_json = res.json()
        self.dump_result(ret_json, "blacklist.csv")

    def dump_result(self, ret_json, csv_name):
        if ret_json["RET_CODE"] != 0:
            print("Request Error")
            return
        if ret_json["TOTAL_COUNT"] == 0:
            df = pd.DataFrame(colums=self.blacklist_cols)
        else:
            df = pd.DataFrame(ret_json["RESULTSET"])
            df = df.rename(columns=self.blacklist_col_map)
        tmp_csv = csv_name + '.tmp'
        df.to_csv(tmp_csv, index=False)
        os.rename(tmp_csv, csv_name)

def query():
    c = EQDClient()
    c.init()
    c.query_pool()
    c.query_blacklist()

if __name__ == '__main__':
    argh.dispatch_commands([query])
