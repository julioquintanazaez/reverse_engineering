from django.shortcuts import render
import openpyxl  
from rest_framework import status  
from rest_framework.response import Response  
from rest_framework.generics import GenericAPIView
from rest_framework import parsers, renderers

from ..serializers.excelserializer import ExcelSerializer, InputTestSerializer

from ..utils.readchunkallelescombinations import ExcelFileParseAllelesCombinationsUtils
from ..utils.reverseengineeringprocessor import ReverseEngineeringProcessor

from ..models.allelesreference import Alleles_Reference
from ..models.tests import Test
from ..models.patients import Patient

from ..utils.combine_patient_genotype_data import combine_patient_genotype_data
from ..utils.json_to_excel import json_to_excel

from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO

from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404

from datetime import datetime
import json

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
        hr = ReverseEngineeringProcessor() 
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
                code = str(datetime.now().strftime("%m/%d/%Y%H:%M:%S"))   # Eliminar cuando lógica de usuarios este lista      
                test, created_test = Test.objects.get_or_create(
                    user_code = data_user +"_"+ code,
                    test_code = data_test +"_"+ code
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
                            response_json = hr.process_patient_genes(genes_data=genes_values)
                            # Processing json here
                            if response_json is not None:
                                 # Si es un diccionario con clave "response"
                                if isinstance(response_json, dict) and "response" in response_json:
                                    if response_json["response"]:  # Verifica que no esté vacío
                                        patient_data_jsons.append(response_json)
                                        patient_info.append({
                                            "Accession number": patiente_code,
                                            "First name": "Name1",
                                            "Last name": "LastN1",
                                            "Middle initial": " ",
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
                    
                    # Guardar en archivo
                    #with open('datos.json', 'w', encoding='utf-8') as archivo:
                    #    json.dump(patient_data_jsons, archivo, ensure_ascii=False, indent=4)
                    #print("JSON guardado exitosamente")

                    print("Combinar resultados")
                    combined_data = combine_patient_genotype_data(
                        patient_data_list=patient_data_jsons,
                        patient_info_list=patient_info
                    )
                    
                    # Generar el Excel en memoria
                    print("Generar el Excel en memoria")                    
                    excel_io = json_to_excel(combined_data)
                    excel_content = excel_io.getvalue()
                    
                    # Guardar el contenido binario directamente en el BinaryField
                    test.result_file = excel_content
                    test.save()
                    
                    # Crear respuesta desde el contenido binario
                    response = HttpResponse(excel_content, 
                                         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename="reverse_engineering_{data_test}.xlsx"'
                    
                    return response
                    
                except Exception as e:
                    print(f"Error in reverse computations: {str(e)}")
                    return Response({'error': f"Fail reverse computations: {str(e)}"}, 
                                  status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            # Si el test ya existía y tiene datos
            if test.result_file:
                response = HttpResponse(test.result_file, 
                                       content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="reverse_engineering_{data_test}.xlsx"'
                return response
            
            return Response({'error': "No results available"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({'error': "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)


