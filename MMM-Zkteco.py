#!/usr/local/bin/python3
import sys
import json
from zk import ZK
from datetime import datetime, date
sys.path.append("zk")


def to_node(message):
    try:
        print(json.dumps(message))
    except Exception:
        pass
    sys.stdout.flush()


if __name__ == "__main__":
    zk = ZK('zkteco.intranet', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
    zk.connect()
    zk.disable_device()
    users = zk.get_users()
    user_list = {}
    for user in users:
        user_list[int(user.user_id)] = user.name

    today = date.today()
    today = datetime(today.year, today.month, today.day)
    attendance = zk.get_user_history(list(user_list.keys()), start_date=today, end_date=None)
    final_dict = {}
    for key, values in attendance.items():
        final_dict[user_list[int(key)]] = [value[0].strftime("%H:%M:%S") for value in values]

    zk.enable_device()
    zk.disconnect()
    to_node(final_dict)

