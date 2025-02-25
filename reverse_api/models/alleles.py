from django.db import models

from .genes import Genes

# Create your models here.

class Alleles(models.Model):
    protein_change = models.TextField(max_length=25,  blank=True, null=True)
    nucleotide_change = models.TextField(max_length=25,  blank=True, null=True)
    allele = models.TextField(max_length=25, blank=True, null=True)
    marker = models.TextField(max_length=25, blank=False)
    genotype = models.TextField(max_length=25, blank=True, null=True)    
    formula = models.TextField(max_length=100, blank=False)
    snp = models.IntegerField(blank=False)

    gene = models.ForeignKey(Genes, related_name='gene_body', on_delete=models.CASCADE)

    def __str__(self):
        return self.marker #'%s %s' % (self.marker,self.allele)