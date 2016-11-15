#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
import json as simplejson
from models import User

# Create your views here.
def index(request):
	return HttpResponse(u"This is lovemarker")

# 登录
def login(request):
	dict = {}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		pushKey = request.POST.get('pushKey')
		user = User.objects.get(username = username , password = password)
		if user:
			dict['errorMessage'] = "login_success"
			dict['status'] = "0"
			dict['resultData'] = user
		else:
			dict['errorMessage'] = "no_such_user_or_password_is_invalid"
			dict['status'] = "8003"
		json = simplejson.dumps(dict)
		return HttpResponse(json)
	else:
		dict['errorMessage'] = "POST failed"
		dict['status'] = "8002"
		json  = simplejson.dumps(dict)
		return HttpResponse("POST failed")	

# 注册
def register(request):
	dict = {}
	resultData = {}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		gender = request.POST.get('gender')
		pushKey = request.POST.get('pushKey')
		birthday = request.POST.get('birthday')
		nickname = request.POST.get('nickname')
		if username and password :
			user = User.objects.get(username = username , password = password)
			if user:
				dict['errorMessage'] = "username_is_exist"
				dict['status'] = "8002"
			else:
				dict['errorMessage'] = "register_success"
				dict['status'] = "0"
				# 将用户数据存入数据库
				user = User(username = username,password = password,gender = gender,pushKey = pushKey,nickname = nickname,birthday = birthday)
				user.save()
				dict['resultData'] = user
		else:
			dict['errorMessage'] = "username_or_password_invalid"
			dict['status'] = "8001"
		json = simplejson.dumps(dict)
		return HttpResponse(json)
	else:
		dict['errorMessage'] = "POST_FAILED"
		dict['status'] = "8001"
		json  = simplejson.dumps(dict)
		return HttpResponse("POST failed")
