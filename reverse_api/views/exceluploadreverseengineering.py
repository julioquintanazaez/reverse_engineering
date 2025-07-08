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
from ..models.tests import Test
from ..models.patients import Patient

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
                patient_data = efpac.readAllelesCombinationsDataFromFile(file)
            except:
                return Response({'error':"Fail to load combinations"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            try:     
                # Guardar en base de datos json de reverse           
                test, created_test = Test.objects.get_or_create(
                    user_code = data_user,
                    test_code = data_test
                ) 
            except:
                return Response({'error':"Fail to save tests in db"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            patients_code = []  

            if created_test:
                # Calcular reverse para cada paciente (test_id, patient_data)
                try:
                    for patientes in patient_data["patience_list"]:
                        # Iterar sobre cada clave-valor en el diccionario
                        for patiente_code, genes_values in patientes.items():
                            response_json = hr.reveng_patience(genes_data=genes_values)
                            print(f"Test code: {test.id}--{test.test_code} with User code: {patiente_code} and JSON length: {len(response_json)}")
                            # Guardar en base de datos json de reverse           
                            try: 
                                # Guardar en base de datos json de reverse           
                                patient, created_patient = Patient.objects.get_or_create(
                                    test = test,
                                    code = patiente_code,
                                    data_json = response_json["response"]
                                ) 
                            except Exception as e:
                                print(f"{'error:Fail to save patient in db'}: {str(e)}")
                                return Response({'error':"Fail to save patient in db"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                            patients_code.append(patiente_code)

                except Exception as e:
                    print(f"{'error:Fail reverse computations'}: {str(e)}")
                    return Response({'error':"Fail reverse computations"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
           
            response_final = {
                "test_code": test.test_code,
                "user_id": test.user_code,
                "patients_code": patients_code 
            }

            return Response(response_final, status=status.HTTP_200_OK)
            
        return Response({'error':"Invalid input"}, status=status.HTTP_400_BAD_REQUEST)




"""
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
            except:
                return Response({'error':"Fail to load combinations"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            try:
                # Calcular reverse aquí
                response = hr.reverse_engineering_patience(patience_data) # Cambiar método
            except:
                return Response({'error':"Fail reverse computations"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            try:     
                 # Guardar en base de datos json de reverse           
                test, _ = Test.objects.get_or_create(
                    user_code = data_user,
                    test_code = data_test,
                    test_data = response["response"]
                ) 
            except:
                return Response({'error':"Fail to save tests in db"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                
            return Response(response, status=status.HTTP_200_OK)
            
        return Response({'error':"Invalid input"}, status=status.HTTP_400_BAD_REQUEST)


"""



