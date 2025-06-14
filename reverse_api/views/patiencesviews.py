from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models.patiencestest import PatiencesTest
from ..serializers.patiencestestserializer import PatiencesTestCreateSerializer, PatiencesTestSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q

"""
class TestResultCreateView(generics.CreateAPIView):
    queryset = PatiencesTest.objects.all()
    serializer_class = PatiencesTestCreateSerializer

    def perform_create(self, serializer):
        serializer.save()
"""
class UserTestResultsView(generics.ListAPIView):
    """
    Endpoint para obtener todos los JSONs de un usuario específico
    """
    serializer_class = PatiencesTestSerializer

    def get_queryset(self):
        user_code = self.kwargs['user_code']
        return PatiencesTest.objects.filter(user_code=user_code)

class TestResultDetailView(generics.RetrieveAPIView):
    """
    Endpoint para obtener un JSON específico por código de test
    """
    serializer_class = PatiencesTestSerializer
    lookup_field = 'test_code'

    def get_object(self):
        test_code = self.kwargs['test_code']
        queryset = self.filter_queryset(self.get_queryset())
       
        # Puede incluir user_code si quieres ser más específico
        if 'user_code' in self.kwargs:
            user_code = self.kwargs['user_code']
            obj = get_object_or_404(queryset, test_code=test_code, user_code=user_code)
        else:
            obj = get_object_or_404(queryset, test_code=test_code)
           
        return obj

    def get_queryset(self):
        return PatiencesTest.objects.all()

class TestResultSearchView(APIView):
    """
    Endpoint avanzado para búsqueda con filtros combinados
    """
    def get(self, request):
        query = Q()
       
        if user_code := request.query_params.get('user_code'):
            query &= Q(user_code=user_code)
           
        if test_code := request.query_params.get('test_code'):
            query &= Q(test_code=test_code)
           
        results = PatiencesTest.objects.filter(query)
        serializer = PatiencesTestSerializer(results, many=True)
        return Response(serializer.data)
    

class TestResultDeleteView(generics.DestroyAPIView):
    """
    Endpoint para eliminar un test específico por código de test
    """
    serializer_class = PatiencesTestSerializer
    lookup_field = 'test_code'

    def get_object(self):
        test_code = self.kwargs['test_code']
        queryset = self.filter_queryset(self.get_queryset())
       
        # Puede incluir user_code si quieres ser más específico
        if 'user_code' in self.kwargs:
            user_code = self.kwargs['user_code']
            obj = get_object_or_404(queryset, test_code=test_code, user_code=user_code)
        else:
            obj = get_object_or_404(queryset, test_code=test_code)
           
        return obj

    def get_queryset(self):
        return PatiencesTest.objects.all()

    def delete(self, request, *args, **kwargs):
        """
        Personalización del mensaje de respuesta al eliminar
        """
        super().delete(request, *args, **kwargs)
        return Response({"detail": "Test succesfuly deleted"}, status=status.HTTP_200_OK)
    
class UserTestResultsDeleteView(generics.GenericAPIView):
    """
    Endpoint para eliminar todos los tests de un usuario específico
    """
    def get_queryset(self):
        user_code = self.kwargs['user_code']
        return PatiencesTest.objects.filter(user_code=user_code)

    def delete(self, request, *args, **kwargs):
        user_code = self.kwargs['user_code']
        queryset = self.get_queryset()
        count = queryset.count()
        queryset.delete()
        return Response({"detail": f"A {count} tests from user {user_code} were deleted"}, status=status.HTTP_200_OK)
