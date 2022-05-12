from django.shortcuts import render, redirect
from home.models import User
from scrapper.models import ScrapperOutput_withNumbers
from scrapper.models import ScrapperOutput_withoutNumbers
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os.path
import json
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time


PROFILE_PIC_FOLDER='static/images/profile-pics/' 

# Create your views here

def user_dashboard(request):
    if request.session['is_login'] is True:
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        results1_count = ScrapperOutput_withNumbers.objects.filter(userid=request.session.get('userid')).count()
        results2_count = ScrapperOutput_withoutNumbers.objects.filter(userid=request.session.get('userid')).count()
        total_results = results1_count + results2_count
        context = {"user_data":user_data,"withnumbers":results1_count,"withoutnumbers":results2_count,"total_results":total_results}
        return render(request,'scrapper/user-dashboard.html',context)
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
            results1_count = ScrapperOutput_withNumbers.objects.filter(userid=request.session.get('userid')).count()
            results2_count = ScrapperOutput_withoutNumbers.objects.filter(userid=request.session.get('userid')).count()
            total_results = results1_count + results2_count
            context = {"user_data":user_data,"total_results":total_results,"withnumbers":results1_count,"withoutnumbers":results2_count,'alert': "success","msg":"Profile Updated!"}
            return render(request, 'scrapper/user-profile.html',context)

        user_data = User.objects.all().filter(id=request.session.get('userid'))
        results1_count = ScrapperOutput_withNumbers.objects.filter(userid=request.session.get('userid')).count()
        results2_count = ScrapperOutput_withoutNumbers.objects.filter(userid=request.session.get('userid')).count()
        total_results = results1_count + results2_count
        context = {"user_data":user_data,"total_results":total_results,"withnumbers":results1_count,"withoutnumbers":results2_count}
        return render(request,'scrapper/user-profile.html',context)
    else:
        return HttpResponse("please log in first")

def scrapper_bot(request):
    try:        
        if request.session['is_login'] is True:
            if request.method =='POST':
                link = request.POST.get("link")
                links = json.loads(link)
                link = links[0]
                userid = request.session.get('userid')
                urls = []
                base_url = 'https://www.autoscout24.it'
                s = HTMLSession()
                # for link in links:
                counter = 1
                while True:
                    index = link.find('page=')
                    new_url = link.replace(link[index + 5],str(counter))
                    r = s.get(new_url)
                    # print("r: ",r)
                    soup = BeautifulSoup(r.content, 'html.parser')
                    items =  soup.select('div.cldt-summary-full-item-main')
                    print("page : ",counter,"status_code : ",r.status_code)
                    for item in items:
                        urls.append(base_url + item.a['href'])
                    counter += 1
                    if r.status_code != 200:
                        break
                print("urls: ",urls)
                for url in urls:
                    r= s.get(url)
                    soup2 = BeautifulSoup(r.content,'html.parser')
                    try:
                        name =soup2.select_one('main > div.cldt-headline h1').text.replace('\n', ' ')
                        print(name)
                    except:
                        name =''
                    try:
                        price =soup2.select_one('.cldt-stage-data h2').text.strip()
                        price = price.replace('€','')
                        price = price.replace(' ','')
                        price = price.replace(',','')
                        price = price.replace('-','')
                        price = float(price)
                    except:
                        price =''
                    try:
                        kilometers =soup2.select_one('.cldt-stage-primary-keyfact').text.strip()
                        kilometers = kilometers.replace('km','')
                        kilometers = kilometers.replace(' ','')
                        kilometers = float(kilometers)
                    except:
                        kilometers= ('')
                    try:

                        image =soup2.select_one('.gallery-picture').img['src']
                    except:
                        image =''

                    try:
                        power =soup2.select_one('.cldt-stage-basic-data-and-highlights div:nth-of-type(3)').text.strip().replace('\n',' ')
                    except:
                        power =''
                    try:
                        date =soup2.select_one('#basicDataFirstRegistrationValue').text
                    except:
                        date =''

                    number =soup2.select_one('a.cldt-stage-call-btn')
                    
                    if number is None:
                        Scrapper_Outputs = ScrapperOutput_withoutNumbers(userid=userid, links=url, Name=name,Price=price, Kilometers=kilometers, Date=date,Power=power, Image=image)
                        Scrapper_Outputs.save()
                    else:
                        Scrapper_Outputs = ScrapperOutput_withNumbers(userid=userid, links=url, Name=name,Price=price, Kilometers=kilometers, Date=date,Power=power, Image=image, Number=number.text)
                        Scrapper_Outputs.save()
                return HttpResponse(links[1])
            
                
            results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
            user_data = User.objects.all().filter(id=request.session.get('userid')).values()
            if user_data[0]['autoscout_scrap'] == "True":
                context= {"username":request.session.get('username'),"data":results,"user_data":user_data}
                return render(request,'scrapper/scrapper-bot.html',context)  
            else:
                return render(request,"home/forbidden.html")
        else:
            return HttpResponse("please log in first")
    except Exception as e:
        return HttpResponse(e)

