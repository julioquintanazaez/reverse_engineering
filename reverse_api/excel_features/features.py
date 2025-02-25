import json
#from ..core.config import settings

features = {
        "gene_columns": 
            {
                "Gene": 0,
                "Protein change": 1,
                "Nucleotide change": 2,
                "Allele": 3,
                "Marker": 4,
                "Genotype": 5,
                "Formula_0": [16, 21],
                "Formula_1": [22, 37],
                "Formula_2": [46, 52],
                "Formula_3": [53, 57],
                "Formula_a": [38, 45]
            },    
        "alleles_columns": 
            {
                "allele": 0,
                "dbSNP": 12
            }
    }

def load_gene_features():    
    return features["gene_columns"]

def load_alleles_features():    
    return features["alleles_columns"]
