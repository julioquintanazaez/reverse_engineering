from django.shortcuts import render
import openpyxl  
from rest_framework import status  
from rest_framework.response import Response  
from rest_framework.generics import GenericAPIView
from rest_framework import parsers, renderers

from ..serializers.excelserializer import ExcelSerializer, InputTestSerializer

from ..utils.readchunkallelescombinations import ExcelFileParseAllelesCombinationsUtils
from ..utils.handle_reverse_engineering import Handle_Reverse_Engineering

from ..models.allelesreference import Alleles_Reference
from ..models.patiencestest import PatiencesTest

from django.utils import timezone

# Create your views here.

class ExcelUploadForReverseEngineeringView(GenericAPIView): 
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    renderer_classes = (renderers.JSONRenderer, )
    file_content_parser_classes = (renderers.JSONRenderer, )
    serializer_class = InputTestSerializer

    def post(self, request):
        efpac = ExcelFileParseAllelesCombinationsUtils() 
        hr = Handle_Reverse_Engineering() 
        serializer_file = self.serializer_class(data=request.data)
        if serializer_file.is_valid(raise_exception=True):
            data_user = serializer_file.validated_data['userid']
            data_test = serializer_file.validated_data['testid']
            data_file = serializer_file.validated_data['file_uploaded']  
            # Validar mediante endpoint que el usuario existe y esta logueado

            # Calcular datos de genes del excel y guardar en un fichero   
            file = data_file 
            try:
                # Preparar datos para reverse_engineering aquí
                patience_data = efpac.readAllelesCombinationsDataFromFile(file)
                # Calcular reverse aquí
                response = hr.reverse_engineering_patience(patience_data) # Cambiar método
                # Guardar en base de datos json de reverse
                _, _ = PatiencesTest.objects.get_or_create(
                    user_code = data_user,
                    test_code = data_test,
                    test_data = response["response"]
                )  
                return Response(response, status=status.HTTP_200_OK)
            except:
                return Response({'error':"Fail reverse computations"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
        return Response({'error':"Invalid input"}, status=status.HTTP_400_BAD_REQUEST)





