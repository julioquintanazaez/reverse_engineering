from django.urls import include, path
from rest_framework import routers
from .views.exceluploadview import ExcelUploadView
from .views.exceluploadallelescombinations import ExcelUploadForReverseEngineeringView
from .views.genesview import GenesListView, GenesAllelesListView
from .views.allelesview import AllelesListView
from .views.allelescombinationsviews import AllelesCombinationsByIDListView, AllelesCombinationsAllListView
from .views.allelesreferenceview import AllelesReferenceListView, GetReverseEngineeringView
from .views.patiencegeneallelereference import GetPatienceReverseEngineeringView

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
    path('load/', ExcelUploadView.as_view(), name='load_file'),
    path('genes/', GenesListView.as_view(), name='genes'),
    path('alleles/', AllelesListView.as_view(), name='alleles'),
    path('genes_alleles/', GenesAllelesListView.as_view(), name='genes_alleles'),
    path('genes_alleles_reference/', AllelesReferenceListView.as_view(), name='genes_alleles_reference'),
    path('get_all_alleles_combinations/', AllelesCombinationsAllListView.as_view(), name='get_all_alleles_combinations'),
    path('get_allelescombinations_by_gene_id/<str:name>/', AllelesCombinationsByIDListView.as_view(), name='get_allelescombinations_by_gene_id'),
    #path('get_reverse_engineering/', GetReverseEngineeringView.as_view(), name='get_reverse_engineering'),
    path('get_patience_reverse_engineering/', GetPatienceReverseEngineeringView.as_view(), name='get_patience_reverse_engineering'),
    path('loadallelecombination/', ExcelUploadForReverseEngineeringView.as_view(), name='loadallelecombination'),
]

urlpatterns += urlpatterns 