from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ValidationError
from BookShelve.Services import user_service
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from BookShelve.serializer import CustomTokenObtainPairSerializer
from BookShelve.exceptions import *
from BookShelve.Services import token_service
from BookShelve.check_permission import required_permission, check_group_permission



class RegistrUserView(APIView):
     '''
        registr user 
        required unique email, password, unique username ,first_name , last_name
        for any user
     '''
     
     permission_classes = (AllowAny,)

     def post (self, request):
         try:
            data = request.data
            user_service.register_user(data)
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


class LogoutView(APIView):
    '''
        logout user
        required none
        for authenticated users
    '''
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
        token_service.delete_refresh_token(info['user_id'])
        return Response("Success", status = 200)
        # delete tokens in client


class RefreshAccessTokenView(jwt_views.TokenRefreshView): 

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        info = token_service.DecodeToken(str(request.data['access']))
        server_refresh = token_service.GetRefreshToken( info['user_id'] )
        #print(server_refresh)
        #print(str(request.data['refresh']))
        if server_refresh is not None  and \
           str(request.data['refresh']) == server_refresh:

            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])
            print(serializer.validated_data)
            return Response(serializer.validated_data, status=200)

        else: 
            if server_refresh is None:
                return Response("Not registr",status = 404)
            token_service.delete_refresh_token(info['user_id']) 
            return Response("You should login again",status = 404)
            


class UserInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    @check_group_permission("auth.view_user")
    def get(self,request):
        '''
        get user info 
        required none
        for client
        '''
        #user_id = required_permission(request, "auth.view_user")
        token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
        user_info = user_service.get_user_info(token_info['user_id'])
        return Response(user_info,status = 200)

    @check_group_permission("auth.change_user")
    def put(self, request):
        '''
        Change user info if its transferred
        required username || first_name || last_name
        for client
        '''

        try:
            data = request.data
            #user_id = required_permission(request, "auth.change_user")
            token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
            user_service.change_user_info(data,token_info['user_id'])
        except UsernameIsExist:
            return Response("Username is already exist",status = 406)
        except NothingToBeDone:
            return Response("Nothing is changed",status = 204)

        return Response("User info has been successfully changed",status = 200)


class UserAvatarView(APIView):

    permission_classes = (IsAuthenticated,) 

    @check_group_permission("BookShelve.view_useravatar")
    def get(self,request):
        #user_id = required_permission(request,"BookShelve.view_useravatar")
        token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
        text = user_service.get_user_avatar(toke_info['user_id'])
        return Response(text,status = 200)

    @check_group_permission("BookShelve.change_useravatar")
    def post(self,request):
        #user_id = required_permission(request,"BookShelve.change_useravatar")
        token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
        user_service.set_user_avatar(token_info['user_id'],str(request['text_image']))
        return Response("Avatar are saved", status = 200)



