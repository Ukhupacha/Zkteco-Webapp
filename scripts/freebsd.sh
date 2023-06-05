#!/bin/sh
pkg install -y python py39-pip py39-matplotlib vim sysutils/py-supervisor
pip install -r ../requirements.txt
# possibility 2:
echo "
[program:attendance]
command=/root/Zkteco-Webapp/app.py
directory=/root/Zkteco-Webapp
autostart=true
" >> /usr/local/etc/supervisord.conf
service supervisord enable
service supervisord start
