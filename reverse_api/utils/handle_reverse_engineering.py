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
            info_snp = self.processes_alleles_pair_extend(gen_id, alleles)
            alleles_combinations.append({
                                        "name" : alleles_pair,
                                        "snps" : info_snp
                                    })
            genes_list.append({
                            "gen_name" : gen_name,
                            "alleles_pair": alleles_combinations
                        }) 
        return genes_list

    def get_alleles_reference_data(self, gen_id, alleles_pair):
        a1_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles_pair[0])
        a1_ref_serializer = AllelesReferenceSerializer(a1_ref, many=True)
        a1_ref_dbsnp = a1_ref_serializer.data[0]["dbsnp"]
        a2_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles_pair[1])
        a2_ref_serializer = AllelesReferenceSerializer(a2_ref, many=True)
        a2_ref_dbsnp = a2_ref_serializer.data[0]["dbsnp"]
        return a1_ref_dbsnp + "+" + a2_ref_dbsnp 

    # Puede que en la consulta al modelo ya pueda extraer los valores
    def extract_alleles_names_from_marker(self, dict_from_marker):
        res = []
        for item in dict_from_marker:
            res.append(item['allele'])
        return res
    
    def extract_alleles_names_from_marker_by_pair(self, dict_from_marker, alleles_pair):
        res = []
        for item in dict_from_marker:
            if item["allele"] in alleles_pair:
                res.append(item['allele'])
        return res

    def check_alleles_pair_from_marker(self, pair, data_from_marker):
        first = pair[0] in data_from_marker
        second = pair[1] in data_from_marker
        return first and second
    
    def get_alleles_dict(self, gen_id):
        temp_alleles = []
        query = Alleles.objects.filter(gene=gen_id)
        serialized_query = AllelesSerializer(query, many=True)
        for item in serialized_query.data:
            temp_alleles.append({
                "allele": item["allele"],
                "marker": item["marker"],
                "formula": item["formula"],
                "freq": 0,
            })
        return temp_alleles
    
    def check_contribution(self, alleles_list, snp_dict, pair_alleles):
        snp_keys = list(snp_dict.keys())
        print(snp_dict)
        for item in alleles_list:
            alleles_in = Alleles.objects.filter(marker=item["marker"]) 
            alleles_in_serializer = AllelesSerializer(alleles_in, many=True)
            alleles_from_marker = self.extract_alleles_names_from_marker(alleles_in_serializer.data)
            allele = item["allele"]
            marker = item["marker"]
            # Si alleles from marker es mayor que uno quiere decir que el marcador contribuye a dos 
            # alleles o sea dos alleles tiene similar marcador
            if (marker in snp_keys):
                if len(alleles_from_marker) > 1 and (allele in pair_alleles) and (pair_alleles[0] != pair_alleles[1]): 
                    item["formula"] = self.h_fromula.proccess_formula(item["formula"], 4)
                    print(f"formula extendida para alleles {allele} snp {marker}")
                else:
                    freq_value = snp_dict[marker]
                    item["formula"] = self.h_fromula.proccess_formula(item["formula"], freq_value)
                    print(f"formula normal para alleles {allele} snp {marker} con frecuencia {freq_value}")
            else:
                freq_value = item["freq"]
                item["formula"] = self.h_fromula.proccess_formula(item["formula"], freq_value)
                print(f"formula en cero para alleles {allele} snp {marker} con frecuencia {freq_value}")
        return alleles_list

    def processes_alleles_pair_extendI(self, gen_id, alleles_pair):   
        snps = []     
        dbsnp_cum = self.get_alleles_reference_data(gen_id, alleles_pair)          
        freq_rs = Counter(dbsnp_cum.split("+"))#.items() # Aquí tengo los que contribuyen {"rs1": 1, "rs2": 2}
        alleles_list = self.get_alleles_dict(gen_id)
        snps = self.check_contribution(alleles_list, freq_rs, alleles_pair)
        return snps

    def processes_alleles_not_relevant(self, gen_id, freq_rs):
        notcont_snp = []
        freq_rs_not = Counter(get_genes_rs_not_contribution_by_alleles_pair(gen_id, freq_rs))
        #print(freq_rs_not)
        for marker in freq_rs_not:
            alleles_in = Alleles.objects.filter(marker=marker) 
            alleles_in_serializer = AllelesSerializer(alleles_in, many=True)
            for item in alleles_in_serializer.data:
                notcont_snp.append({
                    "allele": item["allele"],
                    "marker": item["marker"],
                    "formula": self.h_fromula.proccess_formula(item["formula"], 0),
                    "freq": 0,
                })
        return notcont_snp
    
    def processes_alleles_relevant(self, freq_rs, alleles_pair):
        cont_snp = []
        for marker in freq_rs:
            alleles_in = Alleles.objects.filter(marker=marker) 
            alleles_in_serializer = AllelesSerializer(alleles_in, many=True)
            alleles_from_marker = self.extract_alleles_names_from_marker_by_pair(alleles_in_serializer.data, alleles_pair)
            # Si el marcador o snp contribuye para un solo allele aplicar la formula normal
            if len(alleles_from_marker) < 2:
                print(f"{marker} con freuencia {freq_rs[marker]}")
                print(f"El marcador {marker} Contribuye para un solo allele")
                for item_alleles in alleles_in_serializer.data:
                    if item_alleles["allele"] in alleles_pair:
                        freqencia = freq_rs[marker]
                        cont_snp.append({
                            "marker": marker, #item_alleles["marker"],
                            "formula": self.h_fromula.proccess_formula(item_alleles["formula"], freqencia),
                            "freq": freqencia
                        })
                        a = item_alleles["allele"]
                        print(f"Trabajo para un solo allele para {a} con {marker}")
            # Si el marcador o snp contribuye para más de un allele aplicar el siguiente algoritmo:
            # Si el par de elleles es el mismo, aplicar la fórmula segun frecuencia
            # Al contrario, buscar las fórmulas par de alleles introducido por el usuario
            # Comparar las formulas para el par de alleles y tomar la unión de las mismas
            else:  
                print(f"{marker} con numero de alleles {alleles_from_marker}")   
                print(f"{marker} con freuencia {freq_rs[marker]}")   
                #print(f"El marcador {marker} Contribuye para varios alleles: {list(alleles_from_marker)}")
                if alleles_pair[0] == alleles_pair[1]:
                    freqencia = freq_rs[marker]
                    print(f"Los alleles del par son iguales el procesamiento es por la frecuencia {freqencia}")
                    for item_alleles in alleles_in_serializer.data:                        
                        if item_alleles["allele"] == alleles_pair[0]:
                            #print(item_alleles["allele"])
                            cont_snp.append({
                                "marker": marker, #item_alleles["marker"],
                                "formula": self.h_fromula.proccess_formula(item_alleles["formula"], freqencia),
                                "freq": freqencia
                            })
                else:
                    print(f"Los alleles del par no son iguales el procesamiento es por ambiguedad entre {alleles_pair}")
                    temp_formulas = []
                    freqencia = freq_rs[marker]
                    for item_alleles in alleles_in_serializer.data:
                        if item_alleles["allele"] in alleles_pair:
                            temp_formulas.append(item_alleles["formula"])
                            a = item_alleles["allele"]
                            f = item_alleles["formula"]
                            print(f"Fórmula para {a} con {marker}")
                    print(f"Longitud de la lista de fórmulas a comparar {len(temp_formulas)}")
                    # Selecciona por defecto la parte de la fórmula 1a
                    similar_token = self.h_fromula.join_formula_ambigua(temp_formulas[0], temp_formulas[1])
                    cont_snp.append({
                        "marker": marker,
                        "formula": similar_token,
                        "freq": "1a"
                    })
        return cont_snp


    def processes_alleles_pair_extend(self, gen_id, alleles_pair):   
        snps_con = []     
        snps_notcon = []     
        # Extraer los SNP de los alleles de la tabla Alleles Referent
        dbsnp_cum = self.get_alleles_reference_data(gen_id, alleles_pair)   
        # Calcular la frecuencia de los alleles que contribuyen               
        freq_rs = Counter(dbsnp_cum.split("+"))
        print(freq_rs)
        # Obtengo y proceso los nombres de los alleles que no contribuyen
        snps_notcon = self.processes_alleles_not_relevant(gen_id, freq_rs)
        # Proceso los alleles que contribuyen
        snps_con = self.processes_alleles_relevant(freq_rs, alleles_pair)
        return snps_con + snps_notcon

    def processes_alleles_pair(self, gen_id, alleles_pair):   
        snps = []     
        dbsnp_cum = self.get_alleles_reference_data(gen_id, alleles_pair)          
        freq_rs = Counter(dbsnp_cum.split("+")).items() # Aquí tengo los que contribuyen {"rs1": 1, "rs2": 2}
        freq_rs_not = Counter(get_genes_rs_not_contribution_by_alleles_pair(gen_id, freq_rs)).items() #{"rs3": 0, "rs4": 0}
        freq_rs_not = self.h_fromula.set_frequece_for_not_contrib(freq_rs_not)
        freq_rs_all = dict(list(freq_rs) + list(freq_rs_not)) 
        for key_marker, freq_value in freq_rs_all.items():
            marker_alleles = Alleles.objects.filter(marker=key_marker) 
            if marker_alleles != None:
                marker_serializer = AllelesSerializer(marker_alleles, many=True)
                alleles_from_marker = self.extract_alleles_names_from_marker(marker_serializer.data)
                iqual_alleles = (alleles_pair[0] == alleles_pair[1])
                alleles_in_snp = self.check_alleles_pair_from_marker(alleles_pair, alleles_from_marker)
                for item in marker_serializer.data:
                    formula_ = "None"      
                    try: 
                        if alleles_in_snp and not iqual_alleles:
                            formula_ = self.h_fromula.proccess_formula(item["formula"], 4)
                            snps.append({
                                "allele": item["allele"],
                                "snpname": item["marker"],
                                "formula": formula_,
                                "f_value": 4
                            })
                        else:
                            formula_ = self.h_fromula.proccess_formula(item["formula"], freq_value)
                            f_value_ = freq_value
                            snps.append({
                                "allele": item["allele"],
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
                                    "allele": item["allele"],
                                    "snpname": item["marker"],
                                    "formula": formula_,
                                    "f_value": -1
                                })
            else:
                snps.append({
                    "allele": None,
                    "snpname": None,
                    "formula": None,
                    "f_value": -1
                })

        return snps
    

    