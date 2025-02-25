from django.shortcuts import render
from rest_framework import status  
from rest_framework.response import Response  

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from ..serializers.patiencesserializer import ListPatienceGenesAllelesReferenceSerializer
from ..serializers.genesallelesreferenceerializer import GenesAllelesReferenceSerializer

from ..utils.handle_reverse_engineering import Handle_Reverse_Engineering

# Create your views here.

"""
Este el al método que devuelve la ingeniería inversa para una lista de pacientes con sus genes
y sus pares de alleles.
"""
class GetPatienceReverseEngineeringView(GenericAPIView):  
    serializer_class = ListPatienceGenesAllelesReferenceSerializer
    def post(self, request):
        hr = Handle_Reverse_Engineering() 
        serializer = ListPatienceGenesAllelesReferenceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        try:
            patience_list = []
            data = serializer.data["patience_list"]
            for item in data:
                patience = item["patience"]
                patience_genes = hr.get_patience_reverse_engineering(item)
                patience_list.append({
                            "patience" : patience,
                            "genes_data": patience_genes
                        })
            response = {"patience_list": patience_list}
            return Response(response, status=status.HTTP_200_OK)
        except:
            raise Response({"status":"Some error occur processing reverse engineering"}, status=status.HTTP_400_BAD_REQUEST)
        
