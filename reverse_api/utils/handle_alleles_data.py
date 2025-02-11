from ..models.alleles import Alleles

#Los alleles que no contribuyen se buscan en el modelo Alleles ya que ellos no son 
# objetivo de Allele_Reference
def get_genes_rs_not_contribution_by_alleles_pair(gen_id, allele_freq):
    temp_alleles = []
    for alleles, _ in allele_freq:
        temp_alleles.append(alleles)
    alleles_not_cont = Alleles.objects.filter(
        gene=gen_id
    ).exclude(
        marker__in=temp_alleles
    ).values_list('marker', flat=True)
    return alleles_not_cont
    
   