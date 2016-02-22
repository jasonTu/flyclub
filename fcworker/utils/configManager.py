# coding: utf-8
"""Global configuration access module."""

import json

productConf = '/opt/mbk/conf/mbk.conf'
try:
    with open(productConf) as f:
        globalConfig = json.load(f)
except IOError:
    globalConfig = {}

brokerConfig = globalConfig.get('rabbitmqSettings', {})
broker = 'amqp://{user}:{password}@{ip}:{port}/{vhost}'.format(
    user=brokerConfig['user'],
    password=brokerConfig['password'],
    ip=brokerConfig['serverIP'],
    port=brokerConfig['sericePort'],
    vhost=brokerConfig['vhost']
)

workerSettings = globalConfig.get('workerSettings', {})
backuperConfig = workerSettings.get('backuper', {})
restorerConfig = workerSettings.get('restorer', {})

aliyunConfig = globalConfig.get('aliyunSettings', {})
ossConfig = aliyunConfig.get('OSS', {})
ossInternalConfig = aliyunConfig.get('OSS_Internal', {})
ossMbackupConfig = aliyunConfig.get('OSS_Mbackup', {})

apiServerConfig = globalConfig.get('apiServerSettings', {})
apiServer = 'http://{ip}:{port}/api'.format(
    ip=apiServerConfig.get('serverIP'),
    port=apiServerConfig.get('serverPort'),
)

cassandraConfig = globalConfig.get('cassandraSettings', {})

smsConfig = globalConfig.get('smsSettings', {})
