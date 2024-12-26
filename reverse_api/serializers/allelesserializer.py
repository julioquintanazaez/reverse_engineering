from rest_framework import serializers 
from ..models.alleles import Alleles


# Create your serializers here.

class AllelesSerializer(serializers.ModelSerializer):
    gene_name = serializers.CharField(source='gene.name', read_only=True)
    class Meta:
        model = Alleles  
        fields = [
            'protein_change',
            'nucleotide_change',
            'allele',
            'marker',
            'genotype',
            'formula',
            'gene_name',
            'snp'
        ]

    
    