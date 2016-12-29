#coding=utf-8
import json as simplejson
from json import JSONEncoder

class HttpResultResponse(object):
    """docstring for ResponseStatus"""

    def __init__(self):
        self.jsonResult = {}
        self.status = ""
        self.resultData = {}
        self.errorMessage = ""

    def getJsonResult(self):
        """docstring for ResponseStatus"""
        self.jsonResult['resultData'] = self.resultData
        self.jsonResult['errorMessage'] = self.errorMessage
        self.jsonResult['status'] = self.status
        self.json = simplejson.dumps(self.jsonResult)
        return self.json

class MyEncode(JSONEncoder):
    """docstring for ResponseStatus"""

    def default(self, objs):
        return objs.__dick__

class ErrorMessage(object):
    """docstring for ResponseStatus"""

    USERNAME_OR_PASSWORD_INVALID = "USERNAME_OR_PASSWORD_INVALID"
    NO_SUCH_USER_OR_PASSWORD_IS_INVALID = "NO_SUCH_USER_OR_PASSWORD_IS_INVALID"
    USERNAME_IS_EXIST = "USERNAME_IS_EXIST"
    REGISTER_SUCCESS = "REGISTER_SUCCESS"
    POST_FAILED = "POST_FAILED"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    USER_IS_EXIST = "USER_IS_EXIST"
    USER_IS_NOT_EXIST = "USER_IS_NOT_EXIST"
    USERNAME_IS_NULL = "USERNAME_IS_NULL"
    UPDATE_AVATAR_SUCCESS = "UPDATE_AVATAR_SUCCESS"
    AVATAR_IS_INVALID = "AVATAR_IS_INVALID"
    MODIFY_USER_INFO_SUCCESS = "MODIFY_USER_INFO_SUCCESS"
    UPDATE_POST_SUCCESS = "UPDATE_POST_SUCCESS"
    GET_TAG_SUCCESS = "GET_TAG_SUCCESS"
    GET_TAG_FAILED = "GET_TAG_FAILED"
    GET_POST_SUCCESS = "GET_POST_SUCCESS"
    GET_POST_FAILED = "GET_POST_FAILED"

    def __init__(self):
        pass

class ResponseStatus(object):
    """docstring for ResponseStatus"""
    POST_FAILED = "8001"

    def __init__(self):
        pass
		