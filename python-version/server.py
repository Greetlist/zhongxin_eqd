import pandas as pd
from flask import Flask
from flask_apscheduler import APScheduler
from flask import request, make_response
import configparser

from eqd_client import EQDClient

config = configparser.ConfigParser()
config.read("conf/account.ini")

app = Flask(__name__)
client = EQDClient()
client.get_party_info()
scheduler = APScheduler()
scheduler.init_app(app)
#rpc_client = 

@app.route('/insert_orders', methods=['POST'])
def insert_orders():
    req_json = request.json
    if req_json.get("book", "") != config.get("BOOK", "name"):
        return {"return_code": 1, "msg": "Book is not match"}
    client.update_target_pos(req_json["orders"])
    return {"return_code": 0, "msg": "Success"}

@app.route('/query_init', methods=['POST'])
def query_init():
    client.query_init()

@app.route('/get_current_status', methods=['POST'])
def get_current_status():
    pass
    #return_df = client.target_pos_df[""]
    #rpc_client().return_res(return_df)

@app.route('/query_loan', methods=['POST'])
def query_loan():
    retry_count = 5
    while True:
        res = client.query_pool()
        if res is not None:
            break
        time.sleep(2)
        retry_count -= 1
        if retry_count <= 0:
            break

@scheduler.task('interval', id='do_insert_orders', seconds=2, misfire_grace_time=900)
def do_insert_orders():
    client.insert_orders()
    client.query_orders()
    #return_df = client.target_pos_df[""]
    #rpc_client().return_res(return_df)

if __name__ == '__main__':
    scheduler.start()
    app.run(host='0.0.0.0', port=10000)
