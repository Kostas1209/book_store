from BookShelve.serializer import  UserSerializer
from django.contrib.auth.models import User
from pymemcache.client import base
from BookShelve.Services import token_service


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
    client = base.Client(('localhost', 11211))

    info = token_service.DecodeToken(data["access"]) # get info from  access token

    # write to cache refresh token
    client.set('{}_refresh'.format(info['user_id']), data['refresh'])

    # Write to cache access token 
    client.set('{}_access'.format(info['user_id']), data['access'])

    return 


def save_access_token( data ):

    # Write to cache access token 
    client = base.Client(('localhost', 11211))
    client.set('{}_access'.format(info['user_id']), data['access'])

    return 
