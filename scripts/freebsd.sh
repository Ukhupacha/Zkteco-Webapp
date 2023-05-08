#!/bin/sh
pkg install -y python py39-pip py39-matplotlib vim
pip install -r ../requirements.txt

cat > /etc/rc.d/attendance << EOF
#!/bin/sh

. /etc/rc.subr

name=attendance
rcvar=attendance_enable

command="/usr/sbin/\${name}"

load_rc_config \$name
run_rc_command "\$1"
EOF

chmod +x /etc/rc.d/attendance
service attendance start
