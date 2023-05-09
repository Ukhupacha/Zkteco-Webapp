#!/bin/sh
pkg install -y python py39-pip py39-matplotlib vim sysutils/py-supervisor
pip install -r ../requirements.txt
# possibility 2:
echo "
[program:attendance]
command=/root/Zkteco/app.py
directory=/root/Zkteco
autostart=true
" >> /usr/local/etc/supervisord.conf
service supervisord enable
service supervisord start
