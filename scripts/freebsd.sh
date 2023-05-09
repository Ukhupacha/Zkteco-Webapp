#!/bin/sh
pkg install -y python py39-pip py39-matplotlib vim
pip install -r ../requirements.txt

cat > /usr/local/etc/rc.d/attendance << EOF

#!/bin/sh

# PROVIDE: attendance
# REQUIRE: LOGIN
# KEYWORD: shutdown

. /etc/rc.subr

name=attendance
rcvar=\`set_rcvar\`

load_rc_config \$name

: \${attendance_enable="NO"}
: \${attendance_home_dir:="/root/Zkteco/"}

pidfile="/var/run/\${name}.pid"
attendance_user="root"
procname="python /root/Zkteco/app.py"
command=/usr/sbin/daemon
command_args="-c -f -P \${pidfile} -u \${attendance_user} -r \${procname} --home=\${attendance_home_dir} --logfile=default"

run_rc_command "\$1"

EOF

chmod +x /usr/local/etc/rc.d/attendance
service attendance enable
service attendance start
