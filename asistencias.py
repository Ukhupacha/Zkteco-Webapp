# -*- coding: utf-8 -*-
import sys
import os
import argparse
sys.path.append("zk")
from zk import ZK
from os.path import abspath, expanduser
from utils import getusers, configfile, getgroupandpay, filterdate, attendance2dict, countdays, createpdf

conn = None
parser = argparse.ArgumentParser(description='ZK Basic Reading Tests')
parser.add_argument('-a', '--address',
                    help='ZK device Address [zkteco.intranet]', default='zkteco.intranet')
parser.add_argument('-p', '--port', type=int,
                    help='ZK device port [4370]', default=4370)
parser.add_argument('-T', '--timeout', type=int,
                    help='Default [10] seconds (0: disable timeout)', default=10)
parser.add_argument('-P', '--password', type=int,
                    help='Device code/password', default=0)
parser.add_argument('-f', '--force-udp', action="store_true",
                    help='Force UDP communication')
parser.add_argument('-v', '--verbose', action="store_true",
                    help='Print debug information')
parser.add_argument('-u', '--updatetime', action="store_true",
                    help='Update Date/Time')

args = parser.parse_args()


zk = ZK(args.address, port=args.port, timeout=args.timeout, password=args.password,
        force_udp=args.force_udp, verbose=args.verbose)

try:

    # Return List of Users and ZK Connection
    userList, conn = getusers(zk)

    # Configuration file
    pathFile = abspath(expanduser("~/.config/zkteco/config.ini"))
    config = configfile(pathFile)

    # Filter by user/group
    users, payment = getgroupandpay(userList, config)

    # Filter by date input
    history = filterdate(zk, users)


    # Attendance to dict by date
    employees = attendance2dict(history)

    # Count worked days and error days and payment
    worked = countdays(employees, payment)

    # Create PDF file
    createpdf(employees, worked, userList)

    # Bye
    print("Verificar documento y cerrar esta ventana\n")



except Exception as e:
    print ("Process terminate : {}".format(e))
finally:
    if conn:
        conn.disconnect()
