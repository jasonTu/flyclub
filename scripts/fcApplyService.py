# coding: utf-8
"""FlyClub apply service for roles."""


import os
import sys
import json


productConf = '/opt/flyclub/conf/flyclub.conf'
roleFile = '/tmp/.fc.role'
try:
    with open(productConf) as fp:
        CONFIG = json.load(fp)
except:
    # use the default config
    CONFIG = {}


def usage():
    print 'python fcApplyService.py usage'
    print 'python fcApplyService.py start|stop|restart|reload'
    print 'python fcApplyService.py setrole fcserver|fcworker'
    print 'python fcApplyService.py addrole fcserver|fcworker'


def setrole(role):
    cmd = '> %s' %roleFile
    os.system(cmd)
    CONFIG['currentRoles'] = []
    CONFIG['currentRoles'].append(role)
    with open(productConf, 'w+') as fp:
        json.dump(CONFIG, fp, indent=4)


def addrole(role):
    cmd = 'touch %s' %roleFile
    os.system(cmd)
    try:
        fp = open(roleFile)
        rolesInfo = json.load(fp)
    except:
        fp.close()
        rolesInfo = {}
        rolesInfo['roles'] = []

    if role in rolesInfo['roles']:
        print 'role already added'
    else:
        rolesInfo['roles'].append(role)
        with open(roleFile, 'w+') as fp:
            json.dump(rolesInfo, fp, indent=4)
    # update flyclub conf
    with open(productConf, 'w+') as fp:
        print rolesInfo['roles']
        CONFIG['currentRoles'] = rolesInfo['roles']
        json.dump(CONFIG, fp, indent=4)


def applyService(cmd):
    roles = CONFIG['currentRoles']
    if not roles:
        print 'Check the role config!'
        return
    for item in roles:
        runcmd = CONFIG['roles'][item][cmd]
        print '----------Role: %s----------' %item
        os.system(runcmd)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print usage()
        sys.exit(1)

    if sys.argv[1] == 'setrole':
        if (sys.argv) <= 2:
            print usage()
        else:
            setrole(sys.argv[2])
    elif sys.argv[1] == 'addrole':
        if (sys.argv) <= 2:
            print usage()
        else:
            addrole(sys.argv[2])
    elif sys.argv[1] == 'usage':
        print usage()
    elif sys.argv[1] == 'start':
        applyService('start')
    elif sys.argv[1] == 'stop':
        applyService('stop')
    elif sys.argv[1] == 'restart':
        applyService('restart')
    elif sys.argv[1] == 'reload':
        applyService('reload')
    else:
        print usage()
