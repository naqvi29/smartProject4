from django.db import models

# Create your models here.

class User(models.Model):
    username= models.CharField(max_length=100)
    email= models.EmailField()
    password= models.CharField(max_length=100)
    profile_pic= models.CharField(max_length=200)
    type= models.CharField(max_length=200,default='user')
    users_scrapper = models.CharField(max_length=100,default=True)
    dm_to_group = models.CharField(max_length=100,default=True)
    dm_to_user = models.CharField(max_length=100,default=True)
    add_users_to_group = models.CharField(max_length=100,default=True)
    autoscout_scrap = models.CharField(max_length=100,default=True)

    def __str__(self):
        return self.username
