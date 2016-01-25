#! /bin/bash
# nginx script
# it is v.0.1 version

ROOT=/opt/flyclub
NGINX=/opt/flyclub/3rdParty/nginx-openresty/nginx/sbin/nginx
NGINX_CONF=$ROOT/conf/nginx.conf
PID_FILE=$ROOT/run/nginx.pid
PROG=$(basename $NGINX)
LOCK_FILE=/opt/flyclub/run/nginx.lockfile
SCRIPTNAME=/opt/flyclub/scripts/nginx.sh

do_start() {
  $NGINX -c $NGINX_CONF
  echo "Start nginx service [OK]"
}

do_stop() {
  if [ -f $PID_FILE ]; then
    kill `cat $PID_FILE`
    echo "Stop nginx service [OK]"
  else
    echo "Nginx service is not running!"
  fi
}
 
do_reload() {
  if [ -f $PID_FILE ]; then
    kill -HUP `cat $PID_FILE`
    echo "Reload nginx service [OK]"
  else
    echo "Nginx service is not running!"
    do_start
  fi
}

case "$1" in
   start)
     do_start
     ;;
   stop)
     do_stop
     ;;
   restart)
     do_stop
     do_start
     ;;
   reload)
     do_reload
     ;;
   *)
     echo "Usage: $SCRIPTNAME {start|stop|restart|reload}" >&2
     ;;
esac
