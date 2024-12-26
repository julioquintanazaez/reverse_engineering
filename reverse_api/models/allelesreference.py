from django.db import models

from .genes import Genes

# Create your models here.

class Alleles_Reference(models.Model):
    dbsnp = models.TextField(max_length=25,  blank=True, null=True)
    allele_ref = models.TextField(max_length=25, blank=False)
    gene = models.ForeignKey(Genes, related_name='gene_ref', on_delete=models.CASCADE)

    def __str__(self):
        return self.dbsnp #'%s %s' % (self.allele_ref, self.dbsnp)