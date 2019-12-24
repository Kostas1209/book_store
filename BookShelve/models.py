from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser 
import os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile



class Book(models.Model):

    id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 200, default = '')
    amount_in_storage = models.IntegerField(default = 0)
    author = models.CharField(max_length = 100, default = '')
    price = models.IntegerField(default = 0)

    def __str__(self):
        return self.title
    

class UserBasket(models.Model):

    id = models.AutoField(primary_key = True)
    user_id = models.IntegerField(default = 0)
    book_id = models.IntegerField(default = 0)
    amount = models.IntegerField(default = 0)

    def __str__(self):
        return str(self.user_id)


class UserAvatar(models.Model):

    user_id = models.IntegerField(primary_key = True)
    user_avatar =  models.TextField()

    def __str__(self):
        return str(self.user_id)

