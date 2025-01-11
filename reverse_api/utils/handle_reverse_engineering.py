from collections import Counter
from rest_framework import status  
from rest_framework.response import Response  

from ..serializers.geneserializer import GenesSerializer
from ..serializers.allelesreferenceserializer import AllelesReferenceSerializer
from ..serializers.allelesserializer import AllelesSerializer

from ..models.allelesreference import Alleles_Reference
from ..models.alleles import Alleles
from ..models.genes import Genes

from ..utils.handle_formula import HandleFormulaUtils

# Nuevo método
class Handle_Reverse_Engineering(): 

    def __inint__(self):
        #h_fromula = HandleFormulaUtils()
        pass

    
    def get_reverse_engineering(self, parent_data): 
        """
        Est función recive como parámetro (parent_data) datos de los genes y sus alleles de referencia para calcular
        la ingeniería inversa. La estructura de parámetros de entrada es:
        #data={'gen_list': [{'gen': 'CYP1A1', 'alleles_list': ['*3/*4', '*6/*8']}]}
        """
        h_fromula = HandleFormulaUtils()

        gen_list = parent_data["gen_list"]
        genes_list = []
        for gen_item in gen_list:
            gene = Genes.objects.filter(name=gen_item["gen"])
            gen_serializer = GenesSerializer(gene, many=True) # Serializarla
            gen_name = gen_serializer.data[0]["name"]   
            gen_id = gen_serializer.data[0]["id"]  #Chequear que los genes existan en la base de datos
            gen_alleles_list = gen_item["alleles_list"] # Extraigo la lista de alleles del dict de entrada para el gen    
            alleles_combinations = []
            for alleles_pair in gen_alleles_list: # Iterar sobre la lista de alleles 
                alleles = alleles_pair.split("/")
                a1_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles[0])
                a1_ref_serializer = AllelesReferenceSerializer(a1_ref, many=True)
                a1_ref_dbsnp = a1_ref_serializer.data[0]["dbsnp"]
                a2_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles[1])
                a2_ref_serializer = AllelesReferenceSerializer(a2_ref, many=True)
                a2_ref_dbsnp = a2_ref_serializer.data[0]["dbsnp"]
                dbsnp_cum = a1_ref_dbsnp + "+" + a2_ref_dbsnp  # Extraer y Combinar los dbSNP
                freq_rs = Counter(dbsnp_cum.split("+")).items() # Calculamos la frecuencia de los dbSNP(rs)
                snps = []
                for key_marker, freq_value in freq_rs:
                    marker_exist = Alleles.objects.filter(marker=key_marker) #.exists()
                    if marker_exist != None:
                        marker_serializer = AllelesSerializer(marker_exist, many=True)
                        for item in marker_serializer.data:
                            formula_ = "None"
                            try:                                
                                formula_ = h_fromula.filter_lower_case_formula(
                                    h_fromula.proccess_entry_formula(item["formula"], freq_value)
                                )
                                f_value_ = freq_value
                                snps.append({
                                    "snpname": item["marker"],
                                    "formula": formula_,
                                    "f_value": f_value_
                                })
                            except:
                                print(f"Unknow formula for gene {gen_name} and marker {key_marker}")
                                formula_ = f"Unknow formula for gene {gen_name} and marker {key_marker}"
                                f_value_ = 0    
                                #SNPs contiene lista de diccionarios de SNPname, Formula y Freq                        
                                snps.append({
                                            "snpname": item["marker"],
                                            "formula": formula_,
                                            "f_value": -1
                                        })
                    else:
                        snps.append({
                            "snpname": None,
                            "formula": None,
                            "f_value": -1
                        })
                #Alleles_combinations contien diccionarios de Name y SNPs para un par de alleles
                alleles_combinations.append({
                                            "name" : alleles_pair,
                                            "snps" : snps
                                        })
        
            genes_list.append({
                            "gen_name" : gen_name,
                            "alleles_combinations": alleles_combinations
                        }) 

        result = {"genes_list": genes_list}

        return (result)