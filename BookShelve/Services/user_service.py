import os
from pymemcache.client import base
from django.contrib.auth.models import User
from BookShelve.Services import token_service
from BookShelve.serializer import  UserSerializer




def register_user(request):
    serialized = UserSerializer(data = request.data )

    if serialized.is_valid(raise_exception = True) == False:
         raise Exception("Non valid data")

    obj = User.objects.filter(email = serialized.data["email"])
    if len(obj) != 0:
         raise Exception("email is exist")

    obj = User.objects.filter(username = serialized.data["username"])
    if len(obj) != 0:
         raise Exception("username is exist")

    User.objects.create_user(username = serialized.data["username"], email = serialized.data["email"], password = serialized.data["password"],
                             first_name = serialized.data["first_name"], last_name = serialized.data["last_name"])
    
    return 


def save_tokens(data):
    # save tokens in front

    return 


def save_access_token( data ):

    # save access token in front

    return 
