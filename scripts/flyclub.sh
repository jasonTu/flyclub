#!/bin/bash
#
# flyclub - this script starts and stops the fc server or/and worker
#
# chkconfig:   - 85 15
# description:  mbackup server


PS_CMD="/bin/ps -ef"

VIRTUAL_ENV=/opt/flyclub/env
WORK_SCRIPT=/opt/flyclub/scripts/fcApplyService.py

PYTHON=$VIRTUAL_ENV/bin/python

start()
{
    $PYTHON $WORK_SCRIPT start
}

stop()
{
    $PYTHON $WORK_SCRIPT stop
}

reload()
{
    $PYTHON $WORK_SCRIPT reload
}

case "$1" in
'start')
    start
    ;;

'stop')
    stop
    ;;

'reload')
    reload
    ;;

'restart')
    stop
    start
    ;;

*)
    echo "usage: $0 start|stop|reload|restart"
    exit 1
    ;;
esac
