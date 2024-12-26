from django.shortcuts import render
from rest_framework import status  
from rest_framework.response import Response  

from rest_framework.views import APIView 
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework import parsers, renderers

from ..serializers.geneserializer import GenesSerializer, Genes_AllelesSerializer
from ..models.genes import Genes 

# Create your views here.

class GenesListView(APIView):
    def get(self, request):
        genes = Genes.objects.all()
        serializer = GenesSerializer(genes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GenesAllelesListView(ListAPIView):
    queryset = Genes.objects.all()
    serializer_class = Genes_AllelesSerializer