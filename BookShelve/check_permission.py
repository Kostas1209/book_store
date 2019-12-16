from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from BookShelve.Services import token_service

def required_permission(request, permission : str) -> int:
    '''
    Check group permissions and  raise exception PermissionDenied
    requered request , permission string
    '''

    info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1] )
    #print(info)
    user = User.objects.get(id = info['user_id'])
    #print(user.get_group_permissions())
    #print(user.has_perm(permission))
    if user.has_perm(permission) == False:
        raise PermissionDenied

    return info['user_id']