def scrapper_bot_without_numbers(request):
    if request.session['is_login'] is True:
        results = ScrapperOutput_withoutNumbers.objects.all().filter(userid=request.session.get('userid'))
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        context= {"username":request.session.get('username'),"user_data":user_data,"data":results}
        return render(request,'scrapper/data-without-numbers.html',context)  
    else:
        return HttpResponse("please log in first")

def scrapper_bot_with_numbers(request):
    if request.session['is_login'] is True:
        results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        context= {"username":request.session.get('username'),"user_data":user_data,"data":results}
        return render(request,'scrapper/data-with-numbers.html',context)  
    else:
        return HttpResponse("please log in first")

def scrapper_bot_send_via_number_single(request,number):
    numbers = []
    numbers.append(number.replace(' ', '').replace('-',''))
    message = "hi how are you i am hardcoded"
    for number in numbers:
        account_sid = 'ACb13469f2cfde161c993517c915f3e3f7'
        auth_token = '5841cfd180ae2e44370d861efc990d5c'
        client = Client(account_sid,auth_token)
        message = client.messages.create(to=number, from_='+18623566926',body=message)
        # account_sid = 'ACXXXXXXXXXX'
        # auth_token = 'YYYYYYYY'
        # client = Client(account_sid,auth_token)

        # message = client.message(to=number, from_='+9XXXXXXXXX',body=message)

        print("Message sent to : ",number)
    # redirect 
    results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
    user_data = User.objects.all().filter(id=request.session.get('userid'))
    context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"alert":"success","msg":"Message sent to : "+number+ " successfully"}
    return render(request,'scrapper/data-with-numbers.html',context) 
def scrapper_bot_send_via_number_multiple(request):
    if request.method =='POST':
        numbers = []
        data = request.POST.get("myData")
        data = json.loads(data)
        print("data is :",data)
        for i in data:
                id = (int(i))
                number = ScrapperOutput_withNumbers._meta.get_field('Number').value_from_object(ScrapperOutput_withNumbers.objects.get(id=id))
                numbers.append(number)
        print("numbers is :",numbers)
        numbers.append(number.replace(' ', '').replace('-',''))
        message = "hi how are you i am hardcoded"
        for number in numbers:

            # account_sid = 'ACXXXXXXXXXX'
            # auth_token = 'YYYYYYYY'
            # client = Client(account_sid,auth_token)

            # message = client.message(to=number, from_='+9XXXXXXXXX',body=message)

            print("Message sent to : ",number)
        return HttpResponse(200)

    
