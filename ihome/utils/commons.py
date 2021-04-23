# coding:utf-8

from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import RET
import functools


# Defining a canonical converter
class ReConverter(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        # Invokes the parent class's initialization method
        super(ReConverter, self).__init__(url_map)
        # Save a canonical converter
        self.regex = regex


# Decorator that validates login status defined
def login_required(view_func):
    # The Wraps function sets the property of the function inside the wrapper to the property of the decorated function view_func
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # Determine the login status of the user
        user_id = session.get("user_id")

        # If user login
        if user_id is not None:
            #Save the user_id to the G object, which can be used to retrieve the saved data in the view function
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # If user didn't login
            return jsonify(errno=RET.SESSIONERR, errmsg="User didn't login.")

    return wrapper




# @login_required
# def set_user_avatar():
#     # user_id = session.get("user_id")
#     user_id = g.user_id
#     return json  ""
#
#
# set_user_avatar()  -> wrapper()