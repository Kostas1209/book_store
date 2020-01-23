import os
import memcache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from BookShelve.Services import token_service
from BookShelve.serializer import  UserSerializer
from BookShelve.exceptions import *
from BookShelve.check_permission import required_permission, check_group_permission
from BookShelve.models import UserAvatar
import base64
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import re   


MAX_FILE_SIZE = 1048576  # 1MB

def get_user_info(user_id):
    #user_id = required_permission(request, "auth.view_user")
    user = User.objects.get(id = user_id)
    return {"username" : user.username,
            "first_name" : user.first_name,
            "last_name" : user.last_name,
            "email" : user.email, 
            }

def change_user_info(data, user_id):
    #user_id = required_permission(request, "auth.change_user")
    user = User.objects.get(id = user_id)

    check = False

    if 'username' in data:
        check = True
        try:
            check_unique_user_info(username = str(data['username']))
            user.username = str(data['username'])
        except UsernameIsExist:
            raise UsernameIsExist

    if 'first_name' in data:
        check = True
        user.first_name = str(data['first_name'])

    if 'last_name' in data:
        check = True
        user.last_name = str(data['last_name'])

    if check == False:
        raise NothingToBeDone

    user.save()



def register_user(data):
    serializer = UserSerializer(data = data )

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
    refresh_token = memcache.Client([("cache",11211)])
    info = token_service.DecodeToken(data['access'])
    refresh_token.set(info['user_id'], data['refresh'],time = 24*60*60)
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



def get_user_avatar(user_id):
    #user_id = required_permission(request,"BookShelve.view_useravatar")
    try:
        text = UserAvatar.objects.get(user_id = user_id)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist
    return text.user_avatar

def set_user_avatar(user_id, text_image):
    SIZE = (200,120)

    image_data = re.sub('^data:image/.+;base64,', '', text_image)
    try:
        image = Image.open(BytesIO(base64.b64decode(image_data)))
    except UnidentifiedImageError:
        raise UnidentifiedImageError
    except Exception:
        raise Exception

    if len(image.fp.read()) >= MAX_FILE_SIZE:
        raise FileSize
    image.thumbnail(SIZE,Image.ANTIALIAS) # resize image
    image = image.convert('RGB')
    #image.show()


    #testing
    buffered = BytesIO()
    image.save(buffered, format = "PNG", quality=70,optimize=True)
    img_str = base64.b64encode(buffered.getvalue()) 
    if len(UserAvatar.objects.filter(user_id = user_id)) > 0:
        UserAvatar.objects.filter(user_id=user_id).update(user_avatar = img_str.decode("utf-8"))

    else:       	
        UserAvatar.objects.create(user_id = user_id, user_avatar = img_str.decode("utf-8"))

    #avatar = UserAvatar.objects.get(user_id = user_id)
    #avatar.user_avatar = str(text_image)
    #avatar.save()
    return 


