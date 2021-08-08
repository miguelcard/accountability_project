
from django.http.response import JsonResponse
from rest_framework.views import APIView


class MyOwnView(APIView):
    def get(self, request):
        return JsonResponse({'foo':'bar'})