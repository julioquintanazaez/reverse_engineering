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

    def reveng_patience(self, genes_data): 
        """
        Parámetros:
          1.- patient_data: is a dictionary of genes,
              each gene contains a list of tuples with genes and alleles pairs
        """
        genes_result = []
        #print(genes_data)
        for value in genes_data:
            # Mandar a calcular la ingeniería inversa para el gen y su par de alleles
            geninfo = value.split(">")
            gen = geninfo[0]
            alleles = geninfo[1].split("/")
            try:
                gene = Genes.objects.filter(name=gen)
                gen_serializer = GenesSerializer(gene, many=True) 
                gen_name = gen_serializer.data[0]["name"]   
                gen_id = gen_serializer.data[0]["id"]
                result = self.processes_alleles_pair_extend(gen_id, alleles)
                genes_result.append({gen_name: result})
                #print(f"Gen result.................{result}")
                #print(f"----------------------------------------")
            except:
                #genes_result.append({gen_name: "Fail................"})
                print(f"Fail with gene.................{gen}")

        return {"response": genes_result}

    def reveng_patience(self, genes_data): 
        """
        Parámetros:
          1.- patient_data: is a dictionary of genes,
              each gene contains a list of tuples with genes and alleles pairs
        """
        genes_result = []
        #print(genes_data)
        for value in genes_data:
            # Mandar a calcular la ingeniería inversa para el gen y su par de alleles
            geninfo = value.split(">")
            gen = geninfo[0]
            alleles = geninfo[1].split("/")
            try:
                gene = Genes.objects.filter(name=gen)
                gen_serializer = GenesSerializer(gene, many=True) 
                gen_name = gen_serializer.data[0]["name"]   
                gen_id = gen_serializer.data[0]["id"]
                result = self.processes_alleles_pair_extend(gen_id, alleles)
                genes_result.append({gen_name: result})
                #print(f"Gen result.................{result}")
                #print(f"----------------------------------------")
            except:
                #genes_result.append({gen_name: "Fail................"})
                print(f"Fail with gene.................{gen}")

        return {"response": genes_result}
    
    def processes_alleles_pair_extend(self, gen_id, alleles_pair):   
        snps_con = []     
        snps_notcon = []     
        # Extraer los SNP de los alleles de la tabla Alleles Referent
        dbsnp_cum = self.get_alleles_reference_data(gen_id, alleles_pair)   
        # Calcular la frecuencia de los alleles que contribuyen    
        freq_rs = Counter(dbsnp_cum.split("+"))
        #print(freq_rs)
        # Obtengo y proceso los nombres de los alleles que no contribuyen
        snps_notcon = self.processes_alleles_not_relevant(gen_id, freq_rs)
        # Proceso los alleles que contribuyen
        snps_con = self.processes_alleles_relevant(freq_rs, alleles_pair)
        return snps_con + snps_notcon
    

    def get_alleles_reference_data(self, gen_id, alleles_pair):
        a1_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles_pair[0])
        a1_ref_serializer = AllelesReferenceSerializer(a1_ref, many=True)
        a1_ref_dbsnp = a1_ref_serializer.data[0]["dbsnp"]
        a2_ref = Alleles_Reference.objects.filter(gene=gen_id, allele_ref=alleles_pair[1])
        a2_ref_serializer = AllelesReferenceSerializer(a2_ref, many=True)
        a2_ref_dbsnp = a2_ref_serializer.data[0]["dbsnp"]
        return a1_ref_dbsnp + "+" + a2_ref_dbsnp 
    

    def processes_alleles_not_relevant(self, gen_id, freq_rs):
        #print(f"Entro....a procesar alleles no relevantes")
        notcont_snp = []
        freq_rs_not = Counter(get_genes_rs_not_contribution_by_alleles_pair(gen_id, freq_rs))
        #print(f"{gen_id}")
        #print(freq_rs_not)
        #print(f"-----------------------------------------")
        for marker in freq_rs_not:
            alleles_in = Alleles.objects.filter(marker=marker) 
            alleles_in_serializer = AllelesSerializer(alleles_in, many=True)
            for item in alleles_in_serializer.data:
                notcont_snp.append({
                    #"allele": item["allele"],
                    "marker": item["marker"],
                    "formula": self.h_fromula.proccess_formula(item["formula"], 0),
                    "freq": 0,
                })
                m = item["marker"]
                f = self.h_fromula.proccess_formula(item["formula"], 0)
                #print(f"Gen {m}: con formula: {f}")
        return notcont_snp
    
    
    def processes_alleles_relevant(self, freq_rs, alleles_pair):
        cont_snp = []
        for marker in freq_rs:
            query_alleles = Alleles.objects.filter(marker=marker) 
            query_serializer = AllelesSerializer(query_alleles, many=True)
            alleles_info = self.get_dict_from_alleles_serialized(query_serializer.data)
            a_ambiguity = self.alleles_ambiguity_number(alleles_info, alleles_pair) 
            if len(alleles_info) == 0 : # Marker igual None descartar
                #print("Vacio-o marker igual None----------------")
                cont_snp.append({
                    "marker": marker, 
                    "formula": None,
                    "freq": None
                })     
            elif len(alleles_info) > 0 and len(alleles_info) < 2:  # un marcador no ambiguo y allele único  
                #print(f"Marcador único no ambiguo")  
                freqencia = freq_rs[marker]
                alleles_info = alleles_info[0]
                cont_snp.append({
                    "marker": marker, 
                    "formula": self.h_fromula.proccess_formula(alleles_info["formula"], freqencia),
                    "freq": freqencia
                })     
            else: # Cuando los marcadores generan ambiguadad
                if len(a_ambiguity) != 0: # Si la ambiguedad != 0, vincula alleles que pertenecen al par formador
                    if len(a_ambiguity) > 0 and len(a_ambiguity) < 2 and (alleles_pair[0] != alleles_pair[1]): 
                         # un marcador ambiguo para un solo allele vinculado al par formador, par formador distinto           
                        #print(f"Marcador único ambiguo")
                        freqencia = freq_rs[marker]
                        a_ambiguity = a_ambiguity[0]     
                        cont_snp.append({
                            "marker": marker, 
                            "formula": self.h_fromula.proccess_formula(a_ambiguity["formula"], freqencia),
                            "freq": freqencia
                        })                        
                    else:
                        if alleles_pair[0] == alleles_pair[1]: 
                            # un marcador ambiguo para más de un allele, vinculado al par formador, par igual: *5/*5
                            #print(f"Marcador ambiguo para alleles similares")
                            freqencia = freq_rs[marker]  
                            a_ambiguity = a_ambiguity[0]
                            cont_snp.append({
                                "marker": marker, 
                                "formula": self.h_fromula.proccess_formula(a_ambiguity["formula"], freqencia),
                                "freq": freqencia
                            })
                        else:  # un marcador ambiguo para más de una allele, vinculados al par formador, par formador distinto: *5/*7
                            #print(f"Marcador ambiguo para alleles distintios")
                            temp_formulas = []
                            freqencia = freq_rs[marker]
                            a_ambiguity = a_ambiguity
                            for item_alleles in a_ambiguity:
                                if item_alleles["allele"] in alleles_pair:
                                    temp_formulas.append(item_alleles["formula"])
                            if self.h_fromula.if_exist_formula(temp_formulas[0], temp_formulas[1]): 
                                #print(f"Existe fórmula para los dos")
                                similar_token = self.h_fromula.join_formula_ambigua(temp_formulas[0], temp_formulas[1])
                                cont_snp.append({
                                    "marker": marker,
                                    "formula": similar_token,
                                    "freq": "1a"
                                })
                            else:
                                #print(f"No existe fórmula para los dos")
                                freqencia = freq_rs[marker]
                                a_ambiguity = a_ambiguity[0]
                                cont_snp.append({
                                    "marker": marker, 
                                    "formula": self.h_fromula.proccess_formula(a_ambiguity["formula"], freqencia),
                                    "freq": freqencia
                                })
                else: # Si la ambiguedad es entre alleles que no pertenecen al par formador
                    freqencia = freq_rs[marker]
                    alleles_info = alleles_info[0]
                    cont_snp.append({
                        "marker": marker, 
                        "formula": self.h_fromula.proccess_formula(alleles_info["formula"], freqencia),
                        "freq": freqencia
                    }) 

        return cont_snp
    

    def get_dict_from_alleles_serialized(self, serialized_query):
        # Devuelve la lista de alleles asiciado a un par formador
        temp_alleles = []
        for item_alleles in serialized_query:
            temp_alleles.append({
                "allele": item_alleles["allele"],
                "marker": item_alleles["marker"],
                "formula": item_alleles["formula"],
            })
        return temp_alleles
    
    def alleles_ambiguity_number(self, alleles_info, alleles_pair):
        # Devuelve la lista de alleles asociado a un par formador
        alleles = []
        for item_alleles in alleles_info:
            if item_alleles["allele"] in alleles_pair:
                alleles.append({
                    "allele": item_alleles["allele"],
                    "formula": item_alleles["formula"],
                })
        return alleles

    
    

    
    

    