from django.urls import path
from endpoints.views import get_all_data, create_data, get_data, generate_image

urlpatterns = [
    path('get-all-data', get_all_data),
    path('create-data', create_data),
    path('get-data', get_data),
    path('get-images', generate_image)
]
