from rest_framework import serializers 
from ..models.allelesreference import Alleles_Reference
from ..models.allelescombinations import Alleles_Combinations
from ..serializers.allelescombinarionsserializers import AllelesCombinationsSerializer
from ..serializers.genesallelesreferenceerializer import GeneAllelesSerializer
from ..models.genes import Genes
from rest_framework import status  
from rest_framework.response import Response  


# Create your serializers here.    
   
class AllelesPairSerializer(serializers.Serializer):
    gen = serializers.CharField(max_length=100)
    alleles_pair = serializers.CharField(max_length=100)

    def validate(self, value):
        # Verificar que el gen exista en la base de datos
        gen_name = value.get('gen')
        alleles_pair = value.get('alleles_pair')    

        if not Genes.objects.filter(name=gen_name).exists():
            raise serializers.ValidationError(f"Gen'{gen_name}' does not exist in database")
        
        gene = Genes.objects.get(name=gen_name)

        if not alleles_pair or not isinstance(alleles_pair, str):
            raise serializers.ValidationError("La combinación de alelos debe ser una cadena no vacía.")
        
        aapair = alleles_pair.split("/")
        if len(aapair) != 2 or not all(part for part in aapair):
            raise serializers.ValidationError("La combinación de alelos debe seguir el formato '*x/*y'.")
    
        #if not Alleles_Combinations.objects.filter(gene=gene, allele_combinations=alleles_pair).exists():
        #    raise serializers.ValidationError(f"This combination '{alleles_pair}' does not belongs to gen '{gen_name}' or does not exist in DB.")

        if not Alleles_Reference.objects.filter(gene=gene, allele_ref=aapair[0]).exists():
            raise serializers.ValidationError(f"Allele {aapair[0]} does not exist for {gen_name}")
        
        if not Alleles_Reference.objects.filter(gene=gene, allele_ref=aapair[1]).exists():
            raise serializers.ValidationError(f"Allele {aapair[1]} does not exist for {gen_name}")

        return value
    
class PatienceGenesAllelesReferenceSerializer(serializers.Serializer):
    patience = serializers.CharField(max_length=100)
    gene_data = AllelesPairSerializer(many=True)
    def validate(self, attrs):
        genes = attrs.get('gene_data')
        for gen in genes:
            AllelesPairSerializer().validate(gen)
        return attrs
    
class ListPatienceGenesAllelesReferenceSerializer(serializers.Serializer):
    patience_list = PatienceGenesAllelesReferenceSerializer(many=True)
    def validate(self, attrs):
        patience = attrs.get('patience_list')
        for patience in patience:
            PatienceGenesAllelesReferenceSerializer().validate(patience)
        return attrs
    
    