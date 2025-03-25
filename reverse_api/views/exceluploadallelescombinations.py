from django.shortcuts import render
import openpyxl  
from rest_framework import status  
from rest_framework.response import Response  
from rest_framework.generics import GenericAPIView
from rest_framework import parsers, renderers

from ..serializers.excelserializer import ExcelSerializer
from ..utils.readchunkallelescombinations import ExcelFileParseAllelesCombinationsUtils

from ..serializers.allelesreferenceserializer import AllelesReferenceSerializer
from ..models.allelesreference import Alleles_Reference

from ..serializers.genesallelesreferenceerializer import GenesAllelesReferenceSerializer

from ..utils.handle_reverse_engineering import Handle_Reverse_Engineering


# Create your views here.

class ExcelUploadForReverseEngineeringView(GenericAPIView): 
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    renderer_classes = (renderers.JSONRenderer, )
    file_content_parser_classes = (renderers.JSONRenderer, )
    serializer_class = ExcelSerializer

    def post(self, request):
        efpac = ExcelFileParseAllelesCombinationsUtils() 
        hr = Handle_Reverse_Engineering() 
        serializer_file = self.serializer_class(data=request.data)
        if serializer_file.is_valid(raise_exception=True):
            data_file = serializer_file.validated_data['file_uploaded']
            file = data_file
            #Devolver las combinaciones en un json con formato para reverse 
            try:
                # Calcular reverse_engineering aquí
                genes_alleles_parent_data = efpac.readAllelesCombinationsDataFromFile(file)
                serializer = GenesAllelesReferenceSerializer(data=genes_alleles_parent_data)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
                response = hr.get_reverse_engineering(serializer.data) 
                return Response(response, status=status.HTTP_200_OK) 
                #return Response({'success':"True"}, status=status.HTTP_200_OK) 
            except:
                return Response({'success':"False"}, status=status.HTTP_400_BAD_REQUEST)
            
            
           
    

"""



class GetReverseEngineeringView(GenericAPIView):  

    serializer_class = GenesAllelesReferenceSerializer
    
    def post(self, request):

        hr = Handle_Reverse_Engineering() 

        serializer = GenesAllelesReferenceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        
        try:
            response = hr.get_reverse_engineering(serializer.data) 
            return Response(response, status=status.HTTP_200_OK)
        except:
            raise Response({"status":"Some error occur processing reverse engineering"}, status=status.HTTP_400_BAD_REQUEST)
       
        

"""