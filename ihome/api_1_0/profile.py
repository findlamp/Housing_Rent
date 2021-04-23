# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from flask import g, current_app, jsonify, request, session
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import db, constants
import os
import uuid

@api.route("/users/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    """user_id
    """
    # The user_id is already stored in the G object in the decorator code
    # so it can be read directly from the view
    user_id = g.user_id

    # get picture
    image_file = request.files.get("avatar")

    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg="Image not uploaded")


    # Call Qiniu upload pictures, return the file name TODO to local storage
    try:
        # Get the UUID from the timestamp
        file_name = str(uuid.uuid1())+'.png'
        basedir = os.getcwd()
        image_path = os.path.join(basedir,'ihome','static','images',file_name)
        image_file.save(image_path)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="Image upload failed")

    # Save the file name to the database
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Failed to save image information")

    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    # save successfully 
    return jsonify(errno=RET.OK, errmsg="save successfully ", data={"avatar_url": avatar_url})


@api.route("/users/name", methods=["PUT"])
@login_required
def change_user_name():
    """change username"""
    # With the login_required decorator, you can get the user user_id from the g object
    user_id = g.user_id

    # Gets the user name that the user wants to set
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="Parameter Incomplete")

    name = req_data.get("name")  # set name
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="Names cannot be empty")

    # Save the user nickname name and determine if the name is duplicated (using the unique index of the database)
    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="Set user error")

    # Modify the name field in the session data
    session["name"] = name
    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})


@api.route("/user", methods=["GET"])
@login_required
def get_user_profile():
    """get user information"""
    user_id = g.user_id
    # query database to get user information
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Failed to obtain user information")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="invalid operation")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@api.route("/users/auth", methods=["GET"])
@login_required
def get_user_auth():
    """Get the user's real-name authentication information"""
    user_id = g.user_id

    # query informaiton in the database
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Failed to obtain user real name information")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="invalid operation")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())


@api.route("/users/auth", methods=["POST"])
@login_required
def set_user_auth():
    """Save real-name authentication information"""
    user_id = g.user_id

    # get parameters 
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="wrong parameters ")

    real_name = req_data.get("real_name")  # real name
    id_card = req_data.get("id_card")  # id number

    # Parameter calibration
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # Save the user's name and ID number
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None)\
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="Failed to save user real name information")

    return jsonify(errno=RET.OK, errmsg="OK")

