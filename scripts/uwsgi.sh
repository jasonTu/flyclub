#! /bin/bash
# uwsgi script
# it is v.0.1 version

ROOT=/opt/flyclub
UWSGI_CONF=$ROOT/conf/uwsgi.ini
UWSGI_PN=`ps aux|grep -v "grep"|grep -c "uwsgi"`
UWSGI_PID=`ps -eo pid,comm|grep uwsgi|sed -n 1p|awk '{print $1}'`
UWSGI_PID_FILE=/opt/flyclub/run/nginx.pid
UWSGI=/root/pyenvs/mbackup/bin/uwsgi
WAITTIME=3

if [ ! -n "$1" ]
then
  echo "Usages: bash uwsgi.sh [start|stop|restart]"
fi

if [ $1 = start ]
then
  pn=$UWSGI_PN
  if [ $pn -gt 2 ]
  then
    echo "uwsgi is running!"
    exit 0
  else
    $UWSGI --ini $UWSGI_CONF
    echo "Start uwsgi service [OK]"
  fi
elif [ $1 = stop ]; then
  killall -9 uwsgi
  rm -rf $UWSGI_PID_FILE
  echo "Stop uwsgi service [OK]"
elif [ $1 = restart ]; then
  killall -9 uwsgi
  rm -rf $UWSGI_PID_FILE
  echo "Stop uwsgi service [OK]"
  sleep $WAITTIME
  $UWSGI --ini $UWSGI_CONF
  echo "Restart uwsgi service [OK]"
else
  echo "Usages: bash uwsgi.sh [start|stop|restart]"
fi 
