#! /bin/bash
# fcserver script
# it is v.0.1 version

ROOT=/opt/flyclub
PS_CMD="/bin/ps -ef"
NGINX_MGR=/opt/flyclub/scripts/nginx.sh
SUPERVISORD_PID=/opt/flyclub/run/supervisord.pid
SUPERVISORD=/opt/flyclub/env/bin/supervisord
SUPERVISORD_CONF=/opt/flyclub/conf/supervisord-server.conf
SUPERVISORCTL_CMD=/opt/flyclub/env/bin/supervisorctl
SCRIPTNAME=/opt/flyclub/scripts/fcserver.sh

do_start() {
  $SUPERVISORD -c $SUPERVISORD_CONF
  $NGINX_MGR start
  echo "Start fcserver service [OK]"
}

wait_supervisor_stop()
{
    cnt=0
    while [[ `$PS_CMD | grep -w $SUPERVISORD_CONF | grep -v grep` != "" ]]; do
        sleep 1
        let cnt+=1
        if [[ $cnt -gt 30 ]]; then
            break
        fi
    done
}

stop_supervisor()
{
    for i in `$PS_CMD | grep -w $SUPERVISORD_CONF | grep -v grep | awk '{ print $2 }'`
    do
        /bin/kill $i > /dev/null 2>&1
    done
    wait_supervisor_stop
}

do_stop() {
  stop_supervisor
  $NGINX_MGR stop
  echo "Stop fcserver service [OK]"
}

do_reload() {
  if [ -f $SUPERVISORD_PID ]; then
    $SUPERVISORCTL_CMD -c $SUPERVISORD_CONF reload
  else
    echo "Supervisord and uwsgi is not running!"
    $SUPERVISORD -c $SUPERVISORD_CONF
    echo "Reload supervisord [OK]"
  fi
  $NGINX_MGR reload
  echo "Reload fcserver service [OK]"
}

case "$1" in
   start)
     do_start
     ;;
   stop)
     do_stop
     ;;
   reload)
     do_reload
     ;;
   restart)
     do_stop
     do_start
     ;;
   *)
     echo "Usage: $SCRIPTNAME {start|stop|restart|reload}" >&2
     ;;
esac
