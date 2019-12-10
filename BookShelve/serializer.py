from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ( 'title', 'amount_in_storage', 'author', 'price' )


class BookChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBasket
        fields = ('book_id','user_id','amount')


class UserSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class LoginSerializer(serializers.Serializer):

    password = serializers.CharField()
    username = serializers.CharField(max_length=120)


