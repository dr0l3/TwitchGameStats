#!/bin/sh
# start-cron.sh

rsyslogd
cron -f
touch /var/log/cron.log
