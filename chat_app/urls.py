from django.urls import path
from . import views

urlpatterns = [
    #path('', views.home_view, name='home'),
    path('chat/', views.chat_view, name='chat'),
    path('test-kb/', views.knowledge_base_test_view, name='test_knowledge_base'),
]