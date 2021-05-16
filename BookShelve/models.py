from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser 
from django.core.files.uploadedfile import InMemoryUploadedFile



class Book(models.Model):

    id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 200, default = '')
    amount_in_storage = models.IntegerField(default = 0)
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

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return str(self.first_name)

class Library(models.Model):
    id = models.AutoField(primary_key=True)
    book_id = models.IntegerField()
    author_id = models.IntegerField()

    def __str__(self):
        return str(self.book_id)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    book_id = models.IntegerField()
    user_id = models.IntegerField()
    message = models.CharField(max_length=1000,default='')

    def __str__(self):
        return str(self.book_id)
