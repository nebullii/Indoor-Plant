from django.urls import path
from .views import ask_bot, ai_chat_page

app_name = 'ai'

urlpatterns = [
    path('ask/', ask_bot, name='ask_bot'),
    path('chat/', ai_chat_page, name='ai_chat_page'),
]
