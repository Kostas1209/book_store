from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from BookShelve.Services import user_service
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from pymemcache.client import base
from BookShelve.serializer import CustomTokenObtainPairSerializer

class RegistrUserView(APIView):

     permission_classes = (AllowAny,)

     def post (self, request):
         try:
            user_service.register_user(request)
         except Exception as e:
             return Response(str(e))

         return Response("Account is created")


class LoginView( jwt_views.TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        print(serializer.validated_data)
        user_service.save_tokens(serializer.validated_data)
        return Response( "Tokens was save" )


    #Prototype!!!
class RefreshAccessTokenView(jwt_views.TokenRefreshView): 

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh_token = tokens_service. get_refresh_token()
        print(refresh_token)
        data = self.authenticate(refresh_token)[1] 

        user_service.save_access_token(data)

        return Response("Access token was refresh ")

