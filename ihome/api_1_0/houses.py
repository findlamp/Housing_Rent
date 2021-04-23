# coding:utf-8

from . import api
from flask import g, current_app, jsonify, request, session
from ihome.utils.response_code import RET
from ihome.models import Area, House, Facility, HouseImage, User, Order,Environment,Criminal
from ihome import db, constants, redis_store
from ihome.utils.commons import login_required
from ihome.utils.image_storage import storage
from datetime import datetime
import json
import uuid
import os
from pathlib import Path

# list to json
def listToJson(lst):
    import json
    import numpy as np
    keys = [str(x) for x in np.arange(len(lst))]
    list_json = dict(zip(keys, lst))
    str_json = json.dumps(list_json, indent=2, ensure_ascii=False)  # json to string
    return str_json


@api.route("/areas")
def get_area_info():
    """get the location information"""
    #Attempting to read data from Redis
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # redis have cached data
            current_app.logger.info("hit redis area_info")
            return resp_json, 200, {"Content-Type": "application/json"}
    
    #Query database, read the city information
    try:
        print('Query database, read information')
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Database exception")

    area_dict_li = []
 
    # Converts the object to a dictionary
    for area in area_li:
        area_dict_li.append(area.to_dict())
        print("data{}".format(area.to_dict()))
    # Convert the data to a JSON string
    resp_dict = dict(errno=RET.OK, errmsg="OK", data=area_dict_li)
    resp_json = json.dumps(resp_dict)

    # Save the data to Redis
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}


@api.route("/houses/info", methods=["POST"])
@login_required
def save_house_info():
    """preserve the house information
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    """
    # get data
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")  # house title
    price = house_data.get("price")  # Housing price
    area_id = house_data.get("area_id")  # location id
    address = house_data.get("address")  # address
    room_count = house_data.get("room_count")  # number of rooms
    acreage = house_data.get("acreage")  # size of room
    unit = house_data.get("unit")  # number of room
    capacity = house_data.get("capacity")  # number of people living 
    beds = house_data.get("beds")  # number of beds
    deposit = house_data.get("deposit")  # deposit
    min_days = house_data.get("min_days")  # minimum stay days
    max_days = house_data.get("max_days")  # maximum stay days

    # Calibration parameters
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="Incomplete Parameter")

    # Determine if the amount is correct
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="Wrong Parameter")

    # Determine if the city ID exists
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Database exception")

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg="Incorrect information of district")

    # preserve house information
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # facility
    facility_ids = house_data.get("facility")

    # If the user has checked the facility information, save the database
    if facility_ids:
        # ["7","8"]
        try:
            # select  * from ih_facility_info where id in []
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="Database exception")

        if facilities:
            # facility information
            # perserve facility information
            house.facilities = facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="Failed to save data")

    # preserve successfully
    return jsonify(errno=RET.OK, errmsg="OK", data={"house_id": house.id})


@api.route("/houses/image", methods=["POST","GET"])
@login_required
def save_house_image():
    """preserve house picture id
    """
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="parameter error")

    # whether house_id is correct
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Database exception")

    if house is None:  # if not house:
        return jsonify(errno=RET.NODATA, errmsg="unexistent house")


    # perserve picture in static image
    try:
        # get uuid
        file_name = str(uuid.uuid1())+'.png'
        basedir = os.getcwd()
        image_path = os.path.join(basedir,'ihome','static','images',file_name)
        image_file.save(image_path)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="Failed to save image")

    # Save the image information to the database
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)

    # Process the main image of the house
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="Exception saving image data")

    image_url = constants.QINIU_URL_DOMAIN + file_name

    return jsonify(errno=RET.OK, errmsg="OK", data={"image_url": image_url})


