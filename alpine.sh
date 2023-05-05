#!/bin/sh
apk add --update git python3 python3-dev vim make automake gcc g++ subversion
python3 -m ensurepip
pip3 install -r requirements.txt
cp attendance /etc/init.d/
rc-update add attendance
rc-service attendace start