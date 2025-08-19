from django.shortcuts import render
from rest_framework import status  
from rest_framework.response import Response  

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from ..serializers.allelesreferenceserializer import AllelesReferenceSerializer
from ..models.allelesreference import Alleles_Reference

from ..serializers.genesallelesreferenceerializer import GenesAllelesReferenceSerializer

from ..utils.reverseengineeringprocessor import ReverseEngineeringProcessor

# Create your views here.

class AllelesReferenceListView(APIView):
    def get(self, request):
        genes_ref = Alleles_Reference.objects.all()
        serializer = AllelesReferenceSerializer(genes_ref, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

"""
Este el al método que devuelve la ingeniería inversa para una lista de genes
y sus pares de alleles. Recibe los genes y alleles como parámetros por un post 
"""
class GetReverseEngineeringView(GenericAPIView):  

    serializer_class = GenesAllelesReferenceSerializer
    
    def post(self, request):

        hr = ReverseEngineeringProcessor() 

        serializer = GenesAllelesReferenceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        
        try:
            response = hr.process_patient_genes(serializer.data) 
            return Response(response, status=status.HTTP_200_OK)
        except:
            raise Response({"status":"Some error occur processing reverse engineering"}, status=status.HTTP_400_BAD_REQUEST)
       
        
