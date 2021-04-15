# coding:utf-8

import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = "finalProjectGYL123@"

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://FinalProjectGLY:finalProject123%40@134.209.169.96:3306/FinalProjectGLY"
    # SQLALCHEMY_TRACK_MODIFICATIONS = True # trace the model automatically
    SQLALCHEMY_ECHO = True # print executed sql
    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期，单位秒


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}