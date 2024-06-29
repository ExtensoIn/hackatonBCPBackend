from django.urls import path
from endpoints.views import index

urlpatterns = [
    path('test', index),
]