@api.route("/user/houses", methods=["GET"])
@login_required
def get_user_houses():
    """get information"""
    user_id = g.user_id

    try:
        # House.query.filter_by(user_id=user_id)
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Failed to get data")

    # Convert the searched house information into a dictionary and store it in the list
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """get information"""
    # Try to fetch data from the cache
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret = None

    if ret:
        current_app.logger.info("hit house index info redis")
        # Because Redis saves the JSON string, so the string concatenation is directly returned
        return '{"errno":0, "errmsg":"OK", "data":%s}' % ret, 200, {"Content-Type": "application/json"}
    else:
        try:
            #Query database to return the 5 items with the highest number of house orders
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="Query data failed")

        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="Query no data")

        houses_list = []
        for house in houses:
            # If no picture
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        # Convert the data to JSON and save it to the Redis cache
        json_houses = json.dumps(houses_list)  # "[{},{},{}]"
        try:
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            current_app.logger.error(e)

        return '{"errno":0, "errmsg":"OK", "data":%s}' % json_houses, 200, {"Content-Type": "application/json"}


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """gey information"""
    # When the front end is displayed on the house details page,
    # if the user browsing the page is not the landlord of the house
    #  the reservation button will be displayed. Otherwise
    #  the front end will not be displayed.
    # So the backend needs to return the user_id of the logged-in user
    user_id = session.get("user_id", "-1")
    # Calibration parameters
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="parameter determination ")

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Query data failed")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="The house doesn't exist")

    # Converts house object data to a dictionary
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="Data error")

    # Convert to JSON format
    json_house = json.dumps(house_data)

    # Query geographic information through the AREA information
    area_id = house_data['area_id']
    environment = Environment.query.filter(Environment.area_id == area_id).all()
    environment_data = []
    for item in environment:
        environment_data.append(item.name)
    json_environment = listToJson(environment_data)

    # Use the AREA information to query crime information
    criminal = Criminal.query.filter(Environment.area_id == area_id).all()
    criminal_data = {}
    for item in criminal:
        criminal_data[item.name] = item.times
    json_criminal = json.dumps(criminal_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s,"environment":%s,"criminal":%s}}' % (user_id, json_house,json_environment,json_criminal), \
           200, {"Content-Type": "application/json"}
    return resp


# GET /api/v1.0/houses?sd=2017-12-01&ed=2017-12-31&aid=10&sk=new&p=1
@api.route("/houses")
def get_house_list():
    """get inforamtion list"""
    start_date = request.args.get("sd", "")  # chechin time
    end_date = request.args.get("ed", "")  # check out time
    area_id = request.args.get("aid", "")  # loaction id
    sort_key = request.args.get("sk", "new")  # key
    page = request.args.get("p")  # page

    # time to deal with
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="The date parameter is incorrect")

    # location id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="Incorrect zone parameter")

    # deal with page
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # Get cached data
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type": "application/json"}

    # The parameter list container for the filter condition
    filter_params = []

    # Filling filter parameters
    # time conditions
    conflict_orders = None

    try:
        if start_date and end_date:
            # Query for conflicting orders
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Database exception")

    if conflict_orders:
        # Gets the conflicting house ID from the order
        conflict_house_ids = [order.house_id for order in conflict_orders]

        # If the conflicting house ID is not empty, add a condition to the query parameter
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))

    # area condition 
    if area_id:
        filter_params.append(House.area_id == area_id)

    # query database
    if sort_key == "booking":  # maximum
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:  # new old
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # Handle paging
    try:
        # page
        page_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Database exception")

    # Get page data
    house_li = page_obj.items
    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())

    # Get page number
    total_page = page_obj.pages

    resp_dict = dict(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "current_page": page})
    resp_json = json.dumps(resp_dict)

    if page <= total_page:
        # Set cache data
        redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
        # Hash type
        try:
            # redis_store.hset(redis_key, page, resp_json)
            # redis_store.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)

            # Create a Redis pipe object that can execute multiple statements at once
            pipeline = redis_store.pipeline()

            # Enables recording of multiple statements
            pipeline.multi()

            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)

            # execute statement
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}

















