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
        la ingeniería inversa. La estructura de los datos es:
        #data={'gen_list': [{'gen': 'CYP1A1', 'alleles_list': ['*3/*4', '*6/*8']}]}
        """
        h_fromula = HandleFormulaUtils()

        dict_genes = {} # Creamos un dict para almacenar cada Gen

        gen_list = parent_data["gen_list"]
        for gen_item in gen_list:
            gene = Genes.objects.filter(name=gen_item["gen"])
            gen_serializer = GenesSerializer(gene, many=True) # Serializarla
            gen_name = gen_serializer.data[0]["name"]   
            gen_id = gen_serializer.data[0]["id"]  #Chequear que los genes existan en la base de datos
            gen_alleles_list = gen_item["alleles_list"] # Extraigo la lista de alleles del dict de entrada para el gen    
            dict_alleles = {} # Creamos un dict para almacenar cada par de alleles
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
                # Iterar sobre el diccionario de RS y sus frecuencias
                dict_rs_form = {} # Creamos un dict para los rs y su fórmula específica
                for key_marker, freq_value in freq_rs:
                    # Hacer las consultas por rs a la tabla Alleles 
                    marker_exist = Alleles.objects.filter(marker=key_marker) #.exists()
                    if marker_exist != None:
                        #print(f"Marker: {key_marker}------EXISTE------------") 
                        marker_serializer = AllelesSerializer(marker_exist, many=True)
                        for item in marker_serializer.data:
                            formula_ = "None"
                            try:                                
                                formula_ = h_fromula.filter_lower_case_formula(
                                    h_fromula.proccess_entry_formula(item["formula"], freq_value)
                                )
                                f_value_ = freq_value
                            except:
                                print(f"Unknow formula for gene {gen_name} and marker {key_marker}")
                                formula_ = f"Unknow formula for gene {gen_name} and marker {key_marker}"
                                f_value_ = 0
                            
                            dict_rs_form[item["marker"]] = {
                                                    "formula": formula_,
                                                    "f_value": f_value_
                                                } # Actualizo la información para el RS_i

                    else:
                        dict_rs_form[key_marker] = "None"

                dict_alleles[alleles_pair] = dict_rs_form  # Adicionamos contenido del dict RS para cada par de alleles            
                dict_genes[gen_name] = dict_alleles # Adicionamos el dict de alleles al dict de Genes

        return (dict_genes)