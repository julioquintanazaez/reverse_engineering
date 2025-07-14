from ..models.alleles import Alleles

#Los alleles que no contribuyen se buscan en el modelo Alleles ya que ellos no son 
# objetivo de Allele_Reference
def get_genes_rs_not_contribution_by_alleles_pair(gen_id, allele_freq):
    #print("Entro a extraer")
    temp_alleles = []
    for alleles in allele_freq:
        temp_alleles.append(alleles)
    all_alleles = Alleles.objects.filter(
        gene=gen_id
    ).values_list('marker', flat=True)
    all_alleles = list(set(all_alleles))
    alleles_not_cont = list(filter(lambda x: x not in temp_alleles, all_alleles))

    #print("Salio a extraer")
    #print(f"{gen_id}")
    #print(f"{temp_alleles}")
    #print(f"{all_alleles}")
    #print(f"{alleles_not_cont}")
    #print(f"----------------------------------------")
    return alleles_not_cont
    
   
    """
    alleles_not_cont = Alleles.objects.filter(
        gene=gen_id
    ).exclude(
        marker__in=temp_alleles
    ).values_list('marker', flat=True)
    """