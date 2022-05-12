from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path('user-dashboard', views.user_dashboard, name='user-dashboard'),
    path('user-profile', views.user_profile, name='user_profile'),
    path('telegram-accounts', views.telegram_accounts, name='telegram_accounts'),
    # path('telegram-bot-send/<str:category>/<int:id>/<str:sent>', views.telegram_bot_send, name='telegram_bot_send'),
    path('telegram-dmBot-send', views.telegram_dmBot_send, name='telegram_dmBot_send'),
    path('send-chat/<int:id>', views.send_chat, name='send_chat'),
    path('send-answer/<int:id>', views.send_answer, name='send_answer'),
    path('telegram-bot-add-group', views.telegram_bot_add_group, name='telegram_bot_add_group'),
    path('telegram-bot-add-question', views.telegram_bot_add_question, name='telegram_bot_add_question'),
    path('telegram-bot-add-answer', views.telegram_bot_add_answer, name='telegram_bot_add_answer'),
    path('delete-telegram-account/<int:id>', views.delete_telegram_account, name='delete_telegram_account'),
    path('edit-telegram-account/<int:id>', views.edit_telegram_account, name='edit_telegram_account'),
    path('telegram-bot-add-question', views.telegram_bot_add_question, name='telegram_bot_add_question'),
    path('delete-telegram-groups/<int:id>', views.delete_telegram_groups, name='delete_telegram_groups'),
    path('delete-telegram-questions/<int:id>', views.delete_telegram_questions, name='delete_telegram_questions'),
    path('delete-telegram-answers/<int:id>', views.delete_telegram_answers, name='delete_telegram_answers'),
    path('coming-soon', views.coming_soon, name='coming_soon'),
    path('schedule-messages', views.schedule_messages, name='schedule_messages'),
    path('delete-schedule-messages/<int:id>', views.delete_schedule_messages, name='delete_schedule_messages'),
    path('time-now', views.time_now, name='time_now'),
    path('users-scrapper-account', views.users_scrapper_account, name='users_scrapper_account'),
    path('users-scrapper-groups/<int:account_id>', views.users_scrapper_groups, name='users_scrapper_groups'),
    path('users-scrapper-group-members/<int:account_id>/<int:group_id>', views.users_scrapper_group_members, name='users_scrapper_group_members'),
    path('telegram-user-dmBot-send', views.telegram_user_dmBot_send, name='telegram_user_dmBot_send'),
    path('test', views.test, name='test'),
    path('send-user-chat', views.send_user_chat, name='send_user_chat'),
    path('schedule-user-messages', views.schedule_user_messages, name='schedule_user_messages'),
    path('delete-schedule-user-messages/<int:id>', views.delete_schedule_user_messages, name='delete_schedule_user_messages'),
    path('scrapped-members-api', views.scrapped_members_api, name='scrapped_members_api'),
    path('clear-delete-all-members/<int:account_id>/<int:group_id>', views.clear_delete_all_members, name='clear_delete_all_members'),
    path('delete-scrapped-group/<int:account_id>/<int:group_id>', views.delete_scrapped_group, name='delete_scrapped_group'),
    path('add-users', views.add_users, name='add_users'),
    path('add-users-function', views.add_users_function, name='add_users_function'),
    path('schedule-add-users', views.schedule_add_users, name='schedule_add_users'),
    path('delete-schedule-add-users/<int:id>', views.delete_schedule_add_users, name='delete_schedule_add_users'),
    path('user-dm-logs', views.user_dm_logs, name='user_dm_logs'),
    path('user-add-logs', views.user_add_logs, name='user_add_logs'),
    path('clear-all-user-dm-logs', views.clear_all_user_dm_logs, name='clear_all_user_dm_logs'),
    path('clear-all-user-add-logs', views.clear_all_user_add_logs, name='clear_all_user_add_logs'),
    path('add-manual-member/<int:user_id>/<int:account_id>/<int:group_id>',views.add_manual_member, name='add_manual_member'),
    path('clear-all-cache/<str:confirm>',views.clear_all_cache, name='clear_all_cache'),


    # Added by awais tariq
    path("authenticate_telegram_account",views.authenticate_telegram_account,name='authenticate_telegram_account'),
    path("authenticate_telegram_account_code",views.authenticate_telegram_account_code,name='authenticate_telegram_account_code')

]