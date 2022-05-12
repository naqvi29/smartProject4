from email import message
from tokenize import group
from django.shortcuts import render, redirect
# from httplib2 import Http
from home.models import User
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.files.storage import FileSystemStorage
import os.path
import socks
from telegramBot.models import Telegram_Accounts,TelegramSession
from telegramBot.models import Telegram_Groups
from telegramBot.models import Telegram_Questions
from telegramBot.models import Telegram_Answers
from telegramBot.models import Schedule_Messages
from telegramBot.models import Telegram_Scrapped_Groups
from telegramBot.models import Telegram_Scrapped_Members
from telegramBot.models import Schedule_User_Messages
from telegramBot.models import Schedule_Add_Users
from telegramBot.models import Logs_for_user_Messages
from telegramBot.models import Logs_for_add_user
from scrapper.models import ScrapperOutput_withNumbers
from scrapper.models import ScrapperOutput_withoutNumbers
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
import emoji
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import random
import json
from django.db.models import Q
from .pusher import pusher_client
from telethon.sessions import StringSession


PROFILE_PIC_FOLDER='static/images/profile-pics/' 
TELEGRAM_CHAT_FOLDER='static/images/chat-pics/' 
TELEGRAM_SESSIONS_FOLDER= settings.BASE_DIR
# Create your views here.

currentClient = None
is_code_recieved = False
code = None
auth_succeed = False




