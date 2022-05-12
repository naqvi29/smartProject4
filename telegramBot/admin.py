from django.contrib import admin
from telegramBot.models import Telegram_Accounts,TelegramSession

# Register your models here.
admin.site.register(Telegram_Accounts)
admin.site.register(TelegramSession)

