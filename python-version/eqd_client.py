import argh
import sys
import os
import requests
import configparser
import pandas as pd
import datetime as dt

class EQDClient:
    def __init__(self, config_file="conf/account.ini"):
        self.config = configparser.ConfigParser()
        self.loan_cols = ["AvailableCount", "LoanRate", "Sid", "ExchangeID", "FinanceType", "TradeDate", "ShortName", "SecurityName"]
        self.loan_col_map = {
            "RT_AVA_COUNT":"AvailableCount",
            "LOAN_RATE": "LoanRate",
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
        self.today_str = dt.datetime.now().strftime("%Y-%m-%d")
        self.req_file_name = 'output/{}_order_index.txt'.format(dt.datetime.now().strftime("%Y%m%d"))
        self.req_order_id = self.load_req_order_id()

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
        self.loan_df = self.dump_result(ret_json, "loan_list.csv")
        self.loan_df['Uid'] = self.loan_df[['Sid', 'ExchangeID']].apply(lambda x: x[0] + '-' + self.convert_exchange2local(x[1]) + '-stock', axis=1)

    def query_blacklist(self):
        url = self.config.get("ACCOUNT", "host") + "/eqd/public/get_eqd_blacklist_fast"
        head = {
            "Authorization": "Bearer " + self.auth_code,
        }
        res = requests.post(url=url, headers=head)
        ret_json = res.json()
        self.black_df = self.dump_result(ret_json, "blacklist.csv")

    def get_loan_rate(self, inst_id, exchange_id):
        uid = inst_id + '-' + self.convert_exchange2local(exchange_id) + '-stock'
        return self.loan_df.loc[self.loan_df['Uid'] == uid, 'LoanRate'].values[0]

    def dump_result(self, ret_json, csv_name):
        if ret_json["RET_CODE"] != 0:
            print("Request Error")
            return
        if ret_json["TOTAL_COUNT"] == 0:
            df = pd.DataFrame(colums=self.blacklist_cols) if 'black' in csv_name else pd.DataFrame(colums=self.loan_cols)
        else:
            df = pd.DataFrame(ret_json["RESULTSET"])

        df = df.rename(columns=self.blacklist_col_map) if 'black' in csv_name else df.rename(columns=self.loan_col_map)
        tmp_csv = csv_name + '.tmp'
        df.to_csv(tmp_csv, index=False)
        os.rename(tmp_csv, csv_name)
        return df

    def quota_order(self, single_order):
        print(single_order)
        return
        url = self.config.get("ACCOUNT", "host") + "/eqd/public/put_quota_set_order"
        head = {
            "USER_ID": self.config.get("ACCOUNT", "username"),
            "Authorization": "Bearer " + self.auth_code,
            "SYS_ID":"C",
            "STATION":"PC:172.0.0.1:00-00-00-00-00-00:00000000000000E0:zhang.xc:TF655AY91GHRVL:BFEBFBFF000306A9:C:FAT32:80"
        }
        data = {
            "ASSET_TYPE": "SPT_S",
            "CASH_ACCT_ID": self.config.get("ACCOUNT", "account_id"),
            "CCY_CODE": "CNY",
            "CONTRACT_ID": self.config.get("ACCOUNT", "contract_id"),
            "EVENT_TYPE": "50",
            "EXT_INFO": "NULL",
            "INST_CODE": single_order.inst_id,
            "LOAN_RATE": self.get_loan_rate(single_order.inst_id, single_order.exchange_id) * 100,
            "MARKET_TYPE": self.convert_exchange2zx(single_order.exchange_id),
            "ORDER_COUNT": single_order.order_volume,
            "REMARK": single_order.remark,
            "REQ_DATE": single_order.trade_date,
            "REQ_ID": self.get_next_req_order_id(),
            "REQ_TIME": single_order.trade_date,
            "SYS_ID": "0",
            "TRADE_DATE": single_order.trade_date,
            "TRADE_TYPE": "10"
        }
        res = requests.post(url=url, headers=head, json=data)
        return res

    def get_party_info(self):
        url = self.config.get("ACCOUNT", "host") + "/eqd/public/get_party_info"
        head = {
            "USER_ID": self.config.get("ACCOUNT", "username"),
            "Authorization": "Bearer " + self.auth_code,
        }
        res = requests.post(url=url, headers=head)
        print(res.text)

    def gen_order_list(self, origin_order_list):
        order_list = []
        for order in origin_order_list:
            single_order = SingleOrder()
            single_order.inst_id, single_order.exchange_id, _ = order["Uid"].split("-")
            single_order.order_volume = order["ReqLocateCount"]
            single_order.trade_date = order["TradeDate"]
            order_list.append(single_order)
        return order_list

    def insert_orders(self, origin_order_list):
        order_list = self.gen_order_list(origin_order_list)
        order_per_second = self.config.get("LIMIT", "order_per_second")
        total_round = len(order_list) / order_per_second + 1
        for idx in range(0, total_round):
            for order in order_list[idx*order_per_second:(idx+1)*order_per_second]:
                self.quota_order(order)
            time.sleep(1)
        self.dump_req_order_id()

    def query_orders(self):
        pass

    def load_req_order_id(self):
        if os.path.exists(self.req_file_name):
            with open(self.req_file_name, 'r') as f:
                req_order_id = int(f.read())
        else:
            req_order_id = int(dt.datetime.now().strftime("%Y%m%d")) * 1000000
        return req_order_id

    def dump_req_order_id(self):
        with open(self.req_file_name, 'w+') as f:
            f.write(self.req_order_id)

    def get_next_req_order_id(self):
        self.req_order_id = self.req_order_id + 1
        return self.req_order_id

    def convert_exchange2zx(self, exchange):
        if exchange == "SH":
            return "XSHG"
        return "XSHE"

    def convert_exchange2local(self, exchange):
        if exchange == "XSHG":
            return "SH"
        return "SZ"

def query():
    c = EQDClient()
    c.init()
    c.query_pool()
    c.get_party_info()
    orders = [
        {"Uid": "002142-SZ-stock", "ReqLocateCount": 2000, "TradeDate": "2023-08-18"},
        {"Uid": "601009-SH-stock", "ReqLocateCount": 2000, "TradeDate": "2023-08-18"},
        {"Uid": "300059-SZ-stock", "ReqLocateCount": 2000, "TradeDate": "2023-08-18"},
        {"Uid": "688608-SH-stock", "ReqLocateCount": 2000, "TradeDate": "2023-08-18"},
    ]
    c.insert_orders(orders)

if __name__ == '__main__':
    argh.dispatch_commands([query])