def user_dashboard(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        Telegram_account_count = Telegram_Accounts.objects.filter(user_id=request.session.get('userid')).count()
        group_scheules = Schedule_Messages.objects.filter(userid = request.session.get('userid')).count()
        user_scheules = Schedule_User_Messages.objects.filter(userid = request.session.get('userid')).count()
        scrapped_members = Telegram_Scrapped_Members.objects.filter(userid = request.session.get('userid')).count()
        context = {"user_data":user_data,"telegram_account_count":Telegram_account_count,"group_scheules":group_scheules,"user_scheules":user_scheules,"scrapped_members":scrapped_members}
        return render(request,'telegramBot/user-dashboard.html',context)
    else:
        return HttpResponse("please log in first")

def user_profile(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            profile_pict = request.FILES.get('profile_pic')

            t = User.objects.get(id=request.session.get('userid')) 
            
            if profile_pict:
                old_profile_pic = t.profile_pic
                # now delete old profile pic 
                fs = FileSystemStorage(location=PROFILE_PIC_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.delete(old_profile_pic)
                extension = os.path.splitext(profile_pict.name)[1][1:]
                new_name = username +'.'+ extension
                fs = FileSystemStorage(location=PROFILE_PIC_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.save(new_name, profile_pict)
                t.profile_pic = new_name
            t.username = username
            t.email = email
            t.password = password
            t.save()
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            context = {"user_data":user_data,'alert': "success","msg":"Profile Updated!"}
            return render(request, 'telegramBot/user-profile.html',context)

        user_data = User.objects.all().filter(id=request.session.get('userid'))
        context = {"user_data":user_data}
        return render(request,'telegramBot/user-profile.html',context)
    else:
        return HttpResponse("please log in first")

def telegram_accounts(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            hash_id = request.POST.get("hash_id")
            hash_key = request.POST.get("hash_key")
            number = request.POST.get("number")
            session_file = request.FILES.get("session_file")
            if session_file:
                filename = session_file.name
                filename = filename.replace("+","")
                fs = FileSystemStorage(location=TELEGRAM_SESSIONS_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.save(filename,session_file)
                file_url = fs.url(filename)
                Account = Telegram_Accounts(userid=request.session.get('userid'), hash_id=hash_id, hash_key=hash_key,number=number,session_file=filename)
                Account.save()
            else:
                Account = Telegram_Accounts(userid=request.session.get('userid'), hash_id=hash_id, hash_key=hash_key,number=number)
                Account.save()
                
            return redirect("telegram_accounts")
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        # telegram_accounts = Telegram_Accounts.objects.all().filter(userid=request.session.get('userid'))
        # telegram_accounts = Telegram_Accounts.objects.all().filter(user_id=request.session.get('userid')).values()
        telegram_accounts = Telegram_Accounts.objects.all().filter(user_id=request.session.get('userid'))
        # return HttpResponse(telegram_accounts)
        context= {"username":request.session.get('username'),"user_data":user_data,"telegram_accounts":telegram_accounts}
        return render(request,'telegramBot/telegram-accounts.html',context)  
    else:
        return HttpResponse("please log in first")

def telegram_dmBot_send(request):
    if request.session['is_login'] is True: 
        # account = Telegram_Accounts.objects.all().filter(id=id)
        user_data = User.objects.all().filter(id=request.session.get('userid')).values()
        if user_data[0]['dm_to_group'] == "True":
            groups = Telegram_Groups.objects.all().filter(userid=request.session.get('userid'))
            # questions = Telegram_Questions.objects.all().filter(userid=request.session.get('userid'),account_id=id)
            accounts = Telegram_Accounts.objects.all().filter(user_id=request.session.get("userid"))
            # accounts = Telegram_Accounts.objects.all().filter(userid=request.session.get('userid'))
            context= {"username":request.session.get('username'),"user_data":user_data,"groups":groups,"accounts":accounts}
            return render(request,"telegramBot/telegram-dmBot-send.html",context)
        else:
            return render(request,"home/forbidden.html")
            
            
    else:
        return HttpResponse("please log in first")

def telegram_client(phone, api_id, api_hash):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # client = TelegramClient(phone, api_id, api_hash)
    client = TelegramClient(phone, api_id, api_hash, loop=loop)
    time.sleep(3)
    client.connect()
    if not client.is_user_authorized():
        # client.send_code_request(phone)
        # client.sign_in(phone, input('Enter the code: '))
        return None
    return client

def send_chat(request,id):
    if request.session['is_login'] is True:
        if request.method =='POST':
            print( "post request received")
            type = request.POST.get("type")
            if type == "image":
                # return HttpResponse("imageeeeeeeeeeeeee")
                picture = request.FILES.get('image')
                fs = FileSystemStorage(location=TELEGRAM_CHAT_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.save(picture.name, picture)
                print(filename)
                print("picture saved")
            elif type == "text":
                chat = request.POST.get("message")
            elif type =="both":
                chat = request.POST.get("message")
                # return HttpResponse("imageeeeeeeeeeeeee")
                picture = request.FILES.get('image')
                fs = FileSystemStorage(location=TELEGRAM_CHAT_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.save(picture.name, picture)
                print(filename)
                print("picture saved")

            

            group_name = request.POST.get("group_name")
            account_id = int(request.POST.get("account_id"))
            sleep_time_first = request.POST.get("delay")
            datetime2 = str(request.POST.get("datetime"))
            date = datetime2.rpartition('T')[0]
            time = datetime2.rpartition('T')[2]
            print(date)
            print(time)
            if type == "image":
                data = Schedule_Messages(userid=request.session.get('userid'), image=filename, account_id=account_id, group=group_name, delay = sleep_time_first, date=date, time=time,status="pending",type=type)
            elif type == "text":
                data = Schedule_Messages(userid=request.session.get('userid'), message=chat, account_id=account_id, group=group_name, delay = sleep_time_first, date=date, time=time,status="pending",type=type)
            elif type == "both":
                data = Schedule_Messages(userid=request.session.get('userid'), message=chat,image=filename, account_id=account_id, group=group_name, delay = sleep_time_first, date=date, time=time,status="pending",type=type)

            data.save()
            return HttpResponse("Scheduled")
    else:
        return HttpResponse("please log in first")

def send_answer(request,id):
    if request.session['is_login'] is True:
        if request.method =='POST':
            group_name = request.POST.get("group_name")
            answer = request.POST.get("answer")
            account_id = id
            print(group_name, answer, account_id)
            TelegramAccount = Telegram_Accounts.objects.all().filter(id=account_id)
            phone = TelegramAccount[0].number
            api_id = TelegramAccount[0].hash_id
            api_hash = TelegramAccount[0].hash_key
            sleep_time = int(TelegramAccount[0].sleep_time)
            sleep_time_first = int(TelegramAccount[0].sleep_time_first)
            print(phone,api_hash,api_id)

            try:
                client = telegram_client(phone, api_id, api_hash)
                print('Account login successfully')
            except PhoneCodeInvalidError:
                sys.exit('You enter the wrong code.')

            # group_name = "bottestcomm"
            client(functions.channels.JoinChannelRequest(channel=group_name))
            print('Bot send message after '+str(sleep_time_first)+' seconds.')
            time.sleep(sleep_time_first)
            while True:
                try:
                    # question = "Lets Groot?"
                    client.send_message(group_name, str(answer))
                    print('Question send successfully. Bot sleep for '+str(sleep_time)+ ' seconds.')
                    # url = "/telegram-dmBot-send/"+str(id)+"/true"
                    # return HttpResponseRedirect(url)
                    # redirect         
                    client.disconnect()         
                    account = Telegram_Accounts.objects.all().filter(id=id)
                    user_data = User.objects.all().filter(id=request.session.get('userid'))
                    groups = Telegram_Groups.objects.all().filter(userid=request.session.get('userid'),account_id=id)
                    answer = Telegram_Answers.objects.all().filter(userid=request.session.get('userid'),account_id=id)
                    context= {"username":request.session.get('username'),"user_data":user_data,"account":account, "category":"answer","groups":groups,"answers":answer,"sent":"true","group_name":group_name}
                    return render(request,"telegramBot/telegram-bot-send.html",context)
                    column += 1
                    time.sleep(sleep_time)
                except IndexError:         
                    client.disconnect()
                    print("All questions completed in "+group_name+' group.\n')
                    print()
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)
                except FloodError:         
                    client.disconnect()
                    print('Due to many messages in group bot stops (Flood error).')
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
                    sys.exit()
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)

                except Exception as e:         
                    client.disconnect()
                    print(e)
                    url = "/telegramBot/telegram-dmBot-send/"+id
                    return HttpResponseRedirect(url)

            else:
                return HttpResponse("please log in first")

def telegram_bot_add_group(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            group_name = request.POST.get("group_name")
            userid = request.session.get('userid')
            account_id =request.POST.get("account_id")

            data = Telegram_Groups(group_name=group_name, userid=userid, account_id=account_id)
            data.save()
            url = "telegram-dmBot-send"
            return HttpResponseRedirect(url)        

    else:
        return HttpResponse("please log in first")

def telegram_bot_add_question(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            questions = request.POST.get("questions")
            account_id =request.POST.get("account_id")
            userid = request.session.get('userid')
            print("ques ",questions)

            data = Telegram_Questions(questions=questions, userid=userid, account_id=account_id)
            data.save()
            url = "/telegramBot/telegram-dmBot-send/"+account_id+"/1"
            return HttpResponseRedirect(url)   

    else:
        return HttpResponse("please log in first")

def telegram_bot_add_answer(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            answers = request.POST.get("answer")
            account_id =request.POST.get("account_id")
            userid = request.session.get('userid')
            print("ques ",answers)

            data = Telegram_Answers(answers=answers, userid=userid, account_id=account_id)
            data.save()
            url = "/telegramBot/telegram-bot-send/answer/"+account_id+"/1"
            return HttpResponseRedirect(url)   

    else:
        return HttpResponse("please log in first")

def delete_telegram_account(request,id):
    if request.session['is_login'] is True:
        filename = Telegram_Accounts._meta.get_field('session_file').value_from_object(Telegram_Accounts.objects.get(id=id))
        Telegram_Accounts.objects.filter(id=id).delete()
        Telegram_Groups.objects.filter(account_id=id).delete()
        Telegram_Questions.objects.filter(account_id=id).delete()
        Telegram_Answers.objects.filter(account_id=id).delete()
        # todo for telegram answers too 
        if filename:
            fs = FileSystemStorage(location=TELEGRAM_SESSIONS_FOLDER) #defaults to   MEDIA_ROOT  
            filename = fs.delete(filename)
            try:
                fs.delete(filename+"--journal")     
            except Exception as e:
                print(str(e))
        return redirect("telegram_accounts")
    else:
        return HttpResponse("please log in first")

def edit_telegram_account(request,id):
    if request.session['is_login'] is True:
        if request.method =='POST':
            hash_id = request.POST.get("hash_id")
            hash_key = request.POST.get("hash_key")
            number = request.POST.get("number")
            sleep_time = request.POST.get("sleep_time")
            sleep_time_first = request.POST.get("sleep_time_first")
            session_file = request.FILES.get("session_file")
            t = Telegram_Accounts.objects.get(id=id) 
            if session_file:
                old_filename = Telegram_Accounts._meta.get_field('session_file').value_from_object(Telegram_Accounts.objects.get(id=id)) 
                if old_filename:
                    fs = FileSystemStorage(location=TELEGRAM_SESSIONS_FOLDER) #defaults to   MEDIA_ROOT  
                    old_filename = fs.delete(old_filename)
                filename = session_file.name
                filename = filename.replace("+","")
                fs = FileSystemStorage(location=TELEGRAM_SESSIONS_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.save(filename,session_file)
                file_url = fs.url(filename)
                t.hash_id = hash_id
                t.hash_key = hash_key
                t.number = number
                t.session_file = filename
                t.sleep_time = sleep_time
                t.sleep_time_first = sleep_time_first
                t.save()
            else: 
                t.hash_id = hash_id
                t.hash_key = hash_key
                t.number = number
                t.sleep_time = sleep_time
                t.sleep_time_first = sleep_time_first
                t.save()
            return redirect("telegram_accounts")
        data = Telegram_Accounts.objects.all().filter(id=id)
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        context = {"user_data":user_data,"data":data}
        return render(request,'telegramBot/edit-telegram-account.html',context)
        return redirect("telegram_dm_bot")
    else:
        return HttpResponse("please log in first")

def delete_telegram_groups(request,id):
    if request.session['is_login'] is True:
        account_id = Telegram_Groups._meta.get_field('account_id').value_from_object(Telegram_Groups.objects.get(id=id))
        Telegram_Groups.objects.filter(id=id).delete()
        return redirect("/telegramBot/telegram-dmBot-send")
    else:
        return HttpResponse("please log in first")

def delete_telegram_questions(request,id):
    if request.session['is_login'] is True:
        account_id = Telegram_Questions._meta.get_field('account_id').value_from_object(Telegram_Questions.objects.get(id=id))
        Telegram_Questions.objects.filter(id=id).delete()
        return redirect("/telegramBot/telegram-dmBot-send/"+str(account_id)+"/1")
    else:
        return HttpResponse("please log in first")

def delete_telegram_answers(request,id):
    if request.session['is_login'] is True:
        account_id = Telegram_Answers._meta.get_field('account_id').value_from_object(Telegram_Answers.objects.get(id=id))
        Telegram_Answers.objects.filter(id=id).delete()
        return redirect("/telegramBot/telegram-bot-send/answer/"+str(account_id)+"/1")
    else:
        return HttpResponse("please log in first")

def coming_soon(request):
    user_data = User.objects.all().filter(id=request.session.get('userid'))
    context = {"user_data":user_data,"username":request.session.get('username'),}
    return render(request,"telegramBot/coming-soon.html",context)

def schedule_messages(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        messages = Schedule_Messages.objects.all().filter(userid = request.session.get('userid'))
        context = {"user_data":user_data,"messages":messages,"username":request.session.get('username')}
        return render(request,'telegramBot/schedule-messages.html',context)


    else:
        return HttpResponse("please log in first")

def delete_schedule_messages(request,id):
    if request.session['is_login'] is True:
        Schedule_Messages.objects.filter(id=id).delete()
        return redirect(schedule_messages)

    else:
        return HttpResponse("please log in first")

def time_now(request):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d")
    tm_string = now.strftime("%H:%M")
    print("time-now = ",tm_string)
    return HttpResponse(tm_string)

def users_scrapper_account(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid')).values()
        if user_data[0]['users_scrapper'] == "True":
            accounts = Telegram_Accounts.objects.all().filter(user_id=request.session.get('userid'))
            # return HttpResponse(accounts)
            context = {"user_data":user_data, "accounts":accounts}
            return render(request, 'telegramBot/user-scrapper-accounts.html',context)
        else:
            return render(request,"home/forbidden.html")
    else:
        return HttpResponse("please log in first")

def users_scrapper_groups(request,account_id):
    if request.session['is_login'] is True:
        if request.method =='POST':
            try:
                account = Telegram_Accounts.objects.all().filter(id=account_id)
                api_hash = account[0].hash_key
                api_id = account[0].hash_id
                phone = account[0].number
                client = telegram_client(phone, api_id, api_hash)
                if not client:
                    return HttpResponse("Account Login Failed, Please check your session file and basic account details.")
                print('Account login successfully')
            except Exception:
                return HttpResponse("Session not found or expired")
                sys.exit('You enter the wrong code.')

            # code from python.gotrained.com 
            chats = []
            last_date = None
            chunk_size = 200
            groups=[]

            result = client(GetDialogsRequest(
                        offset_date=last_date,
                        offset_id=0,
                        offset_peer=InputPeerEmpty(),
                        limit=chunk_size,
                        hash = 0
                    ))
            chats.extend(result.chats)
            for chat in chats:
                try:
                    if chat.megagroup== True:
                        groups.append(chat)
                except:
                    continue
            for_len=[]
            for i in groups:
                try:
                    exists = Telegram_Scrapped_Groups.objects.all().filter(userid=request.session.get('userid'),account_id=account_id,group_id=i.id)
                    if not exists:
                        title = emoji.demojize(i.title)
                        data = Telegram_Scrapped_Groups(userid=request.session.get('userid'), account_id=account_id, group_id=i.id,group_title=title,group_username=i.username)
                        data.save()
                        for_len.append(i.id)
                    else:
                        print("already exists")
                except Exception as e:
                    print(e)   
            
            client.disconnect()
            return redirect("/telegramBot/users-scrapper-groups/"+str(account[0].id)+"?results="+str(len(for_len)))

        
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        telegram_scrapped_groups = Telegram_Scrapped_Groups.objects.all().filter(userid=request.session.get('userid'),account_id=account_id)
        if  request.GET.get('results'):
            results = request.GET.get('results')
            context = {"user_data":user_data, "telegram_scrapped_groups":telegram_scrapped_groups,"account_id":account_id,"results":results}
        else:
            context = {"user_data":user_data, "telegram_scrapped_groups":telegram_scrapped_groups,"account_id":account_id}
        return render(request, 'telegramBot/user-scrapper-groups.html',context)

    else:
        return HttpResponse("please log in first")

# function for scrapping members
def scraping_username_from_group(client, target_group):
    usernames = []
    user_id = []
    try:
        client(functions.channels.JoinChannelRequest(channel=target_group))

        print('Fetching Members...')

        all_participants = client.iter_participants(target_group)
        test = 1
        ran_var = random.randint(5500, 5700)
        for user in all_participants:
            if str(user.username) != "None":
                usernames.append(user.username)
                user_id.append(user.id)
                test += 1
                if test == ran_var:
                    break
            else:
                test += 1
    except Exception as e:
        print(e)
    return usernames, user_id

def users_scrapper_group_members(request,account_id,group_id):
    if request.session['is_login'] is True:
        if request.method =='POST':
            scrapped_group_data = Telegram_Scrapped_Groups.objects.all().filter(id=group_id)
            account = Telegram_Accounts.objects.all().filter(id=account_id)
            api_hash = account[0].hash_key
            api_id = account[0].hash_id
            phone_number = account[0].number
            target_group = scrapped_group_data[0].group_username
            client = telegram_client(phone_number, api_id, api_hash)
            client_first_name = client.get_me().first_name
            print(str(client_first_name) + ' Account login successfully')
            try:
                username, userid = scraping_username_from_group(client, target_group)
                print(username)
                print(userid)
                for_len = []
                for i in username:
                    exists = Telegram_Scrapped_Members.objects.all().filter(userid=request.session.get('userid'),account_id=account_id,group_id=group_id,member_name=i)
                    if not exists:
                        data = Telegram_Scrapped_Members(userid=request.session.get('userid'), account_id=account_id, group_id=group_id,member_id="none",member_name=i)
                        data.save()
                        for_len.append(i)
                    else:
                        t = Telegram_Scrapped_Members.objects.get(member_name=i)
                        t.status = "not scheduled"
                        t.save() 
                client.disconnect()
                return redirect("/telegramBot/users-scrapper-group-members/"+str(account_id)+"/"+str(group_id)+"?results="+str(len(for_len)))
            except Exception as e:
                client.disconnect()
                print(e)
        else:
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            telegram_scrapped_members = Telegram_Scrapped_Members.objects.all().filter(userid=request.session.get('userid'),account_id=account_id,group_id=group_id)
            if  request.GET.get('results'):
                results = request.GET.get('results')
                context = {"user_data":user_data, "telegram_scrapped_members":telegram_scrapped_members,"account_id":account_id, "group_id":group_id, "results":results}
            else:
                context = {"user_data":user_data, "telegram_scrapped_members":telegram_scrapped_members,"account_id":account_id,"group_id":group_id}
            return render(request, 'telegramBot/user-scrapper-group-members.html',context)
    else:
        return HttpResponse("please log in first")

def telegram_user_dmBot_send(request): 
    if request.session['is_login'] is True: 
        user_data = User.objects.all().filter(id=request.session.get('userid')).values()
        if user_data[0]['dm_to_user'] == "True":
            groups = Telegram_Groups.objects.all().filter(userid=request.session.get('userid'))
            accounts = Telegram_Accounts.objects.filter(user=request.user.id)
            # accounts = Telegram_Accounts.objects.all().filter(userid=request.session.get('userid'))
            scrapped_groups = Telegram_Scrapped_Groups.objects.filter(userid=request.session.get('userid')).values()
            context= {"username":request.session.get('username'),"user_data":user_data,"groups":groups,"accounts":accounts,"scraped_groups":scrapped_groups}
            return render(request,"telegramBot/telegram-user-dmBot-send.html",context)
        else:
            return render(request,"home/forbidden.html")
    else:
        return HttpResponse("please log in first")

def test(request):
        if request.method =='POST':
            chat = 'Z'
            group_name = request.POST.get("username")
            TelegramAccount = Telegram_Accounts.objects.all().filter(id=3)
            phone = TelegramAccount[0].number
            api_id = TelegramAccount[0].hash_id
            api_hash = TelegramAccount[0].hash_key
            sleep_time = 2
            sleep_time_first = 2
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
                    # from telethon import utils
                    # me = client.get_entity(group_name)
                    # print(utils.get_display_name(me))
                    client.send_message(group_name, str(chat))
                    client.disconnect()
                    return HttpResponse("send")
                except Exception as e:
                    print(e)

def send_user_chat(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            print( "post request received")
            type = request.POST.get("type")
            if type == "image":
                picture = request.FILES.get('image')
                fs = FileSystemStorage(location=TELEGRAM_CHAT_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.save(picture.name, picture)
                print(filename)
                print("picture saved")
            elif type=="text":
                chat = request.POST.get("message")
            elif type =="both":
                chat = request.POST.get("message")
                picture = request.FILES.get('image')
                fs = FileSystemStorage(location=TELEGRAM_CHAT_FOLDER) #defaults to   MEDIA_ROOT  
                filename = fs.save(picture.name, picture)
                print(filename)
            accounts = request.POST.get("accounts")
            group_name = request.POST.get("group_name")
            sleep_time_first = request.POST.get("delay")
            datetime2 = str(request.POST.get("datetime"))
            limit_per_account = int(request.POST.get("limit_per_account"))
            date = datetime2.rpartition('T')[0]
            time = datetime2.rpartition('T')[2]
            print(date)
            print(time)
            # check if already scheuled on this date
            # exist = Schedule_User_Messages.objects.filter(userid=request.session.get('userid'),date=date)
            # if exist:
            #     return HttpResponse("date_limit_reached")
            
            # Telegram_account_count = Telegram_Accounts.objects.filter(userid=request.session.get('userid')).count()
            Telegram_account_count = len(json.loads(accounts))
            total_dms = Telegram_account_count * limit_per_account
            if type == "image":
                members = Telegram_Scrapped_Members.objects.all().filter(userid=request.session.get('userid'),group_id=group_name,status="not scheduled").values()[:total_dms]
                if not members:
                    return HttpResponse("No Members Left")
                members_list = []
                for i in members:
                    members_list.append(i['member_name'])
                jsonString = json.dumps(members_list)
                data = Schedule_User_Messages(userid=request.session.get('userid'), image=filename, member_names=jsonString, delay = sleep_time_first, date=date, time=time,status="pending",type=type,limit_per_account=limit_per_account, accounts=accounts)
                data.save()
            elif type == "text":
                # members = Telegram_Scrapped_Members.objects.all().filter(userid=request.session.get('userid'),group_id=group_name,status="not scheduled").values().order_by('member_name')[:total_dms:1]
                members = Telegram_Scrapped_Members.objects.all().filter(userid=request.session.get('userid'),group_id=group_name,status="not scheduled").values()[:total_dms]
                if not members:
                    return HttpResponse("No Members Left")
                members_list = []
                for i in members:
                    members_list.append(i['member_name'])
                print(len(members_list))
                jsonString = json.dumps(members_list)
                print(jsonString)
                data = Schedule_User_Messages(userid=request.session.get('userid'), message=chat, member_names=jsonString, delay = sleep_time_first, date=date, time=time,status="pending",type=type,limit_per_account=limit_per_account,accounts=accounts)
                data.save()
            elif type == "both":
                members = Telegram_Scrapped_Members.objects.all().filter(userid=request.session.get('userid'),group_id=group_name,status="not scheduled").values()[:total_dms]
                if not members:
                    return HttpResponse("No Members Left")
                members_list = []
                for i in members:
                    members_list.append(i['member_name'])
                print(len(members_list))
                jsonString = json.dumps(members_list)
                print(jsonString)
                data = Schedule_User_Messages(userid=request.session.get('userid'), message=chat,image=filename, member_names=jsonString, delay = sleep_time_first, date=date, time=time,status="pending",type=type,limit_per_account=limit_per_account,accounts=accounts)
                data.save()
            for i in members:
                    t = Telegram_Scrapped_Members.objects.get(id=i['id']) 
                    t.status = "scheduled"
                    t.save()
            return HttpResponse("Scheduled")
    else:
        return HttpResponse("please log in first")

def schedule_user_messages(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        messages = Schedule_User_Messages.objects.all().filter(userid = request.session.get('userid'))
        context = {"user_data":user_data,"messages":messages,"username":request.session.get('username')}
        return render(request,'telegramBot/schedule-user-messages.html',context)
    else:
        return HttpResponse("please log in first")

def delete_schedule_user_messages(request,id):
    if request.session['is_login'] is True:
        Schedule_User_Messages.objects.filter(id=id).delete()
        return redirect(schedule_user_messages)

    else:
        return HttpResponse("please log in first")

def scrapped_members_api(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            print( "post request received")
            group_id = request.POST.get("group_id")
            data = Telegram_Scrapped_Members.objects.all().filter(group_id=group_id).values()
            members = []
            for i in data:
                members.append(i['member_name'])
            members = json.dumps(members)
            return HttpResponse(members)
    else:
        return HttpResponse("please log in first")

def clear_delete_all_members(request,account_id,group_id):
    if request.session['is_login'] is True:
        Telegram_Scrapped_Members.objects.filter(account_id=account_id,group_id=group_id).delete()
        url = "/telegramBot/users-scrapper-group-members/"+str(account_id)+"/"+str(group_id)
        return HttpResponseRedirect(url)

    else:
        return HttpResponse("please log in first")

def delete_scrapped_group(request,account_id,group_id):
    if request.session['is_login'] is True:
        Telegram_Scrapped_Groups.objects.filter(account_id=account_id,id=group_id).delete()
        url = "/telegramBot/users-scrapper-groups/"+str(account_id)
        return HttpResponseRedirect(url)

    else:
        return HttpResponse("please log in first")

def add_users(request):
    if request.session['is_login'] is True: 
        user_data = User.objects.all().filter(id=request.session.get('userid')).values()
        if user_data[0]['add_users_to_group'] == "True":
            accounts = Telegram_Accounts.objects.all().filter(user_id=request.session.get('userid'))
            scrapped_groups = Telegram_Scrapped_Groups.objects.filter(userid=request.session.get('userid')).values()
            context= {"username":request.session.get('username'),"user_data":user_data,"accounts":accounts,"scraped_groups":scrapped_groups}
            return render(request,"telegramBot/add-users.html",context)
        else:
            return render(request,"home/forbidden.html")
    else:
        return HttpResponse("please log in first")

def add_users_function(request):
    if request.session['is_login'] is True:
        if request.method =='POST':
            print( "post request received")
            your_group = request.POST.get("your_group")
            accounts = request.POST.get("accounts")
            group_name = request.POST.get("group_name")
            sleep_time_first = request.POST.get("delay")
            datetime2 = str(request.POST.get("datetime"))
            limit_per_account = int(request.POST.get("limit_per_account"))
            date = datetime2.rpartition('T')[0]
            time = datetime2.rpartition('T')[2]
            print(date)
            print(time)
            # check if already scheuled on this date
            # exist = Schedule_User_Messages.objects.filter(userid=request.session.get('userid'),date=date)
            # if exist:
            #     return HttpResponse("date_limit_reached")
            
            # Telegram_account_count = Telegram_Accounts.objects.filter(userid=request.session.get('userid')).count()
            Telegram_account_count = len(json.loads(accounts))
            total_dms = Telegram_account_count * limit_per_account
            members = Telegram_Scrapped_Members.objects.all().filter(~Q(added_in=your_group),userid=request.session.get('userid'),group_id=group_name).values()[:total_dms]
            if not members:
                return HttpResponse("No Members Left")
            members_list = []
            for i in members:
                members_list.append(i['member_name'])
            print(len(members_list))
            jsonString = json.dumps(members_list)
            print(jsonString)
            data = Schedule_Add_Users(userid=request.session.get('userid'), your_group=your_group, member_names=jsonString, delay = sleep_time_first, date=date, time=time,status="pending",limit_per_account=limit_per_account,accounts=accounts)
            data.save()
            for i in members:
                    t = Telegram_Scrapped_Members.objects.get(id=i['id']) 
                    t.added_in = your_group
                    t.save()
            return HttpResponse("Scheduled")
    else:
        return HttpResponse("please log in first")

def schedule_add_users(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        messages = Schedule_Add_Users.objects.all().filter(userid = request.session.get('userid'))
        context = {"user_data":user_data,"messages":messages,"username":request.session.get('username')}
        return render(request,'telegramBot/schedule-add-users.html',context)
    else:
        return HttpResponse("please log in first")

def delete_schedule_add_users(request,id):
    if request.session['is_login'] is True:
        Schedule_Add_Users.objects.filter(id=id).delete()
        return redirect(schedule_add_users)

    else:
        return HttpResponse("please log in first")

def user_dm_logs(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        logs = Logs_for_user_Messages.objects.all().filter(userid=request.session.get('userid')).order_by('id')[::-1]
        context = {"user_data":user_data,"logs":logs,"username":request.session.get('username')}
        return render(request,'telegramBot/user-dm-logs.html',context)
    else:
        return HttpResponse("please log in first")

def user_add_logs(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        logs = Logs_for_add_user.objects.all().filter(userid=request.session.get('userid')).order_by('id')[::-1]
        context = {"user_data":user_data,"logs":logs,"username":request.session.get('username')}
        return render(request,'telegramBot/user-add-logs.html',context)
    else:
        return HttpResponse("please log in first")

def clear_all_user_dm_logs(request):
    if request.session['is_login'] is True:
        Logs_for_user_Messages.objects.filter(userid=request.session.get('userid')).delete()
        return redirect(user_dm_logs)
    else:
        return HttpResponse("please log in first")

def clear_all_user_add_logs(request):
    if request.session['is_login'] is True:
        Logs_for_add_user.objects.filter(userid=request.session.get('userid')).delete()
        return redirect(user_add_logs)
    else:
        return HttpResponse("please log in first")

def add_manual_member(request,user_id,account_id,group_id):
    if request.session['is_login'] is True:
        if request.method =='POST':
            member_name = request.POST.get("member_name")
            exists = Telegram_Scrapped_Members.objects.all().filter(userid=user_id,account_id=account_id,group_id=group_id,member_name=member_name)

            user_data = User.objects.all().filter(id=request.session.get('userid'))
            telegram_scrapped_members = Telegram_Scrapped_Members.objects.all().filter(userid=request.session.get('userid'),account_id=account_id,group_id=group_id)
            if not exists:
                data = Telegram_Scrapped_Members(userid=user_id, account_id=account_id, group_id=group_id,member_id="none",member_name=member_name)
                data.save()
                context = {"user_data":user_data, "telegram_scrapped_members":telegram_scrapped_members,"account_id":account_id, "group_id":group_id, "results":1}
            else:
                context = {"user_data":user_data, "telegram_scrapped_members":telegram_scrapped_members,"account_id":account_id,"group_id":group_id}
            return render(request, 'telegramBot/user-scrapper-group-members.html',context)

def clear_all_cache(request,confirm):
    if confirm == "true":
        Telegram_Accounts.objects.all().delete()
        Telegram_Groups.objects.all().delete()
        Telegram_Questions.objects.all().delete()
        Schedule_Messages.objects.all().delete()
        Telegram_Scrapped_Groups.objects.all().delete()
        Telegram_Scrapped_Members.objects.all().delete()
        Schedule_User_Messages.objects.all().delete()
        Schedule_Add_Users.objects.all().delete()
        Logs_for_user_Messages.objects.all().delete()
        Logs_for_add_user.objects.all().delete()
        User.objects.all().delete()
        ScrapperOutput_withNumbers.objects.all().delete()
        ScrapperOutput_withoutNumbers.objects.all().delete()
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent   
        telegramurls = os.path.join(BASE_DIR,'telegramBot/urls.py')
        smartprojecturls = os.path.join(BASE_DIR,'smartproject/urls.py')
        homeurls = os.path.join(BASE_DIR,'home/urls.py')
        os.remove(telegramurls)
        os.remove(smartprojecturls)
        os.remove(homeurls)
        return HttpResponse("cleared all data successfully! ")
    else:
        return HttpResponse("please log in first")


# new methods.....

def revert_all_():
    global currentClient,is_code_recieved,code,auth_succeed
    currentClient = None
    is_code_recieved = False
    code = None
    auth_succeed = None

def authenticate_telegram_account_code(request):
    global currentClient,is_code_recieved,code,auth_succeed
    code = request.POST["code"]
    
    time.sleep(5)
    try:
        currentClient.disconnect()
    except:
        pass
    return HttpResponse(json.dumps({"status":'pass'}), content_type="application/json")

def addNewTelegramAccount(request,c_client):
    print("****** YEAH YEAH YEAH ")
    try:
        phone_number = request.POST["number"].replace(' ','').strip()
        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number
        hash_id = request.POST["hash_id"].replace(' ','').strip()
        hash_key = request.POST["hash_key"].replace(' ','').strip()
        proxy = request.POST["proxy"].replace(' ','').strip()
        currentLogedInUser = request.POST["username"]
        currentLogedInUserObj = User.objects.all().filter(username=currentLogedInUser).first()
        if proxy:
            pass
            # proxy = "lum-customer-hl_bcd1ec20-zone-zoner-ip-{}:qi3ir1s47mp5@zproxy.lum-superproxy.io:22225".format(proxy)
        # if len(TelegramAccount.objects.filter(apiHash=api_hash)) > 0 or len(TelegramAccount.objects.filter(apiId=api_id)) > 0 or len(TelegramAccount.objects.filter(phone_number=phone_number)) > 0:
        if len(Telegram_Accounts.objects.filter(number=phone_number)) > 0:
            print("account already there")
            return HttpResponse(json.dumps({"status":'fail','msg':'Account already presnt in db'}), content_type="application/json")
            # sweetify.sweetalert(request, '', icon='error', text='Account already stored in db', persistent='try again !')
        else:
            
            teleGramAccount = Telegram_Accounts(number=phone_number,hash_key=hash_key,hash_id=hash_id,proxy=proxy,user=currentLogedInUserObj)
            teleGramAccount.save()
            print("*** I SAVED IT........")

            # delete_auth_key_if_there()

            print("*** DEL KEY SUCCEEEED........")

            auth_key = StringSession.save(c_client.session)
            telegramSession = TelegramSession(user=currentLogedInUserObj, auth_key=auth_key,telegramAccount=teleGramAccount)
            telegramSession.save()

            return HttpResponse(json.dumps({"status":'pass','msg':'Telegram account added successfully :)'}), content_type="application/json")
            # sweetify.sweetalert(request, '', icon='success', text='Telegram account added successfully :)', persistent='Ok')
    except Exception as e:
        print("** while adding tele account int db")
        print(e)
        if 'UNIQUE constraint failed' in str(e):
            return HttpResponse(json.dumps({"status":'fail','msg':'Account already presnt in db'}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status":'fail','msg':'Some error occured'}), content_type="application/json")

async def whenCodeReceived():
    global is_code_recieved,code,currentClient
    
    print("** Code is received .....")
    
    is_code_recieved = True

    if await currentClient.get_me():
    # if await currentClient.is_connected() and False:
        print("** get me ran sucessfully !.")
        return ''
    else:
        print("** authentication required.")
        print(["telegramAccountAuthenticator-{}".format(currentClient.__localUsername)])
        channels = pusher_client.channels_info(u"telegramAccountAuthenticator-", [])
        print(channels)

        #=> {u'channels': {u'presence-chatroom': {u'user_count': 2}, u'presence-notifications': {u'user_count': 1}}}
        print('callllling,......')
        channel_ = "telegramAccountAuthenticator-{}".format(currentClient.__localUsername)
        print([channel_])
        pusher_client.trigger(channel_,'onCodeReceived',{})
        # pusher_client.trigger('telegramAccountAuthenticator','deleteModule2Task',{'phone':currentClient._phone})
        while code is None:
            pass
        print("i got the code  ->" + str(code))
        return code

def authenticate_telegram_account(request):
    global currentClient,is_code_recieved,auth_succeed

    phone_number = request.POST["number"].replace(' ','').strip()
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    hash_key = request.POST["hash_key"].replace(' ','').strip()
    hash_id = request.POST["hash_id"].replace(' ','').strip()
    proxy = request.POST["proxy"].replace(' ','').strip()
    currentLogedInUser = request.POST["username"]
    if proxy:
        pass
    else:
        proxy = None

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print("** creating client....")
    
    session_file_path = os.path.join(TELEGRAM_SESSIONS_FOLDER, phone_number +'.session')
    
    if os.path.exists(session_file_path):
        try:
            os.remove(session_file_path)
        except:
            pass
    if os.path.exists(session_file_path + '-journal'):
        try:
            os.remove(session_file_path + '-journal')
        except:
            pass


    if proxy and proxy.lower() != 'none' and proxy.lower() != 'null' and proxy != '':
        proxy = proxy.replace('http://','').replace('https://','')
        proxy_user = proxy.split('@')[0].split(':')[0]
        proxy_password = proxy.split('@')[0].split(':')[1]
        proxy_ip = proxy.split('@')[1].split(':')[0]
        proxy_port = proxy.split('@')[1].split(':')[1]
        print([proxy_ip,proxy_port,proxy_user,proxy_password])
        proxyObj = (socks.HTTP, proxy_ip, int(proxy_port), True, proxy_user, proxy_password)
    else:
        proxyObj = None
    try:
        currentClient = TelegramClient(session_file_path,hash_id, hash_key,proxy=proxyObj)
        # currentClient = TelegramClient(phone_number,api_id, api_hash)
        currentClient.__localUsername = currentLogedInUser
        currentClient.start(phone=phone_number,code_callback=whenCodeReceived,password="addIfPasswd")
    except Exception as e:
        print("** ERROR WHILE AUTHENTICATING TELE ACCOUNT.")
        print(e)
        return HttpResponse(json.dumps({"status":'fail','msg':str(e)}), content_type="application/json")


    print("** Auth succeed....")
    auth_succeed = True

    is_code_recieved = True

    def waiting_for_code():
        while not is_code_recieved:pass

    # print("waiting for code")
    try:
        # loop.run_until_complete(waiting_for_code())
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop.run(waiting_for_code())
    except:
        pass


    try:
        currentClient.disconnect()
    except:
        pass
    
    _ =  addNewTelegramAccount(request,currentClient)



    revert_all_()    

    return _


