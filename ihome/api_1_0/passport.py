# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db, constants
from ihome.models import User
from sqlalchemy.exc import IntegrityError
import re


@api.route("/users", methods=["POST"])
def register():
    """signup
    """
    # Gets the requested JSON data and returns the dictionary
    req_dict = request.get_json()

    mobile = req_dict.get("mobile")
    #sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # Calibration parameters
    #if not all([mobile, sms_code, password, password2]):
        #return jsonify(errno=RET.PARAMERR, errmsg="Parameter Incomplete")
    if  not all([mobile, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter Incomplete")
    # Determine the format of the phone number
    
    if not re.match(r"1[34578]\d{9}", mobile):
        # wrong format
        return jsonify(errno=RET.PARAMERR, errmsg="The format of mobile phone number is wrong")
    

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="The two passwords don't match")


    # Save the user's registration data to the database
    user = User(name=mobile, mobile=mobile)
    # user.generate_password_hash(password)

    user.password = password  # set attributes

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # A rollback after a database operation error
        db.session.rollback()
        # It indicates that the phone number has a duplicate value
        #  the phone number has been registered
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="existent phone number")
    except Exception as e:
        db.session.rollback()
        # It indicates that the phone number has a duplicate value,
        # the phone number has been registered
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Query Database Exception")

    # Save the login state to the session
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # reture result
    return jsonify(errno=RET.OK, errmsg="registered successfully ")


@api.route("/sessions", methods=["POST"])
def login():
    """login
    """
    # get parameters
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # check parameters
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter Incomplete")

    # phone number format
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="The format of mobile phone number is wrong")

    # Determine if the number of errors exceeded the limit
    user_ip = request.remote_addr  # ip address
    try:
        access_nums = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="Too many errors, please try again later")

    # Query the user's data object from the database based on the phone number
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Failed to obtain user information")

    # Use the database password and the user to fill in the password for comparison verification
    if user is None or not user.check_password(password):
        #If validation fails, log the number of errors and return a message
        try:
            # Redis incr can add one to string numeric data
            #  initializing it to 1 if the data does not exist to begin with
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="Incorrect user name or password")

    # If the validation is equally successful, save the login status in the session
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="login successfully")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登陆状态"""
    # 尝试从session中获取用户的名字
    name = session.get("name")
    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    # 清除session数据
    csrf_token = session.get("csrf_token")
    session.clear()
    session["csrf_token"] = csrf_token
    return jsonify(errno=RET.OK, errmsg="OK")


