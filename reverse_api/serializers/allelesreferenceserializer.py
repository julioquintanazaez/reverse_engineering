from rest_framework import serializers 
from ..models.allelesreference import Alleles_Reference
from ..models.genes import Genes


# Create your serializers here.

class AllelesReferenceSerializer(serializers.ModelSerializer):
    gene_name = serializers.CharField(source='gene.name', read_only=True)
    class Meta:
        model = Alleles_Reference  
        fields = [
            'dbsnp',
            'allele_ref',
            'gene_name',
        ]

