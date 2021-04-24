# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from ihome.models import Order,House
from ihome.models import User
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET

from ihome import constants, db
import os


@api.route("/orders/<int:order_id>/payment", methods=["GET"])
@login_required
def order_pay(order_id):
    """pay"""
    user_id = g.user_id
    mobile = ''
    # order status
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_PAYMENT").first()
        house = House.query.filter(House.id == order.house_id).first()
        user = User.query.filter(User.id == house.user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Database exception")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="data information error")

    if user is not None:
        mobile = user.mobile
    
    amount = order.amount


    

    pay_html = "http://127.0.0.1:5000/payComplete.html"
    return_info = "?order_id=" + str(order_id) + "&contact="+ mobile + "&amount=" + str(amount/100)
    pay_url = pay_html + return_info
    
    return jsonify(errno=RET.OK, errmsg="OK",data={"pay_url" : pay_url})

@api.route("/order/payment", methods=["PUT"])
def save_order_payment_result():
    """the result of payment"""
    pay_dict = request.form.to_dict()

    
    order_id = pay_dict.get("order_id")
   
    try:
        Order.query.filter_by(id=order_id).update({"status": "WAIT_COMMENT"})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK")








