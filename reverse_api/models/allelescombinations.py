from django.db import models

from .genes import Genes

# Create your models here.

class Alleles_Combinations(models.Model):
    allele_combinations = models.TextField(max_length=100, blank=False)
    gene = models.ForeignKey(Genes, related_name='gene_comb', on_delete=models.CASCADE)

    def __str__(self):
        return self.allele_combinations