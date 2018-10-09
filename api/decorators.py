from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect,JsonResponse

def login_required(view_func):
	def login_check(request):
		if 'user' in request.session:
			return view_func(request)
		else :
			return JsonResponse({'msg':'User not logged in'})
	return login_check