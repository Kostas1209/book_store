from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser 
import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def get_image_path(instance, filename):
    return os.path.join('avatars', str(instance.user_id), filename)

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
    user_avatar =  models.fields.files.ImageField(upload_to = get_image_path, default = 'avatar/None/no-img.jpg')

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_avatar = self.compressImage(self.user_avatar)
        super(UserAvatar, self).save(*args, **kwargs)

    def compressImage(self,uploadedImage):
        imageTemprorary = Image.open(uploadedImage)
        outputIoStream = BytesIO()
        imageTemproraryResized = imageTemprorary.resize( (100,80) ) 
        imageTemprorary.save(outputIoStream , format='PNG', quality=60)
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        return uploadedImage
    def __str__(self):
        return str(self.user_id)

