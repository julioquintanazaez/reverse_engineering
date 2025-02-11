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
from ..utils.handle_alleles_data import get_genes_rs_not_contribution_by_alleles_pair

# Nuevo método
class Handle_Reverse_Engineering(): 
    h_fromula = HandleFormulaUtils()

    def __inint__(self):
        pass

    
    def get_reverse_engineering(self, parent_data): 
        """
        Est función recive como parámetro (parent_data) datos de los genes y sus alleles de referencia para calcular
        la ingeniería inversa. La estructura de parámetros de entrada es:
        #data={'gen_list': [{'gen': 'CYP1A1', 'alleles_list': ['*3/*4', '*6/*8']}]}
        """
        genes_list = []
        gen_list = parent_data["gen_list"]
        for gen_item in gen_list:
            gene = Genes.objects.filter(name=gen_item["gen"])
            gen_serializer = GenesSerializer(gene, many=True) 
            gen_name = gen_serializer.data[0]["name"]   
            gen_id = gen_serializer.data[0]["id"]
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
                                formula_ = self.h_fromula.filter_lower_case_formula(
                                    self.h_fromula.proccess_entry_formula(item["formula"], freq_value)
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
    

    def get_patience_reverse_engineering(self, parent_data): 
        """
        Est función recive como parámetro (parent_data) datos de los genes y sus alleles de referencia para calcular
        la ingeniería inversa. La estructura de parámetros de entrada es:
        #data={'gen_list': [{'gen': 'CYP1A1', 'alleles_list': ['*3/*4', '*6/*8']}]}
        """
        genes_list = []
        
        gen_list = parent_data["gene_data"]
        for gen_item in gen_list:
            gene = Genes.objects.filter(name=gen_item["gen"])
            gen_serializer = GenesSerializer(gene, many=True) 
            gen_name = gen_serializer.data[0]["name"]   
            gen_id = gen_serializer.data[0]["id"]
            alleles_pair = gen_item["alleles_pair"] # Extraigo el par de alleles
            alleles_combinations = []
            alleles = alleles_pair.split("/")
            info_snp = self.processes_alleles_pair(gen_id, alleles)
            alleles_combinations.append({
                                        "name" : alleles_pair,
                                        "snps" : info_snp
                                    })
            genes_list.append({
                            "gen_name" : gen_name,
                            "alleles_pair": alleles_combinations
                        }) 
        return genes_list

    def processes_alleles_pair(self, gen_id, alleles_pair):   
        snps = []     
        a1_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles_pair[0])
        a1_ref_serializer = AllelesReferenceSerializer(a1_ref, many=True)
        a1_ref_dbsnp = a1_ref_serializer.data[0]["dbsnp"]
        a2_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles_pair[1])
        a2_ref_serializer = AllelesReferenceSerializer(a2_ref, many=True)
        a2_ref_dbsnp = a2_ref_serializer.data[0]["dbsnp"]
        dbsnp_cum = a1_ref_dbsnp + "+" + a2_ref_dbsnp  
        freq_rs = Counter(dbsnp_cum.split("+")).items() # Aquí tengo los que contribuyen {"rs1": 1, "rs2": 2}
        freq_rs_not = Counter(get_genes_rs_not_contribution_by_alleles_pair(gen_id, freq_rs)).items() #{"rs3": 0, "rs4": 0}
        freq_rs_not = self.h_fromula.set_frequece_for_not_contrib(freq_rs_not)
        freq_rs_all = dict(list(freq_rs) + list(freq_rs_not)) 
        for key_marker, freq_value in freq_rs_all.items():
            marker_exist = Alleles.objects.filter(marker=key_marker) 
            if marker_exist != None: # Existe nen la base de datos
                marker_serializer = AllelesSerializer(marker_exist, many=True)
                for item in marker_serializer.data:
                    formula_ = "None"      
                    try:    
                        formula_ = self.h_fromula.filter_lower_case_formula(
                            self.h_fromula.proccess_entry_formula(item["formula"], freq_value)
                        )
                        f_value_ = freq_value
                        snps.append({
                            "snpname": item["marker"],
                            "formula": formula_,
                            "f_value": f_value_
                        })
                    except:
                        print(f"Unknow formula for gene {gen_id} and marker {key_marker}")
                        formula_ = f"Unknow formula for gene and marker {key_marker}"
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

        return snps
    

    