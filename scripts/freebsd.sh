#!/bin/sh
pkg install -y python py39-pip py39-matplotlib vim
pip install -r ../requirements.txt

cat > /etc/rc.d/attendance << EOF
#!/bin/sh

# PROVIDE: attendance
# REQUIRE:
# KEYWORD: shutdown

. /etc/rc.subr

name=attendance
rcvar=attendance_enable

load_rc_config \$name

: ${attendance_enable="NO"}
: ${attendance_home_dir:="/root/Zkteco"}

pidfile="/var/run/\${name}.pid"
procname="python /root/Zkteco/app.py"
command=/usr/sbin/daemon
command_args="-f -p \${pidfile} -u attendance \${procname} --home=\${attendance_home_dir} --logfile=default"

run_rc_command "\$1"
EOF

chmod +x /etc/rc.d/attendance
service attendance start
