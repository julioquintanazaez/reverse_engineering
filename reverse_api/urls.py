from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from .views.exceluploadview import ExcelUploadView
from .views.exceluploadreverseengineering import ExcelUploadForReverseEngineeringView
from .views.genesview import GenesListView, GenesAllelesListView
from .views.allelesview import AllelesListView
from .views.allelescombinationsviews import AllelesCombinationsByIDListView, AllelesCombinationsAllListView
from .views.allelesreferenceview import AllelesReferenceListView, GetReverseEngineeringView
from .views.patiencegeneallelereference import GetPatienceReverseEngineeringView
from .views.patientsview import TestPatientsPDFView, PatientCodesByTestView
from .views.exceluploadreverseengineering import ReverseEngineeringJSONView
from .views.excelup_down_loadreverseengineering import ExcelUpDownloadForReverseEngineeringView
from .views.testresultdownloadview import TestResultDownloadView

from .views.testsviews import (
    UserTestResultsView,
    TestResultDetailView,
    TestResultSearchView,
    TestResultDeleteView,
    UserTestResultsDeleteView,
    AllTestResultsDeleteView
)

from .views.cleanupall import DevelopmentCleanupView
from .views.excelimportdataview import GeneImportAPIView

from django.contrib import admin
from rest_framework.routers import DefaultRouter

from drf_yasg.views import get_schema_view  
from drf_yasg import openapi
from rest_framework import permissions  

schema_view = get_schema_view(
    openapi.Info(
        title="Mi API",
        default_version='v1',
        description="Documentación de la  API para buscar productos.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@miapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

#Add your urls here.

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI  
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # Redoc  
    path('genes/', GenesListView.as_view(), name='genes'),
    path('alleles/', AllelesListView.as_view(), name='alleles'),
    path('genes_alleles/', GenesAllelesListView.as_view(), name='genes_alleles'),
    path('genes_alleles_reference/', AllelesReferenceListView.as_view(), name='genes_alleles_reference'),
    #path('get_all_alleles_combinations/', AllelesCombinationsAllListView.as_view(), name='get_all_alleles_combinations'),
    #path('get_allelescombinations_by_gene_id/<str:name>/', AllelesCombinationsByIDListView.as_view(), name='get_allelescombinations_by_gene_id'),
    #path('get_reverse_engineering/', GetReverseEngineeringView.as_view(), name='get_reverse_engineering'),
    #path('get_patience_reverse_engineering/', GetPatienceReverseEngineeringView.as_view(), name='get_patience_reverse_engineering'),
    # Nuevos endpoint adicionados para manejar los requerimientos de las pruebas
    #path('tests/user/<str:user_code>/', UserTestResultsView.as_view(), name='user-test-results'),
    path('tests/test/<str:test_code>/', TestResultDetailView.as_view(), name='test-result-detail'),
    #path('tests/user/<str:user_code>/test/<str:test_code>/', TestResultDetailView.as_view(), name='specific-test-result'),
    path('tests/search/', TestResultSearchView.as_view(), name='test-result-search'),
    path('tests/delete/<str:test_code>/', TestResultDeleteView.as_view(), name='test-result-delete'),
    #path('tests/delete/user/<str:user_code>/', UserTestResultsDeleteView.as_view(), name='test-user-delete'),
    path('tests/<str:test_code>/patient/<str:patient_code>/pdf/', TestPatientsPDFView.as_view(), 
        name='test-paciente-pdf'),
    path('tests/<str:test_code>/patient-codes/', PatientCodesByTestView.as_view(), name='patient-codes-by-test'),
    path('tests/delete-all-test', AllTestResultsDeleteView.as_view(), name='delete-all-test'),
    path('reverse/file/import-data/', GeneImportAPIView.as_view(), name='import_data'),
    #path('reverse/file/load/', ExcelUploadView.as_view(), name='load_file'),
    #path('reverse/file/proccess_reverse/', ExcelUploadForReverseEngineeringView.as_view(), name='proccess_reverse'), 
    #path('reverse/file/reverse_json/', ReverseEngineeringJSONView.as_view(), name='reverse_json'),
    path('reverse/file/proccess_reverse_excel/', ExcelUpDownloadForReverseEngineeringView.as_view(), name='proccess_reverse_excel'), # este es reverse
    path('reverse/file/download-result/<str:test_code>/', TestResultDownloadView.as_view(), name='download_test_result'), # este es reverse
] 

if settings.DEBUG:
    urlpatterns += [
        path('api/dev/clean-database/', DevelopmentCleanupView.as_view(), name='dev-clean-database'),
    ]


urlpatterns += urlpatterns 

