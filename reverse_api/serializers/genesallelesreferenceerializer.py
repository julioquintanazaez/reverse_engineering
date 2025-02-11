from rest_framework import serializers 
from ..models.allelesreference import Alleles_Reference
from ..models.allelescombinations import Alleles_Combinations
from ..serializers.allelescombinarionsserializers import AllelesCombinationsSerializer
from ..models.genes import Genes
from rest_framework import status  
from rest_framework.response import Response  


# Create your serializers here.

    
class GeneAllelesSerializer(serializers.Serializer):
    gen = serializers.CharField(max_length=100)
    alleles_list = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )

    def validate(self, value):
        # Verificar que el gen exista en la base de datos
        gen_name = value.get('gen')
        alleles_comb = value.get('alleles_list')    

        if not Genes.objects.filter(name=gen_name).exists():
            raise serializers.ValidationError(f"Gen'{gen_name}' does not exist in database")
        
        gene = Genes.objects.get(name=gen_name)

        for combination in alleles_comb:

            if not combination or not isinstance(combination, str):
                raise serializers.ValidationError("La combinación de alelos debe ser una cadena no vacía.")
            
            aapair = combination.split("/")
            if len(aapair) != 2 or not all(part for part in aapair):
                raise serializers.ValidationError("La combinación de alelos debe seguir el formato '*x/*y'.")
       
            if not Alleles_Combinations.objects.filter(gene=gene, allele_combinations=combination).exists():
                raise serializers.ValidationError(f"This combination '{combination}' does not belongs to gen '{gen_name}' or does not exist in DB.")

            if not Alleles_Reference.objects.filter(gene=gene, allele_ref=aapair[0]).exists():
                raise serializers.ValidationError(f"Allele {aapair[0]} does not exist for {gen_name}")
            
            if not Alleles_Reference.objects.filter(gene=gene, allele_ref=aapair[1]).exists():
                raise serializers.ValidationError(f"Allele {aapair[1]} does not exist for {gen_name}")

        return value
    
class GenesAllelesReferenceSerializer(serializers.Serializer):
    gen_list = GeneAllelesSerializer(many=True)

    def validate(self, attrs):
        genes = attrs.get('gen_list')
        for gen in genes:
            GeneAllelesSerializer().validate(gen)

        return attrs
    
    
class GeneAllelesSerializer_NotPairValidation(serializers.Serializer):
    gen = serializers.CharField(max_length=100)
    alleles_list = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )

    def validate(self, value):
        # Verificar que el gen exista en la base de datos
        gen_name = value.get('gen')
        alleles_comb = value.get('alleles_list')    

        if not Genes.objects.filter(name=gen_name).exists():
            raise serializers.ValidationError(f"Gen'{gen_name}' does not exist in database")
        
        gene = Genes.objects.get(name=gen_name)

        for combination in alleles_comb:

            if not combination or not isinstance(combination, str):
                raise serializers.ValidationError("La combinación de alelos debe ser una cadena no vacía.")
            
            aapair = combination.split("/")
            if len(aapair) != 2 or not all(part for part in aapair):
                raise serializers.ValidationError("La combinación de alelos debe seguir el formato '*x/*y'.")
       
            if not Alleles_Reference.objects.filter(gene=gene, allele_ref=aapair[0]).exists():
                raise serializers.ValidationError(f"Allele {aapair[0]} does not exist for {gen_name}")
            
            if not Alleles_Reference.objects.filter(gene=gene, allele_ref=aapair[1]).exists():
                raise serializers.ValidationError(f"Allele {aapair[1]} does not exist for {gen_name}")

        return value
    
class GenesAllelesReferenceSerializer_NotPairValidation(serializers.Serializer):
    gen_list = GeneAllelesSerializer_NotPairValidation(many=True)

    def validate(self, attrs):
        genes = attrs.get('gen_list')
        for gen in genes:
            GeneAllelesSerializer_NotPairValidation().validate(gen)

        return attrs