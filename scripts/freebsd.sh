#!/bin/sh
pkg install -y python py39-pip py39-matplotlib vim
pip install -r ../requirements.txt

cat > /etc/rc.d/attendance << EOF
#!/bin/sh
#
# PROVIDE: attendance
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name=attendance
rcvar=attendance_enable

command="/root/Zkteco/python app.py"

load_rc_config \$name

#
# DO NOT CHANGE THESE DEFAULT VALUES HERE
# SET THEM IN THE /etc/rc.conf FILE
#
attendance_enable=\${attendance_enable-"NO"}
pidfile=\${attendance_pidfile-"/var/run/attendance.pid"}

run_rc_command "\$1"
EOF

chmod +x /etc/rc.d/attendance
service attendance start
