from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ValidationError
from BookShelve.Services import user_service
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from pymemcache.client import base
from BookShelve.serializer import CustomTokenObtainPairSerializer
from BookShelve.exceptions import *
from BookShelve.token_service import *

class RegistrUserView(APIView):
     '''
        registr user 
        required unique email, password, unique username ,first_name , last_name
        for any user
     '''
     
     permission_classes = (AllowAny,)

     def post (self, request):
         try:
            user_service.register_user(request)
         except EmailIsExist:
             return Response("Email is already exist", status = 406)
         except UsernameIsExist:
             return Response("Username is already exist", status = 406)


         return Response("Account is created", status = 201)

class LoginView( jwt_views.TokenObtainPairView):
    '''
        login user
        required email, password
        for any user
    '''

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response("Not Authorized", status = 401)
        except ValidationError:
            return Response("User not found", status = 404)

        print(serializer.validated_data)
        user_service.save_refresh_token_in_cache(serializer.validated_data) # save refresh_token in server 
        return Response(serializer.validated_data, status = 200)     # send both tokens to client


    #Template!!!
class RefreshAccessTokenView(jwt_views.TokenRefreshView): 

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
        server_refresh = token_service.GetRefreshToken( info['user_id'] )
        if request.data['refresh'] == server_refresh:
            serializer = self.get_serializer(data=request.data)

            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])
            print(serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        else: 
            token_service.delete_refresh_token(info['user_id'])
            #Redirect to login




class UserInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        '''
        get user info 
        required none
        for client
        '''

        user_info = user_service.get_user_info(request)
        return Response(user_info,status = 200)

    def put(self, request):
        '''
        Change user info if its transferred
        required username || first_name || last_name
        for client
        '''

        try:
            user_service.change_user_info(request)
        except UsernameIsExist:
            return Response("Username is already exist",status = 406)
        except NothingToBeDone:
            return Response("Nothing is changed",status = 204)

        return Response("User info has been successfully changed",status = 200)


class UserAvatarView(APIView):

    permission_classes = (IsAuthenticated,) 

    def get(self,request):
        text = user_service.get_user_avatar(request)
        return Response(text,status = 200)

    def post(self,request):
        user_service.set_user_avatar(request)
        return Response("Avatar are saved", status = 200)



