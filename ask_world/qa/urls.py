from django.urls import path
from . import views

urlpatterns = [
    path('', views.test, name='index'),
    path('hot/', views.test, name='hot'), # список лучших вопросов
    path('questions/', views.test, name='questions'),
    path('questions/<int:id>', views.test, name='question'),
    path('tags/', views.test, name='tags'),
    path('tags/<int:id>', views.test, name='tag'),
    path('ask/', views.test, name='ask'),
    path('signup/', views.test, name='signup'),
    path('login/', views.test, name='login'),
    path('logout/', views.test, name='logout'),
    path('profile/', views.test, name='profile'),
    path('settings/', views.test, name='settings'),

]