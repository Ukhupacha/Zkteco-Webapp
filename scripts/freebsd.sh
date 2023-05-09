#!/bin/sh
pkg install -y python py39-pip py39-matplotlib vim
pip install -r ../requirements.txt

cat > /usr/local/etc/rc.d/attendance << EOF

#!/bin/sh

# PROVIDE: attendance
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name=attendance
rcvar=attendance_enable

load_rc_config \$name

: \${attendance_enable="NO"}


pidfile="/var/run/\${name}.pid"
command="/root/Zkteco/app.py"
command_interpreter=/usr/local/bin/python
run_rc_command "\$1"
EOF

chmod +x /usr/local/etc/rc.d/attendance
service attendance start
