from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect

def login_required(view_func):
	def login_check(request,code=0):
		# request.session['user']='test'
		if 'user' in request.session:
			return view_func(request,code)
		else :
			return HttpResponseRedirect("/dalalbull/register/")
	return login_check