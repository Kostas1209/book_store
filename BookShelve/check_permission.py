from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from BookShelve.Services import token_service

def required_permission(request, permission : str) -> int:
    '''
    Check group permissions and  raise exception PermissionDenied
    requere request , permission string
    '''

    info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1] )
    #print(info)
    user = User.objects.get(id = info['user_id'])
    #print(user.get_group_permissions())
    #print(user.has_perm(permission))
    if user.has_perm(permission) == False:
        raise PermissionDenied

    return info['user_id']



def check_group_permission(permission : str):
    '''
    Check group permissions and  raise exception PermissionDenied
    requere  permission string
    should decorate view methods(get, post ...)
    '''
    def Decorator(func):
        def decorator(self,request):
            info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1] )
            #print(info)
            user = User.objects.get(id = info['user_id'])
            #print(user.get_group_permissions())
            #print(user.has_perm(permission))
            if user.has_perm(permission) == False:
                raise PermissionDenied

            response = func(self, request)
            return response

        return decorator
    return Decorator

