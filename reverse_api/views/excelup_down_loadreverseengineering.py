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

from ..utils.combine_patient_genotype_data import combine_patient_genotype_data
from ..utils.json_to_excel import json_to_excel

from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from datetime import datetime

# Create your views here.

class ExcelUpDownloadForReverseEngineeringView(GenericAPIView): 
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
                patient_data_jsons = []
                patient_info = []
                try:
                    for patiente in patient_data["patience_list"]:
                        for patiente_code, genes_values in patiente.items():
                            #print(f"{patiente_code}: --- {genes_values}")
                            #print(f"Reverse para paciente {patiente_code}")
                            response_json = hr.reveng_patience(genes_data=genes_values)
                            # Processing json here
                            if response_json is not None:
                                patient_data_jsons.append(response_json)
                                patient_info.append({
                                    "Accession number": patiente_code,
                                    "First name": "Name1",
                                    "Last name": "LastN1",
                                    "DOB": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                                    "Ordering physician": "Dtor",
                                    "Gender": "Unknown",
                                    "Collection date":	datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                                    "Received date": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                                    "Report generated": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                                    "Report format type": "F01",
                                    "Renal function": 1,
                                    "Smoker": 1, 
                                    "Daily or nearly daily alcohol intake":	1,
                                    "Language":	"L001"
                                })
                                patients_code.append(patiente_code)
                            else:
                                print(f"Error: hr.reveng_patience output None for {patiente_code}")
                    
                    print("Combinar resultados")
                    combined_data = combine_patient_genotype_data(
                        patient_data_list=patient_data_jsons,
                        patient_info_list=patient_info
                    )
                    print("Convertir a json")
                    # Convertir el JSON combinado a Excel
                    excel_content  = json_to_excel(combined_data)
                    
                    # Crear un archivo en memoria sin guardar en disco
                    file_name = f'reverse_engineering_{data_test}.xlsx'
                    in_memory_file = BytesIO(excel_content.getvalue())
                    
                    # Guardar en el modelo sin persistir en disco
                    test.result_file.save(
                        file_name, 
                        ContentFile(in_memory_file.read()),
                        save=False
                    )
                    
                    # Guardar el resto de los campos
                    test.save()
                    
                except Exception as e:
                    print(f"{'error:Fail reverse computations'}: {str(e)}")
                    return Response({'error':"Fail reverse computations"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            response = FileResponse(test.result_file.open('rb'))
            response['Content-Disposition'] = f'attachment; filename="{test.result_file.name.split("/")[-1]}"'
            return response
            
        return Response({'error':"Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def download_test_result(request, test_code):
        test = get_object_or_404(Test, test_code=test_code)
        if test.result_file:
            response = FileResponse(test.result_file.open('rb'))
            response['Content-Disposition'] = f'attachment; filename="{test.result_file.name.split("/")[-1]}"'
            return response
        raise Http404("File not found")



