# coding:utf-8

from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect

import redis
import logging
from logging.handlers import RotatingFileHandler
from ihome.utils.commons import ReConverter

#initialized database
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# database
db = SQLAlchemy()

# Create a Redis connection object
redis_store = None

# Configuration log information
# Sets the logging level of the log
logging.basicConfig(level=logging.INFO)
# Creates a logger that specifies the path to save the log, the maximum size of each log file
#  and the upper limit on the number of log files saved
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# Creates a format log level for logging records
# Enter the file name of the log message
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# Set the logging format for the logger you just created
file_log_handler.setFormatter(formatter)
# Add a day logger to the global logging tool object used by the Flask app
logging.getLogger().addHandler(file_log_handler)


# factory pattern
def create_app(config_name):
    """
    Create FLASK's application object
    :param config_name: str  The name of the pattern that configures the pattern （"develop",  "product"）
    :return:
    """
    app = Flask(__name__)

    # The class that gets the configuration parameters based on the name of the configuration pattern
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # Initialize DB with app
    db.init_app(app)

    
    # Initialize redis
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # Use flask-session to save session data to Redis
    Session(app)

    # Add CSRF protection to flask
    CSRFProtect(app)

    # Add a custom converter for the flask
    app.url_map.converters["re"] = ReConverter

    # Registered blueprint
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    # Register blueprints that provide static file
    from ihome import web_html
    app.register_blueprint(web_html.html)

    return app