from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat, name='api_chat'),
]