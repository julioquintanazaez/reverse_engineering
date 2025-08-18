from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
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
            FileResponse: Respuesta con el archivo adjunto
            Http404: Si el test no existe o no tiene archivo de resultados
        """
        # Obtener el test o devolver 404 si no existe
        test = get_object_or_404(Test, test_code=test_code)
        
        # Verificar que el test tenga un archivo de resultados
        if not test.result_file:
            raise Http404("El test no tiene archivo de resultados asociado")
            
        # Abrir el archivo en modo lectura binaria
        try:
            file = test.result_file.open('rb')
        except FileNotFoundError:
            raise Http404("El archivo de resultados no se encuentra en el sistema")
            
        # Obtener el nombre del archivo (última parte de la ruta)
        filename = test.result_file.name.split('/')[-1]
        
        # Crear la respuesta con el archivo adjunto
        response = FileResponse(file)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Opcional: establecer el tipo MIME si lo conoces
        response['Content-Type'] = 'application/xlsx'  # por ejemplo para PDF
        
        return response