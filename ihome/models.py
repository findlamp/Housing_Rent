# -*- coding:utf-8 -*-

from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from ihome import constants

# TODO 
class BaseModel(object):

    create_time = db.Column(db.DateTime, default=datetime.now)  # record set time
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # record update time


class User(BaseModel, db.Model):
    """user"""

    __tablename__ = "ih_user_profile"

    id = db.Column(db.Integer, primary_key=True)  # user id
    name = db.Column(db.String(32), unique=True, nullable=False)  # user name
    password_hash = db.Column(db.String(128), nullable=False)  # password
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # phone number
    real_name = db.Column(db.String(32))  # realname
    id_card = db.Column(db.String(20))  # id
    avatar_url = db.Column(db.String(128))  # the route of picture
    houses = db.relationship("House", backref="user")  # house
    orders = db.relationship("Order", backref="user")  # order

    # When you add a property decorator, you change the function to a property whose name is the function name
    @property
    def password(self):
        """Function behavior that reads a property"""
        # return "xxxx"
        raise AttributeError("This property can only be set, not read")

    # Using this decorator, the corresponding set property action
    @password.setter
    def password(self, value):
        """
         user.passord = "xxxxx"
        :param value: value "xxxxx", 
        :return:
        """
        self.password_hash = generate_password_hash(value)

    # def generate_password_hash(self, origin_password):
    #     """Encrypt the password"""
    #     self.password_hash = generate_password_hash(origin_password)

    def check_password(self, passwd):
        """
        verify the password
        :param passwd:  original password
        :return: correct，return True， otherwise False
        """
        return check_password_hash(self.password_hash, passwd)

    def to_dict(self):
        """Converts the object to dictionary data"""
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar": constants.QINIU_URL_DOMAIN + self.avatar_url if self.avatar_url else "",
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict

    def auth_to_dict(self):
        """Convert real name information to dictionary data"""
        auth_dict = {
            "user_id": self.id,
            "real_name": self.real_name,
            "id_card": self.id_card
        }
        return auth_dict


class Area(BaseModel, db.Model):
    """城区"""

    __tablename__ = "ih_area_info"

    id = db.Column(db.Integer, primary_key=True)  # location id
    name = db.Column(db.String(32), nullable=False)  # location name
    houses = db.relationship("House", backref="area")  # location house

    def to_dict(self):
        """将对象转换为字典"""
        d = {
            "aid": self.id,
            "aname": self.name
        }
        return d


# Building facilities list, establish many-to-many relationship between building and facilities
house_facility = db.Table(
    "ih_house_facility",
    db.Column("house_id", db.Integer, db.ForeignKey("ih_house_info.id"), primary_key=True),  # house id
    db.Column("facility_id", db.Integer, db.ForeignKey("ih_facility_info.id"), primary_key=True)  # facility id
)


