# -*-coding:utf-8-*-

""" 队列配置 """
rabbitmq = {
    'connector':'Amqp',
    'expire':60,
    'default':'default',
    'host':'172.16.1.196',
    'username':'admin',
    'password':'welcome@rbmq',
    'port':5672,
    'vhost':'/',
    'select':0,
    'timeout':0,
    'persistent':False,
}