from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect, JsonResponse


def login_required(view_func):
    def login_check(request):
        if "user" in request.session:
            return view_func(request)
        else:
            return JsonResponse({"msg": "User not logged in"})

    return login_check


# from django.conf import settings
# from rest_framework.response import Response
# from rest_framework import status

# import jwt


# def login_required(fn):
#     # Decorator to check if user has sent a valid JWT with the request
#     def wrapper_fn(req):
#         key = req.headers.get("Authorization")
#         if not key:
#             return Response("Malformed Token", status.HTTP_401_UNAUTHORIZED)
#         key = key.split(" ")
#         if len(key) != 2:
#             return Response("Malformed Token", status.HTTP_401_UNAUTHORIZED)
#         key = key[1]
#         try:
#             jwt_data = jwt.decode(key, settings.JWT_SECRET_KEY, algorithm="HS512")
#             return fn(req, jwt_data)
#         except Exception as e:
#             return Response("Malformed Token", status.HTTP_401_UNAUTHORIZED)

#     return wrapper_fn