# coding:utf-8

import datetime

from flask import request, g, jsonify, current_app
from ihome import db, redis_store
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET
from ihome.models import House, Order
from . import api


@api.route("/orders", methods=["POST"])
@login_required
def save_order():
    """preserve order"""
    user_id = g.user_id

    # get parameters 
    order_data = request.get_json()
    if not order_data:
        return jsonify(errno=RET.PARAMERR, errmsg="wrong parameters")

    house_id = order_data.get("house_id")  # house id
    start_date_str = order_data.get("start_date")  # checkin
    end_date_str = order_data.get("end_date")  # checkout

    # parameter testing
    if not all((house_id, start_date_str, end_date_str)):
        return jsonify(errno=RET.PARAMERR, errmsg="wrong parameters")

    # Date format check
    try:
        # Converts the requested time parameter string to the datetime type
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        assert start_date <= end_date
        # Count the number of days booked
        days = (end_date - start_date).days + 1  # datetime.timedelta
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="Date format error")

    # Inquire if the house exists
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Failed to query if the house exists")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="unexistent house")

    # Whether the house booked is the landlord's own
    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="You can't book your own house")

    # Make sure the house has not been ordered by someone else 
    # during the time the user booked it
    try:
        # Query the number of orders for time conflicts
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date,
                                   Order.end_date >= start_date).count()
        #  select count(*) from order where ....
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Check for error. Please try again later")
    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="The house has been booked")

    # price
    amount = days * house.price

    # preserve order
    order = Order(
        house_id=house_id,
        user_id=user_id,
        begin_date=start_date,
        end_date=end_date,
        days=days,
        house_price=house.price,
        amount=amount
    )
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存订单失败")
    return jsonify(errno=RET.OK, errmsg="OK", data={"order_id": order.id})


# /api/v1.0/user/orders?role=custom     role=landlord
@api.route("/user/orders", methods=["GET"])
@login_required
def get_user_orders():
    """查询用户的订单信息"""
    user_id = g.user_id

    # The identity of the user, the user wants to query as tenants booking the order of the house,
    # others still want a query as a landlord others booked their orders of the house
    role = request.args.get("role", "")

    # query order information
    try:
        if "landlord" == role:
            # Query the order as the landlord
            # Inquire what the house that belongs to oneself has first
            houses = House.query.filter(House.user_id == user_id).all()
            houses_ids = [house.id for house in houses]
            # Then check the booking order for your own house
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).order_by(Order.create_time.desc()).all()
        else:
            #To query the order as a tenant, to query the order booked by yourself
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Failed to query order information")

    # Converts the order object to dictionary data
    orders_dict_list = []
    if orders:
        for order in orders:
            orders_dict_list.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data={"orders": orders_dict_list})


@api.route("/orders/<int:order_id>/status", methods=["PUT"])
@login_required
def accept_reject_order(order_id):
    """accept deny"""
    user_id = g.user_id

    # get parameters
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="wrong parameters")

    # The action parameter indicates whether the client is requesting an action to accept or reject an order
    action = req_data.get("action")
    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="wrong parameters")

    try:
        # Query the order based on the order number and ask the order to be in the waiting state
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="The order data could not be obtained")

    # Make sure landlords can only modify orders for their own homes
    if not order or house.user_id != user_id:
        return jsonify(errno=RET.REQERR, errmsg="The operation is invalid")

    if action == "accept":
        # Accept the order and set the order status to wait for comments
        order.status = "WAIT_PAYMENT"
    elif action == "reject":
        # Reject the order, requiring the user to convey the reason for the rejection
        reason = req_data.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="wrong parameters")
        order.status = "REJECTED"
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="operation failure")

    return jsonify(errno=RET.OK, errmsg="OK")


@api.route("/orders/<int:order_id>/comment", methods=["PUT"])
@login_required
def save_order_comment(order_id):
    """preserve conmment"""
    user_id = g.user_id
    # preserve parameters
    req_data = request.get_json()
    comment = req_data.get("comment")  # comment

    # check parameters
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg="wrong parameters")

    try:
        # 需要确保只能评论自己下的订单，而且订单处于待评价状态才可以
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_COMMENT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="The order data could not be obtained")

    if not order:
        return jsonify(errno=RET.REQERR, errmsg="invalid operation")

    try:
        # Set the status of the order to completed
        order.status = "COMPLETE"
        # Save the evaluation information of the order
        order.comment = comment
        # Increase the completed order number of the house by 1
        house.order_count += 1
        db.session.add(order)
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="operation failure")

    # Because the house details have the evaluation information of the order
    # so that the latest evaluation information can be displayed in the house details 
    # the detail cache of this order house in Redis is deleted
    try:
        redis_store.delete("house_info_%s" % order.house.id)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="OK")
