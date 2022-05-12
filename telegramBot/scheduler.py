from email import message
from django.shortcuts import render, redirect
# from httplib2 import Http
from home.models import User
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
import os.path
from telegramBot.models import Telegram_Accounts
from telegramBot.models import Telegram_Groups
from telegramBot.models import Telegram_Questions
from telegramBot.models import Telegram_Answers
from telegramBot.models import Schedule_Messages
from telegramBot.models import Schedule_User_Messages
from telegramBot.models import Logs_for_user_Messages
from telegramBot.models import Schedule_Add_Users
from telegramBot.models import Logs_for_add_user
from django.conf import settings
import time
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import *
from telethon import functions
import sys
from datetime import datetime
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
import json
from telethon.tl.functions.channels import InviteToChannelRequest


PROFILE_PIC_FOLDER='static/images/profile-pics/' 
TELEGRAM_SESSIONS_FOLDER= settings.BASE_DIR
TELEGRAM_CHAT_FOLDER='static/images/chat-pics/' 
# Create your views here.

def some_task():
    print('Tick! The time is: %s' % datetime.now())
    data = Schedule_Messages.objects.all().filter(status="pending")
    for i in data:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
        tm_string = now.strftime("%H:%M")
        print("time-now = ",tm_string)
        if i.date == dt_string and i.time==tm_string:
            print("scheduled message running start")
            print(i.message)

            group_name = i.group
            account_id = i.account_id
            chat = i.message
            image = i.image
            sleep_time_first = i.delay
            type = i.type

            print(group_name, chat, account_id, sleep_time_first, datetime)
            TelegramAccount = Telegram_Accounts.objects.all().filter(id=account_id)
            phone = TelegramAccount[0].number
            api_id = TelegramAccount[0].hash_id
            api_hash = TelegramAccount[0].hash_key
            sleep_time = 2
            sleep_time_first = int(sleep_time_first)
            print(phone,api_hash,api_id)
            try:
                client = telegram_client(phone, api_id, api_hash)
                print('Account login successfully')
            except PhoneCodeInvalidError:
                sys.exit('You enter the wrong code.')
            # client(functions.channels.JoinChannelRequest(channel=group_name))
            print('Bot send message after '+str(sleep_time_first)+' seconds.')
            time.sleep(sleep_time_first)
            while True:
                try:
                    if type == "text":
                        client.send_message(group_name, str(chat))
                    elif type =="image":
                        picture = 'static/images/chat-pics/'+image 
                        client.send_file(group_name,picture)
                    elif type =="both":
                        picture = 'static/images/chat-pics/'+image 
                        client.send_file(group_name,picture,caption=chat)
                    print('Question send successfully. Bot sleep for '+str(sleep_time)+ ' seconds.')
                    client.disconnect()
                    t = Schedule_Messages.objects.get(id=i.id)
                    t.status = "completed"
                    t.save()
                    # now delete the picture from folder 
                    if type=="image":
                        fs = FileSystemStorage(location=TELEGRAM_CHAT_FOLDER) #defaults to   MEDIA_ROOT  
                        filename = fs.delete(image)
                    return HttpResponse('Chat send successfully') 
                except IndexError:         
                    client.disconnect()
                    print("All questions completed in "+group_name+' group.\n')
                    print()
                    return HttpResponse("All questions completed in "+group_name+' group.\n')
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)
                except FloodError:         
                    client.disconnect()
                    print('Due to many messages in group bot stops (Flood error).')
                    return HttpResponse('Due to many messages in group bot stops (Flood error).')
                    sys.exit()
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)
                except FloodWaitError:         
                    client.disconnect()
                    print('Due to many messages in group bot stops (Flood error).')
                    sys.exit()
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)
                except Exception as e:         
                    client.disconnect()
                    print(e)
                    return HttpResponse(e)
                    sys.exit()
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)

                except Exception as e:         
                    client.disconnect()
                    print(e)
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)


