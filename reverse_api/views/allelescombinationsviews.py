from collections import Counter
from django.shortcuts import render
from rest_framework import status  
from rest_framework.response import Response  

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import parsers, renderers

from ..serializers.allelescombinarionsserializers import AllelesCombinationsSerializer
from ..serializers.geneserializer import GenesSerializer
from ..models.allelescombinations import Alleles_Combinations
from ..models.genes import Genes


# Create your views here.

class AllelesCombinationsAllListView(APIView):
    def get(self, request):
        allelescombinations = Alleles_Combinations.objects.all()
        serializer = AllelesCombinationsSerializer(allelescombinations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AllelesCombinationsByIDListView(APIView):
    def get(self, request, name):
        # Validar que el gen existe
        serializer = GenesSerializer(data={'name': name})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        # Obtener el gen validado
        gen = serializer.validated_data['name']
        item = Genes.objects.get(name=gen)        
        combinaciones = item.gene_comb.all()
        # Serializar los datos para la respuesta
        serializer_combinations = AllelesCombinationsSerializer(combinaciones, many=True)
        
        return Response(serializer_combinations.data, status=status.HTTP_200_OK)

    