def scrapper_bot_send_via_web_single(request,type,id):
    
    if request.method =='POST':
        message = request.POST.get("message")
        name = request.POST.get("name")
        email = request.POST.get("email")
        number = request.POST.get("number")
        print(message,name,email,number)
        if type=='with-numbers':
            url = ScrapperOutput_withNumbers._meta.get_field('links').value_from_object(ScrapperOutput_withNumbers.objects.get(id=id))
        elif type=='without-numbers':
            url = ScrapperOutput_withoutNumbers._meta.get_field('links').value_from_object(ScrapperOutput_withoutNumbers.objects.get(id=id))
        urls = []
        url1 = "https://www.autoscout24.it/annunci/jaguar-f-pace-f-pace-3-0d-tdv6-portfolio-awd-300cv-auto-my18-diesel-grigio-a129f31b-950d-4d01-adcd-0edfc363fdd0?source=list_searchresults"
        url2 = "https://www.autoscout24.it/annunci/bmw-1er-m-coupe-118d-sport-edition-diesel-grigio-31464155-1d5c-4ed6-8294-833acca9fed3?source=list_searchresults"

        urls.append(url2)

        # message = "this is message2"
        # name = "Syed Zamanat Abbas"
        # email = "mali29april@gmail.com"
        # number = "+923232629249"

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # path = r'C:\Users\CCS LAPTOP HYD\Desktop\driver\chromedriver.exe'
        path = r'C:\Users\HOME\Desktop\chromedriver.exe'
        driver = webdriver.Chrome(path,options=chrome_options)

        driver.get('https://www.autoscout24.it/annunci/volkswagen-golf-volkswagen-golf-1-9-tdi-5p-comfortline-diesel-nero-8ab0eba5-7c72-47ca-b952-dbb58ba1d2db?source=list_searchresults')
        time.sleep(7)

        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 10)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(10)
        for url in urls:
            driver.get(url)
            print("sending message to row.. xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.")
            time.sleep(7)
            comment = driver.find_element_by_name('comment')
            comment.clear()
            comment.send_keys(message)
            time.sleep(1)
            sende_name = driver.find_element_by_name('senderName')
            sende_name.clear()
            sende_name.send_keys(name)
            time.sleep(1)
            sender_email = driver.find_element_by_name('senderEmail')
            sender_email.clear()
            sender_email.send_keys(email)
            phone = driver.find_element_by_name('fullPhoneNumber')
            phone.clear()
            phone.send_keys(number)
            time.sleep(1)
            driver.find_element_by_css_selector('label[for="privacyAgreement"]').click()
            time.sleep(1)
            driver.find_element_by_css_selector('input[type ="submit"]').click()
            time.sleep(5)
            current_url = driver.current_url
            if "messaggio-inviato-con-successo" in current_url:
                print(f"message sent sent to row xxxxxxxxxxxxxxxxx...")
                results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
                user_data = User.objects.all().filter(id=request.session.get('userid'))
                context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"alert":"success","msg":"message sent to "+url}
                return render(request,'scrapper/data-with-numbers.html',context)  

            else:
                print("message failed xxxxxxxxxxxxxxxxxxxxxxxxxx.")
                
                results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
                user_data = User.objects.all().filter(id=request.session.get('userid'))
                context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"alert":"danger","msg":"message failed to "+url}
                return render(request,'scrapper/data-with-numbers.html',context)
                driver.close()


        driver.close()
        return redirect (scrapper_bot)

def clear_all_scrapper_data(request,id):
    if request.session['is_login'] is True:
        if request.session['userid'] == id:
            ScrapperOutput_withNumbers.objects.filter(userid=request.session.get('userid')).delete()
            ScrapperOutput_withoutNumbers.objects.filter(userid=request.session.get('userid')).delete()

            user_data = User.objects.all().filter(id=request.session.get('userid'))
            results1_count = ScrapperOutput_withNumbers.objects.filter(userid=request.session.get('userid')).count()
            results2_count = ScrapperOutput_withoutNumbers.objects.filter(userid=request.session.get('userid')).count()
            total_results = results1_count + results2_count
            context = {"user_data":user_data,"total_results":total_results,"withnumbers":results1_count,"withoutnumbers":results2_count,"alert":"success","msg":"Data cleared successfully"}
            return render(request,'scrapper/user-profile.html',context)
        else:
            return HttpResponse("Invalid userid")
    else:
        return HttpResponse("please log in first")

def select_scrapped_data(request,type,id):
    if request.session['is_login'] is True:
        if type == 'with-numbers':
            results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"type":"withnumbers"}
            return render(request,'scrapper/select-scrapped-data.html',context)  
        elif type =='without-numbers':
            results = ScrapperOutput_withoutNumbers.objects.all().filter(userid=request.session.get('userid'))
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"type":"withoutnumbers"}
            return render(request,'scrapper/select-scrapped-data.html',context) 
        else:
            return HttpResponse("not defined")
        
    else:
        return HttpResponse("please log in first")

def delete_data(request,id,type):
    if request.session['is_login'] is True:
        if type == 'with-numbers':
            ScrapperOutput_withNumbers.objects.filter(id=id).delete()
            results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"alert":"success","msg":"Row deleted"}
            return render(request,'scrapper/data-with-numbers.html',context)  
        elif type == 'without-numbers':
            ScrapperOutput_withoutNumbers.objects.filter(id=id).delete()
            results = ScrapperOutput_withoutNumbers.objects.all().filter(userid=request.session.get('userid'))
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"alert":"success","msg":"Row deleted"}
            return render(request,'scrapper/data-without-numbers.html',context) 
    else:
        return HttpResponse("please log in first")

