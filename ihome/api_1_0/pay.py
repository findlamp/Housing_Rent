# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from ihome.models import Order,House
from ihome.models import User
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
#from alipay import AliPay
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


    '''     
    # creat object
    alipay_client = AliPay(
        appid="2016081600258081",
        app_notify_url=None,  # return url
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),  # private key
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),  # public key
        sign_type="RSA2",  # RSA or RSA2
        debug=True  # False
    )

    # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount/100.0),   # 总金额
        subject=u"爱家租房 %s" % order.id,  # 订单标题
        return_url="http://127.0.0.1:5000/payComplete.html",  # 返回的连接地址
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 构建让用户跳转的支付连接地址
    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    '''

    #info = "contact : " + mobile + "\n"  +"amount : " + str(amount/100)
    pay_html = "http://127.0.0.1:5000/payComplete.html"
    return_info = "?order_id=" + str(order_id) + "&contact="+ mobile + "&amount=" + str(amount/100)
    pay_url = pay_html + return_info
    #return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url": pay_url})
    return jsonify(errno=RET.OK, errmsg="OK",data={"pay_url" : pay_url})

@api.route("/order/payment", methods=["PUT"])
def save_order_payment_result():
    """保存订单支付结果"""
    pay_dict = request.form.to_dict()

    # 对支付宝的数据进行分离  提取出支付宝的签名参数sign 和剩下的其他数据
    #alipay_sign = alipay_dict.pop("sign")

    '''
    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2016081600258081",
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),  # 私钥
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # 借助工具验证参数的合法性
    # 如果确定参数是支付宝的，返回True，否则返回false
    result = alipay_client.verify(alipay_dict, alipay_sign)
    '''
    #if result:
        # 修改数据库的订单状态信息
    order_id = pay_dict.get("order_id")
    #trade_no = alipay_dict.get("trade_no")  # 支付宝的交易号
    try:
        Order.query.filter_by(id=order_id).update({"status": "WAIT_COMMENT"})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK")








