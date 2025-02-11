from ..models.genes import Genes
from ..models.allelescombinations import Alleles_Combinations

from itertools import combinations 
from itertools import product


class Handle_Alleles_Combinations(): 

    def __inint__(self):
        pass

    def fill_Alleles_Combinations(self): 
        # Obtener todos loas genes de la base de datos
        genes = Genes.objects.all()
        # Iterar sobre cada gen 
        for gen in genes:
            # obtener todos los alleles de referencia
            gene_ref = gen.gene_ref.all()
            # Guardar los nombres de los alleles para calcular sus combinaciones
            aleles_names = [allele.allele_ref for allele in gene_ref]
            # Generar todas las combinaciones por pares sin repeticiones
            #combinations_alleles_by_pairs = list(combinations(aleles_names, 2))
            combinations_alleles_by_pairs = [(a, b) for a in aleles_names for b in aleles_names] #list(combinations(aleles_names, 2))
            # Mostrar resultados
            for combinacion in combinations_alleles_by_pairs:
                # Adicionar en la base de datos de combinaciones
                str_combination = f"{combinacion[0]}/{combinacion[1]}"
                C1 = "*5"
                C2 = "XN"
                # Si la combinación ("*5", "XN") o ("XN", "*5") no sucede
                if  (C1 == combinacion[0] and C2 in combinacion[1]) or (C2 in combinacion[0] and C1 == combinacion[1]):
                    #print(f"Combinación no posible -----------{str_combination}--------------------------") 
                    pass
                else:                    
                    _, _ = Alleles_Combinations.objects.get_or_create(
                                allele_combinations = str_combination,
                                gene=gen
                            ) 

        return "Correct"

