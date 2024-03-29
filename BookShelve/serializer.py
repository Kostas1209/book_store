from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import  TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        self.user = User.objects.filter(email=attrs[self.username_field]).first()

        if not self.user:
            raise ValidationError('The user is not valid.')

        if self.user:
            if not self.user.check_password(attrs['password']):
                raise ValidationError('Incorrect credentials.')
        print(self.user)
        if self.user is None or not self.user.is_active:
            raise ValidationError('No active account found with the given credentials')

        return {}

class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):

        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ( 'id', 'title', 'amount_in_storage', 'price' )


class BookChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBasket
        fields = ('book_id','amount')


class UserSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class ResponseBookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    price = serializers.IntegerField()
    amount_in_storage = serializers.IntegerField()
    title = serializers.CharField()
    author = serializers.ListField()


class BookSerializerWithId(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ( 'id', 'title', 'amount_in_storage', 'price' )


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ( 'id', 'first_name', 'last_name' )

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ( 'id', 'book_id', 'user_id','message' )




