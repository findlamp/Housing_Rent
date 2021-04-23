# coding:utf-8

class RET:
    OK                  = "0"
    DBERR               = "4001"
    NODATA              = "4002"
    DATAEXIST           = "4003"
    DATAERR             = "4004"
    SESSIONERR          = "4101"
    LOGINERR            = "4102"
    PARAMERR            = "4103"
    USERERR             = "4104"
    ROLEERR             = "4105"
    PWDERR              = "4106"
    REQERR              = "4201"
    IPERR               = "4202"
    THIRDERR            = "4301"
    IOERR               = "4302"
    SERVERERR           = "4500"
    UNKOWNERR           = "4501"

error_map = {
    RET.OK                    : u"Success",
    RET.DBERR                 : u"Database query error",
    RET.NODATA                : u"No data",
    RET.DATAEXIST             : u"Existent data",
    RET.DATAERR               : u"Wrong data",
    RET.SESSIONERR            : u"User didn't log in",
    RET.LOGINERR              : u"User's unsuccessful login ",
    RET.PARAMERR              : u"parameter error",
    RET.USERERR               : u"unexistent user",
    RET.ROLEERR               : u"wrong user information",
    RET.PWDERR                : u"wrong password",
    RET.REQERR                : u"Illegal requests or limited number of requests",
    RET.IPERR                 : u"limited IP",
    RET.THIRDERR              : u"Third party system error",
    RET.IOERR                 : u"File read/write error",
    RET.SERVERERR             : u"internal error",
    RET.UNKOWNERR             : u"unknown error",
}
