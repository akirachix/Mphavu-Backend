from django.urls import  path
from .views import user_login, loginSSO, callback, logout, index
urlpatterns = [
   path('login/', user_login, name='user_login'),
   path('logout/', logout, name='logout'),
   path('callback/', callback, name='callback'),
   path('sso-login/', loginSSO, name='login_sso'),
   path('', index, name='index'),
]