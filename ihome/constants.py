# coding:utf-8
import os

# The Redis validity period of the image verification code, unit: seconds
IMAGE_CODE_REDIS_EXPIRES = 180

# Redis validity period of SMS verification code, unit: second
SMS_CODE_REDIS_EXPIRES = 300

# The interval between sending SMS verification code, in seconds
SEND_SMS_CODE_INTERVAL = 60

# Number of login error attempts
LOGIN_ERROR_MAX_TIMES = 5

# Login error limit time, in seconds
LOGIN_ERROR_FORBID_TIME = 600

# The Key value of the picture address will not be changed for the time being
QINIU_URL_DOMAIN =  '/static/images/'

# Cache time of city information, unit: seconds
AREA_INFO_REDIS_CACHE_EXPIRES = 7200

# The home page shows the largest number of homes
HOME_PAGE_MAX_HOUSES = 5

# The Redis cache time of the home page housing data, unit: seconds
HOME_PAGE_DATA_REDIS_EXPIRES = 7200

# Maximum number of reviews displayed on the house detail page
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30

# Housing details page data Redis cache time, unit: seconds
HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200

# Housing list page per page data capacity
HOUSE_LIST_PAGE_CAPACITY = 2

# Number of pages in the house list cache time, per second
HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200

# Alipay gateway address (payment address domain name)
ALIPAY_URL_PREFIX = "https://openapi.alipaydev.com/gateway.do?"
