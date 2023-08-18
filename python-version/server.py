from flask import Flask
from flask_apscheduler import APScheduler
from flask import request, make_response

from eqd_client import EQDClient

app = Flask(__name__)
client = EQDClient()
client.init()
client.get_party_info()
scheduler = APScheduler()
scheduler.init_app(app)

@app.route('/insert_orders', methods=['POST'])
def insert_orders():
    req_json = request.json
    client.update_target_pos(req_json["orders"])
    return {"return_code": 0}

@scheduler.task('interval', id='do_insert_orders', seconds=10, misfire_grace_time=900)
def do_insert_orders():
    client.insert_orders()
    client.query_orders()

if __name__ == '__main__':
    scheduler.start()
    app.run(host='0.0.0.0', port=10000)
