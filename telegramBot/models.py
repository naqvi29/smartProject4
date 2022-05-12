from django.db import models
from django.contrib.auth import get_user_model
from home.models import User

# Create your models here.
# class Telegram_Accounts(models.Model):
#     userid= models.CharField(max_length=100)
#     hash_id= models.TextField()
#     hash_key= models.TextField()
#     number= models.CharField(max_length=120)
#     session_file= models.TextField()
#     sleep_time= models.CharField(max_length=120,default=2)
#     sleep_time_first= models.CharField(max_length=120,default=2)
#     def __str__(self):
#         return self.number


# # # # # # # # # # # # # # # # # # # # # # # # #  ADDED THESE MODELS


class Telegram_Accounts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,default=None,blank=True)
    number = models.CharField(max_length=500)
    hash_key = models.CharField(max_length=500)
    hash_id = models.CharField(max_length=500)
    proxy = models.CharField(max_length=200,null=True)
    sleep_time= models.CharField(max_length=120,default=2)
    sleep_time_first= models.CharField(max_length=120,default=2)
    def __str__(self):
        return self.number

class TelegramSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,default=None,blank=True)
    telegramAccount = models.ForeignKey(Telegram_Accounts,on_delete=models.CASCADE,null=True,default=None)
    auth_key = models.CharField(max_length=5000,null=True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # END

class Telegram_Groups(models.Model):
    userid= models.CharField(max_length=100)
    account_id= models.CharField(max_length=100)
    group_name= models.TextField()
    def __str__(self):
        return self.group_name

class Telegram_Questions(models.Model):
    userid= models.CharField(max_length=100)
    account_id= models.CharField(max_length=100)
    questions= models.TextField()
    def __str__(self):
        return self.questions

class Telegram_Answers(models.Model):
    userid= models.CharField(max_length=100)
    account_id= models.CharField(max_length=100)
    answers= models.TextField()
    def __str__(self):
        return self.answers

class Schedule_Messages(models.Model):
    userid= models.CharField(max_length=100)
    message = models.TextField()
    image = models.TextField(default="")
    account_id= models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    delay = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    type = models.CharField(max_length=100, default="text")
    def __str__(self):
        return self.message
    
class Telegram_Scrapped_Groups(models.Model):
    userid = models.CharField(max_length=100)
    account_id= models.CharField(max_length=100)
    group_id = models.CharField(max_length=100) 
    group_title = models.TextField() 
    group_username = models.TextField() 
    def __str__(self):
        return self.group_title

class Telegram_Scrapped_Members(models.Model):
    userid = models.CharField(max_length=100)
    account_id= models.CharField(max_length=100)
    group_id = models.CharField(max_length=100) 
    member_id = models.CharField(max_length=100)
    member_name = models.TextField() 
    status = models.CharField(max_length=100, default="not scheduled")
    added_in = models.TextField(default="")
    def __str__(self):
        return self.member_name

class Schedule_User_Messages(models.Model):
    userid= models.CharField(max_length=100)
    message = models.TextField()
    image = models.TextField(default="")
    member_names = models.TextField()
    delay = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    type = models.CharField(max_length=100, default="text")
    limit_per_account = models.CharField(max_length=100, default=40)
    accounts = models.TextField(default="")
    def __str__(self):
        return self.message

class Logs_for_user_Messages(models.Model):
    userid= models.CharField(max_length=100)
    log = models.TextField()
    message = models.TextField()
    image = models.TextField(default="")
    member_name = models.TextField()
    account= models.CharField(max_length=100)
    type = models.CharField(max_length=100, default="text")
    date = models.TextField(default="")
    time = models.TextField(default="")
    def __str__(self):
        return self.log

class Schedule_Add_Users(models.Model):
    userid= models.CharField(max_length=100)
    your_group = models.TextField()
    member_names = models.TextField()
    delay = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    limit_per_account = models.CharField(max_length=100, default=40)
    accounts = models.TextField(default="")
    def __str__(self):
        return self.your_group

class Logs_for_add_user(models.Model):
    userid= models.CharField(max_length=100)
    log = models.TextField()
    your_group = models.TextField()
    member_name = models.TextField()
    account= models.CharField(max_length=100)
    date = models.TextField(default="")
    time = models.TextField(default="")
    def __str__(self):
        return self.log