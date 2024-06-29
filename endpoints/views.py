from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def index(request):
    if request.method == 'GET':
        params = request.GET.get('params', "No se encontro el parametro 'params' en la URL")
        return JsonResponse({'message': f'Hello, world! {params}'})