def bulk_user_dm_task():
    print("bulk dm user task..")
    data = Schedule_User_Messages.objects.all().filter(status="pending")
    for i in data:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
        tm_string = now.strftime("%H:%M")
        print(dt_string,tm_string)
        if i.date == dt_string and i.time==tm_string:
            print("scheduled message running start")
            member_names = i.member_names
            accounts = i.accounts
            accounts = json.loads(accounts)
            user_id = i.userid
            sleep_time_first = i.delay
            type = i.type
            limit_per_account = int(i.limit_per_account)
            print("limit per account is: ", limit_per_account)
            member_names = json.loads(member_names)
            start = 0
            limit = limit_per_account
            for x in accounts:
                TelegramAccount = Telegram_Accounts.objects.all().filter(number=x)
                phone = TelegramAccount[0].number
                api_id = TelegramAccount[0].hash_id
                api_hash = TelegramAccount[0].hash_key
                sleep_time = 2
                sleep_time_first = int(sleep_time_first)
                print("Logging In")
                print(phone,api_hash,api_id)
                try:
                    client = telegram_client(phone, api_id, api_hash)
                    print('Account login successfully')
                except PhoneCodeInvalidError:
                    sys.exit('You enter the wrong code.')
                time.sleep(sleep_time_first)
                # while True:
                try:
                    if type == "text":
                        chat = i.message
                        for member in range(start,limit):
                            check = client.send_message(member_names[member], str(chat))
                            if check:
                                # save log 
                                Cnow = datetime.now()
                                Cdate = now.strftime("%Y-%m-%d")
                                Ctime = now.strftime("%H:%M")
                                data = Logs_for_user_Messages(userid=user_id, message=chat, member_name=member_names[member], account = phone, type = type ,log="Message sent Successfully!",date=Cdate,time=Ctime)
                                data.save()
                                print("Message sent to "+ member_names[member] +" from account "+ phone)
                            else:
                                # save log 
                                Cnow = datetime.now()
                                Cdate = now.strftime("%Y-%m-%d")
                                Ctime = now.strftime("%H:%M")
                                data = Logs_for_user_Messages(userid=user_id, message=chat, member_name=member_names[member], account = phone, type = type ,log="Message Failed!",date=Cdate,time=Ctime)
                                data.save()
                                print("member is: ",member_names[member])
                                print("Message failed to "+ member_names[member] +" from account "+ phone)
                        start = start + limit
                        limit = limit + limit
                    elif type == "image":
                        image = i.image
                        for member in range(start,limit):
                            picture = 'static/images/chat-pics/'+image 
                            check = client.send_file(member_names[member],picture)
                            if check:
                                # save log 
                                Cnow = datetime.now()
                                Cdate = now.strftime("%Y-%m-%d")
                                Ctime = now.strftime("%H:%M")
                                data = Logs_for_user_Messages(userid=user_id, image=image,message="", member_name=member_names[member], account=phone, type=type ,log="Message sent Successfully!",date=Cdate,time=Ctime)
                                data.save()
                                print("Message sent to "+ member_names[member] +" from account "+ phone)
                            else:
                                # save log 
                                Cnow = datetime.now()
                                Cdate = now.strftime("%Y-%m-%d")
                                Ctime = now.strftime("%H:%M")
                                data = Logs_for_user_Messages(userid=user_id, image=image,message="", member_name=member_names[member], account=phone, type=type ,log="Message Failed!",date=Cdate,time=Ctime)
                                data.save()
                                print("Message failed to "+ member_names[member] +" from account "+ phone)
                        start = start + limit
                        limit = limit + limit
                    elif type == "both":
                        chat = i.message
                        image = i.image
                        for member in range(start,limit):
                            picture = 'static/images/chat-pics/'+image 
                            check = client.send_file(member_names[member],picture,caption=chat)
                            if check:
                                # save log 
                                Cnow = datetime.now()
                                Cdate = now.strftime("%Y-%m-%d")
                                Ctime = now.strftime("%H:%M")
                                data = Logs_for_user_Messages(userid=user_id, message=chat,image=image, member_name=member_names[member], account=phone, type=type ,log="Message sent Successfully!",date=Cdate,time=Ctime)
                                data.save()
                                print("Message sent to "+ member_names[member] +" from account "+ phone)
                            else:
                                # save log 
                                Cnow = datetime.now()
                                Cdate = now.strftime("%Y-%m-%d")
                                Ctime = now.strftime("%H:%M")
                                data = Logs_for_user_Messages(userid=user_id, message=chat,image=image, member_name=member_names[member], account=phone, type=type ,log="Message Failed!",date=Cdate,time=Ctime)
                                data.save()
                                print("Message failed to "+ member_names[member] +" from account "+ phone)
                        start = start + limit
                        limit = limit + limit
                    client.disconnect()
                except IndexError: 
                    # save log 
                    Cnow = datetime.now()
                    Cdate = now.strftime("%Y-%m-%d")
                    Ctime = now.strftime("%H:%M")
                    data = Logs_for_user_Messages(userid=user_id, image="",message=chat, member_name=member_names[member], account=phone, type=type ,log=IndexError,date=Cdate,time=Ctime)
                    data.save()           
                    client.disconnect()
                except FloodError: 
                    # save log 
                    Cnow = datetime.now()
                    Cdate = now.strftime("%Y-%m-%d")
                    Ctime = now.strftime("%H:%M")
                    data = Logs_for_user_Messages(userid=user_id, image="",message=chat, member_name=member_names[member], account=phone, type=type ,log=FloodError,date=Cdate,time=Ctime)
                    data.save()           
                    client.disconnect()
                except FloodWaitError: 
                    # save log 
                    Cnow = datetime.now()
                    Cdate = now.strftime("%Y-%m-%d")
                    Ctime = now.strftime("%H:%M")
                    data = Logs_for_user_Messages(userid=user_id, image="",message=chat, member_name=member_names[member], account=phone, type=type ,log=FloodWaitError,date=Cdate,time=Ctime)
                    data.save()           
                    client.disconnect()
                except Exception as e: 
                    # save log 
                    Cnow = datetime.now()
                    Cdate = now.strftime("%Y-%m-%d")
                    Ctime = now.strftime("%H:%M")
                    data = Logs_for_user_Messages(userid=user_id, image="",message=chat, member_name=member_names[member], account=phone, type=type ,log=e,date=Cdate,time=Ctime)
                    data.save()           
                    client.disconnect()
                    print(e)
            t = Schedule_User_Messages.objects.get(id=i.id)
            t.status = "completed"
            t.save()
            print("USER SCHEDULE COMPLETED")
            # now delete the picture from folder 
            # if type=="image":
            #     fs = FileSystemStorage(location=TELEGRAM_CHAT_FOLDER) #defaults to   MEDIA_ROOT  
            #     filename = fs.delete(chat)
            

