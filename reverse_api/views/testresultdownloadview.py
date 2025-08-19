from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404, HttpResponse
from django.views import View
from rest_framework.views import APIView
from ..models.tests import Test  # Asegúrate de importar tu modelo Test

class TestResultDownloadView(APIView):
    def get(self, request, test_code, format=None):
        """
        Vista para descargar el archivo de resultados de un test dado su código.
        
        Args:
            request: HttpRequest object
            test_code (str): Código único del test
            
        Returns:
            HttpResponse: Respuesta con el archivo adjunto
            Http404: Si el test no existe o no tiene archivo de resultados
        """
        test = get_object_or_404(Test, test_code=test_code)
        
        if not test.result_file:
            raise Http404("El test no tiene archivo de resultados asociado")
            
        # Convertir el binary field a bytes
        file_data = bytes(test.result_file)
        
        # Crear una respuesta con los bytes
        response = HttpResponse(file_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="result_{test.test_code}.bin"'
        
        return response