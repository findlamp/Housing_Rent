# coding:utf-8

from flask import Blueprint


# Creating Blueprint Objects
api = Blueprint("api_1_0", __name__)


# Import the view of the blueprint
from . import demo, passport, profile, houses, orders,pay
