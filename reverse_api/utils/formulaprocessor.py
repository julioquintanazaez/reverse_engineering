import re

class FormulaProcessor:
    """
    Procesador de fórmulas genéticas para el análisis de alelos.
    Maneja extracción, limpieza y combinación de fórmulas.
    """
    
    def __init__(self):
        pass

    def extract_genotypes(self, cleaned_text):
        """
        Extrae genotipos de texto previamente limpiado.
        
        Args:
            cleaned_text (str): Texto limpio de caracteres especiales
            
        Returns:
            list: Lista de genotipos extraídos
        """
        if not cleaned_text:
            return []
            
        genotype_sections = cleaned_text.split("SI")
        genotypes = []
        
        for section in genotype_sections:
            if not section:
                continue
                
            steps = section.split(";")
            genotype_steps = [
                step.replace("F8=", "") 
                for step in steps 
                if step.startswith("F")
            ]
            
            if genotype_steps:
                genotype = "$".join(genotype_steps)
                genotypes.append(genotype)
        
        return genotypes

    def process_formula_entry(self, formula, frequency):
        """
        Procesa una entrada de fórmula para un nivel de frecuencia dado.
        
        Args:
            formula (str): Fórmula a procesar
            frequency (int): Nivel de frecuencia a extraer
            
        Returns:
            list: Componentes de la fórmula procesados
        """
        if not formula:
            return []
            
        # Limpieza básica del texto
        trans_table = str.maketrans("", "", "();O'\"")
        clean_text = formula.translate(trans_table).replace(";0;", "")
        
        genotypes = self.extract_genotypes(clean_text)
        if not genotypes:
            return []
            
        try:
            selected_genotype = genotypes[frequency - 1] if frequency > 0 else genotypes[0]
            return [part.split("=")[-1] for part in selected_genotype.split("$") if "=" in part]
        except IndexError:
            return []

    def process_formula(self, formula, frequency):
        """
        Procesa una fórmula completa para un nivel de frecuencia.
        
        Args:
            formula (str): Fórmula completa con secciones
            frequency (int): Nivel de frecuencia a procesar
            
        Returns:
            list: Componentes de la sección seleccionada, excluyendo valores None
        """
        if not formula:
            return []
            
        formula_parts = formula.split("@")
        if len(formula_parts) <= frequency + 1:
            return []
            
        selected_part = formula_parts[frequency + 1].split("|")
        return [x for x in selected_part if x != "None"]

    def formulas_compatible(self, formula1, formula2):
        """
        Determina si dos fórmulas son compatibles para combinación.
        
        Args:
            formula1 (str): Primera fórmula a comparar
            formula2 (str): Segunda fórmula a comparar
            
        Returns:
            bool: True si las fórmulas tienen estructura compatible
        """
        parts1 = formula1.split("@")[-1].split("|")
        parts2 = formula2.split("@")[-1].split("|")
        
        filtered1 = [p for p in parts1 if p != "None"]
        filtered2 = [p for p in parts2 if p != "None"]
        
        return len(filtered1) > 1 and len(filtered2) > 1

    def combine_formulas(self, formula1, formula2):
        """
        Combina dos fórmulas compatibles, manteniendo partes comunes.
        
        Args:
            formula1 (str): Primera fórmula a combinar
            formula2 (str): Segunda fórmula a combinar
            
        Returns:
            list: Partes comunes de ambas fórmulas, excluyendo None
        """
        parts1 = formula1.split("@")[-1].split("|")
        parts2 = formula2.split("@")[-1].split("|")
        
        common_parts = [
            p1 
            for p1, p2 in zip(parts1, parts2) 
            if p1 == p2 and p1 != "None"
        ]
        
        return common_parts

    def filter_lowercase(self, formula_parts):
        """
        Filtra partes de fórmula que contienen minúsculas.
        
        Args:
            formula_parts (list): Partes de fórmula a filtrar
            
        Returns:
            list: Partes sin elementos que contengan minúsculas
        """
        lowercase_chars = set("abcdefghijklmnñopqrstuvwxyz-")
        return [
            part 
            for part in formula_parts 
            if not any(c in lowercase_chars for c in part)
        ]