from collections import Counter
from django.shortcuts import render
from rest_framework import status  
from rest_framework.response import Response  

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import parsers, renderers

from ..serializers.allelesserializer import AllelesSerializer
from ..models.alleles import Alleles 

# Create your views here.

class AllelesListView(APIView):
    def get(self, request):
        genes_body = Alleles.objects.all()
        serializer = AllelesSerializer(genes_body, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    