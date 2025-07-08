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
                "Genotype": 5
            },         
        "alleles_columns": 
            {
                "allele": 0,
                "dbSNP": 12
            }
    }

"""
"formula_columns": 
            {
                "0": [16, 21],
                "1": [22, 37],
                "2": [46, 52],
                "3": [53, 57],
                "1a": [38, 45]
            }, 
"""


def load_gene_features():  
    return features["gene_columns"]


def load_alleles_features():    
    return features["alleles_columns"]


def load_formula_features(sheet):    
    return features["formula_columns"]


def get_formula_indexes_from_row(row_values):
    formula_columns = {
        "0": [0, 0],
        "1": [0, 0],  
        "2": [0, 0],
        "3": [0, 0],
        "1a": [0, 0]
    }
    # Proceso para actualizar los índices de inicio y fin
    for key in formula_columns:
        start_index = None
        end_index = None
        for i, value in enumerate(row_values):
            if str(value) == key:
                if start_index is None:
                    start_index = i
                end_index = i
        if start_index is not None:
            formula_columns[key] = [start_index, end_index]

    return formula_columns
