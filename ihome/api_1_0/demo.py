# coding:utf-8

from . import api
from ihome import db, models
# import logging
from flask import current_app, request


@api.route("/index")
def index():
    #print("hello")
    # logging.error()   # record wrong message
    # logging.warn()   # warning
    # logging.info()   # inforamtion
    # logging.debug()   # test
    current_app.logger.error("error info")
    current_app.logger.warn("warn info")
    current_app.logger.info("info info")
    current_app.logger.debug("debug info")

    # request.cookies.get("csrf_token")
    # session.get
    return "index page"


# logging.basicConfig(level=logging.ERROR)