class House(BaseModel, db.Model):
    """house information"""

    __tablename__ = "ih_house_info"

    id = db.Column(db.Integer, primary_key=True)  # house id
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False)  # landlord id
    area_id = db.Column(db.Integer, db.ForeignKey("ih_area_info.id"), nullable=False)  # location id
    title = db.Column(db.String(64), nullable=False)  # title
    price = db.Column(db.Integer, default=0)  # cost
    address = db.Column(db.String(512), default="")  # address
    room_count = db.Column(db.Integer, default=1)  # number of rooms
    acreage = db.Column(db.Integer, default=0)  # house size
    unit = db.Column(db.String(32), default="")  # number of rooms
    capacity = db.Column(db.Integer, default=1)  # The number of people a house holds
    beds = db.Column(db.String(64), default="")  # number of beds
    deposit = db.Column(db.Integer, default=0)  # deposit
    min_days = db.Column(db.Integer, default=1)  # Minimum stay days
    max_days = db.Column(db.Integer, default=0)  # Maximum stay days，0 repesents unlimited
    order_count = db.Column(db.Integer, default=0)  # number of orders
    index_image_url = db.Column(db.String(256), default="")  # the route of picture
    facilities = db.relationship("Facility", secondary=house_facility)  # house facility
    images = db.relationship("HouseImage")  # picture of room
    orders = db.relationship("Order", backref="house")  # order

    def to_basic_dict(self):
        """Convert basic information to dictionary data"""
        house_dict = {
            "house_id": self.id,
            "title": self.title,
            "price": self.price,
            "area_name": self.area.name,
            "img_url": constants.QINIU_URL_DOMAIN + self.index_image_url if self.index_image_url else "",
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "ctime": self.create_time.strftime("%Y-%m-%d"),
            "area_id" : self.area_id
        }
        return house_dict

    def to_full_dict(self):
        """Convert details to dictionary data"""
        house_dict = {
            "hid": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "acreage": self.acreage,
            "unit": self.unit,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days,
            "area_id" : self.area_id
        }

        # house picture
        img_urls = []
        for image in self.images:
            img_urls.append(constants.QINIU_URL_DOMAIN + image.url)
        house_dict["img_urls"] = img_urls

        # house facility
        facilities = []
        for facility in self.facilities:
            facilities.append(facility.id)
        house_dict["facilities"] = facilities

        # comment
        comments = []
        orders = Order.query.filter(Order.house_id == self.id, Order.status == "COMPLETE", Order.comment != None)\
            .order_by(Order.update_time.desc()).limit(constants.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
        for order in orders:
            comment = {
                "comment": order.comment,  # inforamtion
                "user_name": order.user.name if order.user.name != order.user.mobile else "anonymous user",  # 发表评论的用户
                "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%S")  # time
            }
            comments.append(comment)
        house_dict["comments"] = comments
        return house_dict


class Facility(BaseModel, db.Model):
    """facility"""

    __tablename__ = "ih_facility_info"

    id = db.Column(db.Integer, primary_key=True)  # id
    name = db.Column(db.String(32), nullable=False)  # name


class HouseImage(BaseModel, db.Model):
    """house picture"""

    __tablename__ = "ih_house_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house_info.id"), nullable=False)  # house id
    url = db.Column(db.String(256), nullable=False)  # route of picture
class Order(BaseModel, db.Model):
    """order"""

    __tablename__ = "ih_order_info"

    id = db.Column(db.Integer, primary_key=True)  # order id
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False)  # user id
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house_info.id"), nullable=False)  # house id
    begin_date = db.Column(db.DateTime, nullable=False)  # checkin
    end_date = db.Column(db.DateTime, nullable=False)  # checkout
    days = db.Column(db.Integer, nullable=False)  # number of days
    house_price = db.Column(db.Integer, nullable=False)  # cost per night
    amount = db.Column(db.Integer, nullable=False)  # total cost
    status = db.Column(  # stauts of order
        db.Enum(   # ex     # django choice
            "WAIT_ACCEPT",  # remian to be accepted,
            "WAIT_PAYMENT",  # remain to be paid
            "PAID",  # paid
            "WAIT_COMMENT",  # remain to be commented
            "COMPLETE",  # completed
            "CANCELED",  # cancel
            "REJECTED"  # deny
        ),
        default="WAIT_ACCEPT", index=True)  
    comment = db.Column(db.Text)  # Specifies that this field is indexed in MySQL to speed up queries
    trade_no = db.Column(db.String(80))  # The current number of the transaction

    def to_dict(self):
        """Converts order information to dictionary data"""
        order_dict = {
            "order_id": self.id,
            "title": self.house.title,
            "img_url": constants.QINIU_URL_DOMAIN + self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""
        }
        return order_dict

# updated information
class Environment(BaseModel, db.Model):
    "facility"
    __tablename__ = "ih_environment_info"
    id = db.Column(db.Integer, primary_key=True)  
    area_id = db.Column(db.Integer)
    name = db.Column(db.String(32), nullable=False)  

    def to_dict(self):
        environment_dict = {
            "area_id": self.id,
            "id" : self.id,
            "name" : self.name
        }
        return environment_dict





class Criminal(BaseModel, db.Model):
    "event"
    __tablename__ = "ih_criminal_info"
    id = db.Column(db.Integer, primary_key=True)  
    area_id = db.Column(db.Integer)
    times = db.Column(db.Integer)
    name = db.Column(db.String(32), nullable=False)  
    
    def to_dict(self):
        criminal_dict = {
            "id" : self.id,
            "name" : self.name,
            "area_id" : self.area_id,
            "times" : self.times
        }
        return criminal_dict



