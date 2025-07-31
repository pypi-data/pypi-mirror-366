# -*-coding:utf-8-*-

""" 队列配置 """
rabbitmq = {
    'connector':'Amqp',
    'expire':60,
    'default':'default',
    'host':'183.62.164.205',
    'username':'admin',
    'password':'tpass@rbmq',
    'port':5672,
    'vhost':'/',
    'select':0,
    'timeout':0,
    'persistent':False,
}