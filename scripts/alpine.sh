#!/bin/sh
apk add --update git python3 python3-dev vim make automake gcc g++ subversion
python3 -m ensurepip
pip3 install -r ../requirements.txt
cact >  /etc/init.d/attendance << EOF
#!/sbin/openrc-run
# Copyright 2021 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

name="attendance"
description="Attendance zkteco"
command="/root/Zkteco/app.py"
pidfile="/run/\${RC_SVCNAME}.pid"
command_background=true
EOF
chmod +x /etc/init.d/attendance
rc-update add attendance
rc-service attendance start