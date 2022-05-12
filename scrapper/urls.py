from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path('user-dashboard', views.user_dashboard, name='user-dashboard'),
    path('user-profile', views.user_profile, name='user_profile'),
    path('scrapper-bot', views.scrapper_bot, name='scrapper_bot'),
    path('scrapper-bot-with-numbers', views.scrapper_bot_with_numbers, name='scrapper_bot'),
    path('scrapper-bot-without-numbers', views.scrapper_bot_without_numbers, name='scrapper_bot'),
    path('scrapper-bot-send-via-number-single/<str:number>', views.scrapper_bot_send_via_number_single, name='scrapper_bot_send_via_number_single'),
    path('scrapper-bot-send-via-number-multiple', views.scrapper_bot_send_via_number_multiple, name='scrapper_bot_send_via_number_multiple'),
    path('scrapper-bot-send-via-web-single/<str:type>/<int:id>', views.scrapper_bot_send_via_web_single, name='scrapper_bot_send_via_web_single'),
    path('clear-all-scrapper-data/<int:id>', views.clear_all_scrapper_data, name='clear_all_scrapper_data'),
    path('select-scrapped-data/<str:type>/<int:id>', views.select_scrapped_data, name='select_scrapped_data'),
    path('delete-data/<str:type>/<int:id>', views.delete_data, name='delete_data'),
    path('edit-data/<str:type>/<int:id>', views.edit_data, name='edit_data'),
    path('messages-sent', views.messages_sent, name='messages_sent'),
    path('message-scrapper-bot-send-via-web-single/<str:type>/<int:id>', views.message_scrapper_bot_send_via_web_single, name='message_scrapper_bot_send_via_web_single'),
    path('scrapper-filter/<str:type>/<int:id>', views.scrapper_filter, name='scrapper_filter'),
]