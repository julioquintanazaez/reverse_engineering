# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.managecleanup import development_only
from ..models.alleles import Alleles
from ..models.allelescombinations import Alleles_Combinations
from ..models.allelesreference import Alleles_Reference
from ..models.genes import Genes
from ..models.patients import Patient
from ..models.tests import Test

class DevelopmentCleanupView(APIView):
    @development_only
    def post(self, request):
        # Eliminación en orden seguro para evitar problemas de FK
        models_to_clean = [
            Test,
            Patient,
            Alleles_Combinations,
            Alleles,
            Alleles_Reference,
            Genes
        ]
        
        try:
            for model in models_to_clean:
                model.objects.all().delete()
            
            return Response(
                {"message": "Datos de desarrollo limpiados exitosamente"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Error al limpiar datos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )