# coding:utf-8

import redis


class Config(object):
    """configuration information """
    SECRET_KEY = "finalProjectGYL123@"

    # database
    SQLALCHEMY_DATABASE_URI = "mysql://FinalProjectGLY:finalProject123%40@134.209.169.96:3306/FinalProjectGLY"
    # SQLALCHEMY_TRACK_MODIFICATIONS = True # trace the model automatically
    SQLALCHEMY_ECHO = True # print executed sql
    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask-session
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  
    PERMANENT_SESSION_LIFETIME = 86400  


class DevelopmentConfig(Config):
    """Configuration information for the development mode"""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration information"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}