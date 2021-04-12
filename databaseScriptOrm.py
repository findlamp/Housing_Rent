# 数据库自动化脚本

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib import parse
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, Column,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import *
from werkzeug.security import generate_password_hash, check_password_hash
from ihome import constants
# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = Column(DateTime, default=datetime.now)  # 记录的创建时间
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel,Base):
    """用户"""

    __tablename__ = "ih_user_profile"

    id = Column(Integer, primary_key=True)  # 用户编号
    name = Column(String(32), unique=True, nullable=False)  # 用户暱称
    password_hash = Column(String(128), nullable=False)  # 加密的密码
    mobile = Column(String(11), unique=True, nullable=False)  # 手机号
    real_name = Column(String(32))  # 真实姓名
    id_card = Column(String(20))  # 身份证号
    avatar_url = Column(String(128))  # 用户头像路径
    houses = relationship("House", backref="user")  # 用户发布的房屋
    orders = relationship("Order", backref="user")  # 用户下的订单

    # 加上property装饰器后，会把函数变为属性，属性名即为函数名
    @property
    def password(self):
        """读取属性的函数行为"""
        # print(user.password)  # 读取属性时被调用
        # 函数的返回值会作为属性值
        # return "xxxx"
        raise AttributeError("这个属性只能设置，不能读取")

    # 使用这个装饰器, 对应设置属性操作
    @password.setter
    def password(self, value):
        """
        设置属性  user.passord = "xxxxx"
        :param value: 设置属性时的数据 value就是"xxxxx", 原始的明文密码
        :return:
        """
        self.password_hash = generate_password_hash(value)

    # def generate_password_hash(self, origin_password):
    #     """对密码进行加密"""
    #     self.password_hash = generate_password_hash(origin_password)

    def check_password(self, passwd):
        """
        检验密码的正确性
        :param passwd:  用户登录时填写的原始密码
        :return: 如果正确，返回True， 否则返回False
        """
        return check_password_hash(self.password_hash, passwd)

    def to_dict(self):
        """将对象转换为字典数据"""
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar": constants.QINIU_URL_DOMAIN + self.avatar_url if self.avatar_url else "",
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict

    def auth_to_dict(self):
        """将实名信息转换为字典数据"""
        auth_dict = {
            "user_id": self.id,
            "real_name": self.real_name,
            "id_card": self.id_card
        }
        return auth_dict


class Area(BaseModel,Base):
    """城区"""

    __tablename__ = "ih_area_info"

    id = Column(Integer, primary_key=True)  # 区域编号
    name = Column(String(32), nullable=False)  # 区域名字
    houses = relationship("House", backref="area")  # 区域的房屋

    def to_dict(self):
        """将对象转换为字典"""
        d = {
            "aid": self.id,
            "aname": self.name
        }
        return d


# 房屋设施表，建立房屋与设施的多对多关系
house_facility = Table(
    "ih_house_facility",
    Base.metadata,
    Column("house_id", Integer, ForeignKey("ih_house_info.id"), primary_key=True),  # 房屋编号
    Column("facility_id", Integer, ForeignKey("ih_facility_info.id"), primary_key=True)  # 设施编号
)


class House(BaseModel,Base):
    """房屋信息"""

    __tablename__ = "ih_house_info"

    id = Column(Integer, primary_key=True)  # 房屋编号
    user_id = Column(Integer, ForeignKey("ih_user_profile.id"), nullable=False)  # 房屋主人的用户编号
    area_id = Column(Integer, ForeignKey("ih_area_info.id"), nullable=False)  # 归属地的区域编号
    title = Column(String(64), nullable=False)  # 标题
    price = Column(Integer, default=0)  # 单价，单位：分
    address = Column(String(512), default="")  # 地址
    room_count = Column(Integer, default=1)  # 房间数目
    acreage = Column(Integer, default=0)  # 房屋面积
    unit = Column(String(32), default="")  # 房屋单元， 如几室几厅
    capacity = Column(Integer, default=1)  # 房屋容纳的人数
    beds = Column(String(64), default="")  # 房屋床铺的配置
    deposit = Column(Integer, default=0)  # 房屋押金
    min_days = Column(Integer, default=1)  # 最少入住天数
    max_days = Column(Integer, default=0)  # 最多入住天数，0表示不限制
    order_count = Column(Integer, default=0)  # 预订完成的该房屋的订单数
    index_image_url = Column(String(256), default="")  # 房屋主图片的路径
    facilities = relationship("Facility", secondary=house_facility)  # 房屋的家具
    images = relationship("HouseImage")  # 房屋的图片
    orders = relationship("Order", backref="house")  # 房屋的订单



class Facility(BaseModel,Base):
    "家具信息"

    __tablename__ = "ih_facility_info"

    id = Column(Integer, primary_key=True)  # 家具编号
    name = Column(String(32), nullable=False)  # 家具名字


class HouseImage(BaseModel,Base):
    """房屋图片"""

    __tablename__ = "ih_house_image"

    id = Column(Integer, primary_key=True)
    house_id = Column(Integer, ForeignKey("ih_house_info.id"), nullable=False)  # 房屋编号
    url = Column(String(256), nullable=False)  # 图片的路径


class Order(BaseModel,Base):
    """订单"""

    __tablename__ = "ih_order_info"

    id = Column(Integer, primary_key=True)  # 订单编号
    user_id = Column(Integer, ForeignKey("ih_user_profile.id"), nullable=False)  # 下订单的用户编号
    house_id = Column(Integer, ForeignKey("ih_house_info.id"), nullable=False)  # 预订的房间编号
    begin_date = Column(DateTime, nullable=False)  # 预订的起始时间
    end_date = Column(DateTime, nullable=False)  # 预订的结束时间
    days = Column(Integer, nullable=False)  # 预订的总天数
    house_price = Column(Integer, nullable=False)  # 房屋的单价
    amount = Column(Integer, nullable=False)  # 订单的总金额
    status = Column(  # 订单的状态
        Enum(   # 枚举     # django choice
            "WAIT_ACCEPT",  # 待接单,
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED"  # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)    # 指明在mysql中这个字段建立索引，加快查询速度
    comment = Column(Text)  # 订单的评论信息或者拒单原因
    trade_no = Column(String(80))  # 交易的流水号 支付宝的



class environment(BaseModel,Base):
    "周边配套"
    __tablename__ = "ih_environment_info"
    id = Column(Integer, primary_key=True)  # 订单编号
    name = Column(String(32), nullable=False)  # 家具名字

house_environment = Table(
    "ih_area_environment",
    Base.metadata,
    Column("area_id", Integer, ForeignKey("ih_area_info.id"), primary_key=True),  # 房屋编号
    Column("environment_id", Integer, ForeignKey("ih_environment_info.id"), primary_key=True)  # 设施编号
)



class criminal(BaseModel,Base):
    "周边案件"
    __tablename__ = "ih_criminal_info"
    id = Column(Integer, primary_key=True)  # 订单编号
    name = Column(String(32), nullable=False)  # 家具名字

house_environment = Table(
    "ih_area_criminal",
    Base.metadata,
    Column("area_id", Integer, ForeignKey("ih_area_info.id"), primary_key=True),  # 房屋编号
    Column("criminal_id", Integer, ForeignKey("ih_criminal_info.id"), primary_key=True)  # 设施编号
)


engine = create_engine('mysql://FinalProjectGLY:finalProject123%40@134.209.169.96:3306/FinalProjectGLY')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)