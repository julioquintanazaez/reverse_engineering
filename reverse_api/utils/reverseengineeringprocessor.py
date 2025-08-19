from collections import Counter
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from ..models.allelesreference import Alleles_Reference
from ..models.alleles import Alleles
from ..models.genes import Genes

from ..serializers.geneserializer import GenesSerializer
from ..serializers.allelesreferenceserializer import AllelesReferenceSerializer
from ..serializers.allelesserializer import AllelesSerializer

from .formulaprocessor import FormulaProcessor


class ReverseEngineeringProcessor:
    """
    Procesador para realizar ingeniería inversa de datos genéticos.
    Maneja el procesamiento de genes y alelos para análisis genético.
    """
    
    def __init__(self):
        self.formula_processor = FormulaProcessor()

    def process_patient_genes(self, genes_data):
        """
        Procesa los datos genéticos de un paciente.
        
        Args:
            genes_data (list): Lista de strings en formato "gen>alelo1/alelo2"
            
        Returns:
            dict: Resultados del procesamiento por gen en formato:
                {"response": [{"gen1": resultados}, {"gen2": resultados}, ...]}
        """
        results = []
        
        if not genes_data:
            return {"response": [], "error": "No genes data provided"}
            
        for gene_entry in genes_data:
            try:
                gene_name, alleles = self._parse_gene_entry(gene_entry)
                gene_data = self._get_gene_data(gene_name)
                
                if gene_data:
                    processing_result = self._process_alleles_pair(
                        gene_data['id'], 
                        alleles
                    )
                    results.append({gene_data['name']: processing_result})
                    
            except ValueError as e:
                print(f"Invalid gene entry format: {gene_entry}. Error: {str(e)}")
            except Exception as e:
                print(f"Error processing gene {gene_entry}: {str(e)}")
        
        return {"response": results}

    def _parse_gene_entry(self, gene_entry):
        """
        Parsea una entrada de gen en formato "gen>alelo1/alelo2".
        
        Args:
            gene_entry (str): Cadena con información del gen y alelos
            
        Returns:
            tuple: (nombre_gen, [alelo1, alelo2])
            
        Raises:
            ValueError: Si el formato no es válido
        """
        if not isinstance(gene_entry, str) or ">" not in gene_entry:
            raise ValueError("Invalid gene entry format")
            
        gene_info = gene_entry.split(">")
        if len(gene_info) != 2 or "/" not in gene_info[1]:
            raise ValueError("Invalid gene or alleles format")
            
        return gene_info[0], gene_info[1].split("/")

    def _get_gene_data(self, gene_name):
        """
        Obtiene datos serializados de un gen desde la base de datos.
        
        Args:
            gene_name (str): Nombre del gen a buscar
            
        Returns:
            dict or None: Diccionario con id y nombre del gen, o None si no se encuentra
        """
        gene = Genes.objects.filter(name=gene_name).first()
        if not gene:
            print(f"Gene {gene_name} not found in database")
            return None
            
        serializer = GenesSerializer(gene)
        return {
            "id": serializer.data["id"],
            "name": serializer.data["name"]
        }

    def _process_alleles_pair(self, gene_id, alleles_pair):
        """
        Procesa un par de alelos para un gen específico.
        
        Args:
            gene_id (int): ID del gen en la base de datos
            alleles_pair (list): Lista con dos alelos a procesar
            
        Returns:
            list: Resultados combinados de alelos contribuyentes y no contribuyentes
        """
        if len(alleles_pair) != 2:
            return []
            
        # Obtener datos de referencia para los alelos
        reference_data = self._get_alleles_reference_data(gene_id, alleles_pair)
        if not reference_data:
            return []
            
        rs_frequency = Counter(reference_data.split("+"))
        
        # Procesar ambos tipos de alelos
        contributing = self._process_contributing_alleles(rs_frequency, alleles_pair)
        non_contributing = self._process_non_contributing_alleles(gene_id, rs_frequency)
        
        return contributing + non_contributing

    def _get_alleles_reference_data(self, gene_id, alleles_pair):
        """
        Obtiene datos de referencia para un par de alelos desde la base de datos.
        
        Args:
            gene_id (int): ID del gen
            alleles_pair (list): Par de alelos a buscar
            
        Returns:
            str: Cadena concatenada de datos dbSNP separados por "+"
        """
        if not alleles_pair or len(alleles_pair) < 2:
            return ""
            
        queries = [
            Q(gene=gene_id, allele_ref=alleles_pair[0]),
            Q(gene=gene_id, allele_ref=alleles_pair[1])
        ]
        
        references = Alleles_Reference.objects.filter(queries[0] | queries[1])
        if not references.exists():
            return ""
            
        serializer = AllelesReferenceSerializer(references, many=True)
        return "+".join([item["dbsnp"] for item in serializer.data])

    def _process_contributing_alleles(self, rs_frequency, alleles_pair):
        """
        Procesa alelos que contribuyen al resultado genético.
        
        Args:
            rs_frequency (Counter): Frecuencias de los marcadores
            alleles_pair (list): Par de alelos analizados
            
        Returns:
            list: Lista de diccionarios con resultados por marcador
        """
        results = []
        
        for marker, frequency in rs_frequency.items():
            alleles = self._get_alleles_info(marker)
            if not alleles:
                results.append(self._create_marker_result(marker, None, None))
                continue
                
            if len(alleles) == 1:
                results.append(
                    self._create_simple_marker_result(marker, alleles[0], frequency)
                )
            else:
                results.extend(
                    self._process_ambiguous_markers(marker, alleles, alleles_pair, frequency)
                )
        
        return results
    
    def get_non_contributing_alleles(self, gene_id, allele_frequency):
        """
        Identifica alelos no contribuyentes para un gen específico.
        
        Args:
            gene_id (int): ID del gen en la base de datos
            allele_frequency (Counter): Frecuencias de alelos contribuyentes
            
        Returns:
            list: Marcadores de alelos no contribuyentes
        """
        if not gene_id or not allele_frequency:
            return []
            
        # Obtener todos los marcadores únicos para el gen
        all_markers = Alleles.objects.filter(
            gene=gene_id
        ).values_list('marker', flat=True).distinct()
        
        # Filtrar marcadores que no están en los contribuyentes
        contributing_markers = set(allele_frequency.keys())
        return list(set(all_markers) - contributing_markers)
    

    def _process_non_contributing_alleles(self, gene_id, rs_frequency):
        """
        Procesa alelos que no contribuyen al resultado genético.
        
        Args:
            gene_id (int): ID del gen
            rs_frequency (Counter): Frecuencias de los marcadores
            
        Returns:
            list: Lista de diccionarios con resultados por marcador no contribuyente
        """
        non_contributing_rs = self.get_non_contributing_alleles(gene_id, rs_frequency)
        if not non_contributing_rs:
            return []
            
        results = []
        
        for marker in non_contributing_rs:
            alleles_info = self._get_alleles_info(marker)
            for allele in alleles_info:
                results.append({
                    "marker": marker,
                    "formula": self.formula_processor.process_formula(allele["formula"], 0),
                    "freq": 0,
                })
        
        return results

    def _get_alleles_info(self, marker):
        """
        Obtiene información de alelos para un marcador específico.
        
        Args:
            marker (str): Marcador a buscar
            
        Returns:
            list: Lista de diccionarios con información de alelos
        """
        alleles = Alleles.objects.filter(marker=marker)
        if not alleles.exists():
            return []
            
        serializer = AllelesSerializer(alleles, many=True)
        return self._serialize_alleles_data(serializer.data)

    def _serialize_alleles_data(self, serialized_data):
        """
        Formatea datos serializados de alelos.
        
        Args:
            serialized_data (list): Datos de alelos serializados
            
        Returns:
            list: Lista de diccionarios con información estructurada
        """
        return [
            {
                "allele": item["allele"],
                "marker": item["marker"],
                "formula": item["formula"],
            }
            for item in serialized_data
        ]

    def _create_marker_result(self, marker, formula, frequency):
        """
        Crea un resultado básico para un marcador.
        
        Args:
            marker (str): Nombre del marcador
            formula (str): Fórmula asociada
            frequency (int): Frecuencia
            
        Returns:
            dict: Resultado estructurado
        """
        return {
            "marker": marker,
            "formula": formula,
            "freq": frequency
        }

    def _create_simple_marker_result(self, marker, allele_info, frequency):
        """
        Crea resultado para un marcador no ambiguo.
        
        Args:
            marker (str): Nombre del marcador
            allele_info (dict): Información del alelo
            frequency (int): Frecuencia
            
        Returns:
            dict: Resultado estructurado
        """
        return {
            "marker": marker,
            "formula": self.formula_processor.process_formula(
                allele_info["formula"], 
                frequency
            ),
            "freq": frequency
        }

    def _process_ambiguous_markers(self, marker, alleles_info, alleles_pair, frequency):
        """
        Procesa marcadores con ambigüedad en los alelos.
        
        Args:
            marker (str): Nombre del marcador
            alleles_info (list): Información de alelos
            alleles_pair (list): Par de alelos analizados
            frequency (int): Frecuencia
            
        Returns:
            list: Lista de resultados para marcadores ambiguos
        """
        ambiguous_alleles = self._get_ambiguous_alleles(alleles_info, alleles_pair)
        
        if not ambiguous_alleles:
            return [self._create_simple_marker_result(
                marker, 
                alleles_info[0], 
                frequency
            )]
            
        if len(ambiguous_alleles) == 1 and alleles_pair[0] != alleles_pair[1]:
            return [self._create_simple_marker_result(
                marker,
                ambiguous_alleles[0],
                frequency
            )]
            
        if alleles_pair[0] == alleles_pair[1]:
            return [self._create_simple_marker_result(
                marker,
                ambiguous_alleles[0],
                frequency
            )]
            
        return self._process_complex_ambiguity(
            marker,
            ambiguous_alleles,
            alleles_pair,
            frequency
        )

    def _get_ambiguous_alleles(self, alleles_info, alleles_pair):
        """
        Identifica alelos ambiguos relacionados con el par analizado.
        
        Args:
            alleles_info (list): Información de alelos
            alleles_pair (list): Par de alelos analizados
            
        Returns:
            list: Alelos ambiguos encontrados
        """
        return [
            {
                "allele": item["allele"],
                "formula": item["formula"],
            }
            for item in alleles_info
            if item["allele"] in alleles_pair
        ]

    def _process_complex_ambiguity(self, marker, ambiguous_alleles, alleles_pair, frequency):
        """
        Procesa casos complejos de ambigüedad en alelos.
        
        Args:
            marker (str): Nombre del marcador
            ambiguous_alleles (list): Alelos ambiguos
            alleles_pair (list): Par de alelos analizados
            frequency (int): Frecuencia
            
        Returns:
            list: Resultados para ambigüedad compleja
        """
        formulas = [
            allele["formula"]
            for allele in ambiguous_alleles
            if allele["allele"] in alleles_pair
        ]
        
        if len(formulas) < 2:
            return [self._create_simple_marker_result(
                marker,
                ambiguous_alleles[0],
                frequency
            )]
            
        if self.formula_processor.formulas_compatible(formulas[0], formulas[1]):
            return [{
                "marker": marker,
                "formula": self.formula_processor.combine_formulas(formulas[0], formulas[1]),
                "freq": "1a"
            }]
            
        return [self._create_simple_marker_result(
            marker,
            ambiguous_alleles[0],
            frequency
        )]
    
