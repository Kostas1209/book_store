import os
from pymemcache.client import base
from django.contrib.auth.models import User
from BookShelve.Services import token_service
from BookShelve.serializer import  UserSerializer
from BookShelve.exceptions import *
from BookShelve.check_permission import required_permission
from BookShelve.models import UserAvatar

def get_user_info(request):
    user_id = required_permission(request, "auth.view_user")
    user = User.objects.get(id = user_id)
    return {"username" : user.username,
            "first_name" : user.first_name,
            "last_name" : user.last_name,
            "email" : user.email, 
            }

def change_user_info(request):
    user_id = required_permission(request, "auth.change_user")
    user = User.objects.get(id = user_id)

    check = False

    if 'username' in request.data:
        check = True
        try:
            check_unique_user_info(username = str(request.data['username']))
            print('test')
            user.username = str(request.data['username'])
        except UsernameIsExist:
            raise UsernameIsExist

    if 'first_name' in request.data:
        check = True
        user.first_name = str(request.data['first_name'])

    if 'last_name' in request.data:
        check = True
        user.last_name = str(request.data['last_name'])

    if check == False:
        raise NothingToBeDone

    user.save()



def register_user(request):
    serializer = UserSerializer(data = request.data )

    if serializer.is_valid(raise_exception = True) == False:
         raise SerializerNonValid
    try:
        check_unique_user_info(username = serializer.data['username'],
                           email = serializer.data['email'])
    except EmailIsExist:
        raise EmailIsExist
    except UsernameIsExist:
        raise UsernameIsExist

    user = User.objects.create_user(username = serializer.data["username"], email = serializer.data["email"], password = serializer.data["password"],
                             first_name = serializer.data["first_name"], last_name = serializer.data["last_name"])
    user.groups.set([3]) # client group
    user.save()

    
    return 



def save_refresh_token_in_cache(data):

    refresh_token = base.Client(("localhost",11211))
    info = token_service.DecodeToken(data['access'])
    refresh_token.set(info['user_id'], data['refresh'], time = 60 * 60 * 24)

    return 

def save_access_token( data ):

    # save access token in front

    return 



def check_unique_user_info(username = None , email = None):

    if email  is not None:
        obj = User.objects.filter(email = email)
        if len(obj) != 0:
            raise EmailIsExist

    if username is not None:
        obj = User.objects.filter(username = username)
        if len(obj) != 0:
            raise UsernameIsExist



def get_user_avatar(request):
    user_id = required_permission(request,"BookShelve.view_useravatar")
    text = UserAvatar.objects.get(id = user_id)
    
    return text

def set_user_avatar(request):
    user_id = required_permission(request,"BookShelve.change_useravatar")
    avatar = UserAvatar.objects.get(id = user_id)
    avatar.user_avatar = str(request['text_image'])
    avatar.save()

    return 