def add_users_to_groups():
    print("add users to group..")
    data = Schedule_Add_Users.objects.all().filter(status="pending")
    for i in data:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
        tm_string = now.strftime("%H:%M")
        if i.date == dt_string and i.time==tm_string:
            print("scheduled add users to group running start")
            member_names = i.member_names
            user_id = i.userid
            your_group = i.your_group
            sleep_time_first = i.delay
            limit_per_account = int(i.limit_per_account)
            member_names = json.loads(member_names)
            accounts = i.accounts
            accounts = json.loads(accounts)
            start = 0
            limit = limit_per_account
            for x in accounts:
                TelegramAccount = Telegram_Accounts.objects.all().filter(number=x)
                phone = TelegramAccount[0].number
                api_id = TelegramAccount[0].hash_id
                api_hash = TelegramAccount[0].hash_key
                sleep_time = 2
                sleep_time_first = int(sleep_time_first)
                print(phone,api_hash,api_id)
                try:
                    print("Logging In")
                    client = telegram_client(phone, api_id, api_hash)
                    print('Account login successfully')
                except PhoneCodeInvalidError:
                    sys.exit('You enter the wrong code.')
                time.sleep(sleep_time_first)
                # while True:
                try:
                    for member in range(start,limit):
                    # for index, member in enumerate(member_names):   
                        try:
                            check = client(InviteToChannelRequest(your_group,[member_names[member]]))
                            if check:
                                # save log 
                                dnow = datetime.now()
                                ddate = now.strftime("%Y-%m-%d")
                                dtime = now.strftime("%H:%M")
                                data = Logs_for_add_user(userid=user_id, your_group=your_group, member_name=member_names[member], account = phone ,log="User add Successfully!",date=ddate,time=dtime)
                                data.save()
                                print(member_names[member]+" added  from account "+ phone)
                            else:
                                data = Logs_for_add_user(userid=user_id, your_group=your_group, member_name=member_names[member], account = phone ,log="User not added!",date=ddate,time=dtime)
                                data.save()

                        except Exception as e:
                            # save log 
                            dnow = datetime.now()
                            ddate = now.strftime("%Y-%m-%d")
                            dtime = now.strftime("%H:%M")
                            data = Logs_for_add_user(userid=user_id, your_group=your_group, member_name=member_names[member], account = phone ,log=e,date=ddate,time=dtime)
                            data.save()
                            print(member_names[member]+" not added  from account "+ phone)
                            print(e)
                    start = start + limit
                    limit = limit + limit
                    client.disconnect()
                    t = Schedule_Add_Users.objects.get(id=i.id)
                    t.status = "completed"
                    t.save()
                except IndexError:      
                    print("index error occured")
                    client.disconnect()
                except FloodError:      
                    print('Due to many messages in group bot stops (Flood error).')
                    client.disconnect()
                except Exception as e:   
                    print(e)
                    client.disconnect()
            
            print("ADD USERS SCHEDULE COMPLETED")

def telegram_client(phone, api_id, api_hash):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # client = TelegramClient(phone, api_id, api_hash)
    client = TelegramClient(phone, api_id, api_hash, loop=loop)
    time.sleep(3)
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))
    return client



# from jobs import some_task
# from views import Job1 as some_task
def start_jobs():
    scheduler = BackgroundScheduler()
    
    #Set cron to runs every 20 min.
    # cron_job = {'month': '*', 'day': '*', 'hour': '*', 'minute':'*/20'}
    
    #Add our task to scheduler.
    # scheduler.add_job(some_task, 'cron', **cron_job)
    scheduler.add_job(some_task, 'interval', seconds=30)
    scheduler.add_job(bulk_user_dm_task,'interval',seconds=30)
    scheduler.add_job(add_users_to_groups,'interval',seconds=30)
#And finally start.    
    scheduler.start()