def edit_data(request,type,id):
    if request.session['is_login'] is True:
        if type == 'with-numbers':
            if request.method =='POST':
                t = ScrapperOutput_withNumbers.objects.get(id=id)
                link = request.POST.get("link")
                Name = request.POST.get("Name")
                try:
                    Price = float(request.POST.get("Price"))
                    Kilometer = float(request.POST.get("Kilometer"))
                except:
                    return HttpResponse("only numbers are allowed in price and kilometers")
                Date = request.POST.get("Date")
                Power = request.POST.get("Power")
                Image = request.POST.get("Image")
                Number = request.POST.get("Number")
                t.Number = Number
                t.links = link 
                t.Name = Name
                t.Price = Price
                t.Kilometers = Kilometer
                t.Date = Date
                t.Power = Power
                t.Image = Image
                t.save()
                results = ScrapperOutput_withNumbers.objects.all().filter(userid=request.session.get('userid'))
                user_data = User.objects.all().filter(id=request.session.get('userid'))
                context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"alert":"success","msg":"Data Edited Success"}
                return render(request,'scrapper/data-with-numbers.html',context)  

            data = ScrapperOutput_withNumbers.objects.filter(id=id)
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            context= {"username":request.session.get('username'),"user_data":user_data,"data":data,"type":"with-numbers"}
            return render(request,'scrapper/edit-data.html',context)  
        elif type =='without-numbers':
            if request.method =='POST':
                t = ScrapperOutput_withoutNumbers.objects.get(id=id)
                link = request.POST.get("link")
                Name = request.POST.get("Name")
                try:
                    Price = float(request.POST.get("Price"))
                    Kilometer = float(request.POST.get("Kilometer"))
                except:
                    return HttpResponse("only numbers are allowed in price and kilometers")
                Date = request.POST.get("Date")
                Power = request.POST.get("Power")
                Image = request.POST.get("Image")
                t.links = link 
                t.Name = Name
                t.Price = Price
                t.Kilometers = Kilometer
                t.Date = Date
                t.Power = Power
                t.Image = Image
                t.save()
                results = ScrapperOutput_withoutNumbers.objects.all().filter(userid=request.session.get('userid'))
                user_data = User.objects.all().filter(id=request.session.get('userid'))
                context= {"username":request.session.get('username'),"user_data":user_data,"data":results,"alert":"success","msg":"Data Edited Success"}
                return render(request,'scrapper/data-without-numbers.html',context)  

            data = ScrapperOutput_withoutNumbers.objects.filter(id=id)
            user_data = User.objects.all().filter(id=request.session.get('userid'))
            context= {"username":request.session.get('username'),"user_data":user_data,"data":data,"type":"without-numbers"}
            return render(request,'scrapper/edit-data.html',context) 
        else:
            return HttpResponse("not defined")
    else:
        return HttpResponse("please log in first")

def messages_sent(request):
    user_data = User.objects.all().filter(id=request.session.get('userid'))
    context = {"alert":"success","msg":"Messages Sent Successfully","user_data":user_data}
    return render(request,'scrapper/messages-sent.html',context)



def message_scrapper_bot_send_via_web_single(request,type,id):
    if type=='with-numbers':
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        
        url = ScrapperOutput_withNumbers._meta.get_field('links').value_from_object(ScrapperOutput_withNumbers.objects.get(id=id))
        context = {"user_data":user_data,"type":type,"id":id,"url":url}
        return render(request,"scrapper/message-for-scrapper.html",context)
    elif type=='without-numbers':
        user_data = User.objects.all().filter(id=request.session.get('userid'))
        
        url = ScrapperOutput_withoutNumbers._meta.get_field('links').value_from_object(ScrapperOutput_withoutNumbers.objects.get(id=id))
        context = {"user_data":user_data,"type":type,"id":id,"url":url}
        return render(request,"scrapper/message-for-scrapper.html",context)

def scrapper_filter(request,type,id):
    if request.method =='POST':
        price_min = request.POST.get("price-min")
        price_max = request.POST.get("price-max")
        km_min = request.POST.get("km-min")
        km_max = request.POST.get("km-max")
    
        if type=='with-numbers':
            if price_min and price_max and km_min and km_max:
                results = ScrapperOutput_withNumbers.objects.all().filter(userid=id, Price__lte = price_max,Price__gte=price_min,Kilometers__lte = km_max, Kilometers__gte=km_min)
                print(results)
                user_data = User.objects.all().filter(id=request.session.get('userid'))
                context= {"username":request.session.get('username'),"user_data":user_data,"data":results}
                return render(request,'scrapper/filtered-data-with-numbers.html',context) 
            else:
                return HttpResponse("missing data")
        if type=='without-numbers':
            if price_min and price_max and km_min and km_max:
                results = ScrapperOutput_withoutNumbers.objects.all().filter(userid=id, Price__lte = price_max,Price__gte=price_min,Kilometers__lte = km_max, Kilometers__gte=km_min)
                user_data = User.objects.all().filter(id=request.session.get('userid'))
                context= {"username":request.session.get('username'),"user_data":user_data,"data":results}
                return render(request,'scrapper/filtered-data-without-numbers.html',context) 
            else:
                return HttpResponse("missing data") 
