from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import parsers, renderers

from ..serializers.exceluploadserializer import ExcelUploadSerializer
from ..utils.genedataimporter import GeneDataImporter


class GeneImportAPIView(GenericAPIView): 
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    renderer_classes = (renderers.JSONRenderer, )
    file_content_parser_classes = (renderers.JSONRenderer, )
    serializer_class = ExcelUploadSerializer

    def post(self, request, format=None):
        serializer_file = self.serializer_class(data=request.data)
        if serializer_file.is_valid(raise_exception=True):
            data_file = serializer_file.validated_data['file_uploaded']
            file = data_file

        file_obj = file #request.FILES['file']
        file_name = default_storage.save(f'tmp/{file_obj.name}', ContentFile(file_obj.read()))
        file_path = default_storage.path(file_name)
        
        try:
            importer = GeneDataImporter()
            importer.process_excel_file(file_path)
            
            return Response({
                'message': 'File processed successfully',
                'genes_processed': importer.total_genes,
                'alleles_created': importer.total_alleles,
                'allele_refs_created': importer.total_allele_refs
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(file_path):
                os.remove(file_path)