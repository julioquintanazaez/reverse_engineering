from rest_framework import serializers 
from ..models.genes import Genes
from ..serializers.allelesserializer import AllelesSerializer

# Create your serializers here.

class GenesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genes  
        fields = '__all__'

    def validate_id(self, value):
        """
        Validar que el gen existe en la base de datos.
        """
        try:
            gene = Genes.objects.get(name=value)
        except Genes.DoesNotExist:
            raise serializers.ValidationError("El gen con este ID no existe.")
        return gene  # Devuelve el objeto validado
    
class Genes_AllelesSerializer(serializers.ModelSerializer):
    gene_body = AllelesSerializer(many=True, read_only=True)
    class Meta:
        model = Genes  
        fields = ['pk', 'name', 'gene_body']   



