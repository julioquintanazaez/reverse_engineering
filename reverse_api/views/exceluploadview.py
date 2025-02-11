from django.shortcuts import render
import openpyxl  
from rest_framework import status  
from rest_framework.response import Response  

from rest_framework.views import APIView  
#from rest_framework.viewsets import ViewSet
from rest_framework.generics import GenericAPIView
from rest_framework import parsers, renderers

from ..serializers.exceluploadserializer import ExcelUploadSerializer

from ..utils.readgeneschunks import ExcelFileParseUtils


# Create your views here.

class ExcelUploadView(GenericAPIView): 
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    renderer_classes = (renderers.JSONRenderer, )
    file_content_parser_classes = (renderers.JSONRenderer, )
    serializer_class = ExcelUploadSerializer

    def post(self, request):
        """
        Upload a excel file to extract data
        ---
        parameters:
          - in: body
            file_uploaded: body
            required: true
            schema:
              file_uploaded: URL
              required:
                - file
              properties:
                file_uploaded:
                  type: string
                  description: The url of the file
        responses:
          201:
            description: File readed succesfuly
          400:
            description: Bad request
        """
        erfd = ExcelFileParseUtils()
        serializer_file = self.serializer_class(data=request.data)
        if serializer_file.is_valid(raise_exception=True):
            data_file = serializer_file.validated_data['file_uploaded']
            file = data_file
            erfd.readDataFile(file)            
            return Response({'success':"True"}, status=status.HTTP_200_OK)      

        return Response({'success':"False"}, status=status.HTTP_400_BAD_REQUEST)