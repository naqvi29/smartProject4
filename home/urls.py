from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('admin-dashboard', views.admin_dashboard, name='admin-dashboard'),
    path('admin-login', views.admin_login, name='admin_login'),
    path('admin-users', views.admin_users, name='admin_users'),
    path('delete-user/<int:id>', views.delete_user, name='delete_user'),
    path('edit-user/<int:id>', views.edit_user, name='edit_user'),
    path('admin-profile', views.admin_profile, name='admin_profile'),
    # path('add-user', views.add_user, name='add_user'),
]