from rest_framework import serializers 
from ..models.allelescombinations import Alleles_Combinations
from ..models.genes import Genes


# Create your serializers here.

class AllelesCombinationsSerializer(serializers.ModelSerializer):    
    gene = serializers.CharField(source='gene.name', read_only=True)
    class Meta:
        model = Alleles_Combinations  
        fields = [
            'allele_combinations',
            'gene',
        ]

