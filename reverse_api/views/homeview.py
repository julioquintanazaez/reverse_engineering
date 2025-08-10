# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HomeView(APIView):
    def get(self, request):
        data = {
            "message": "Welcome to API Reverse Engineering v 0.0.1.1.5!"
        }
        return Response(data, status=status.HTTP_200_OK)