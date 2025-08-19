from openpyxl import load_workbook
from ..models.genes import Genes
from ..models.alleles import Alleles
from ..models.allelesreference import Alleles_Reference
from django.core.exceptions import ObjectDoesNotExist
from collections import defaultdict

class GeneDataImporter:
    def __init__(self):
        self.current_gene = None
        self.current_allele = None
        self.gene_created = False
        self.alleles_count = 0
        self.allele_refs_count = 0
        self.formula_groups = None
        self.snp_counter = 0  
        self.total_genes = 0
        self.total_alleles = 0
        self.total_allele_refs = 0

    def process_excel_file(self, file_path):
        # Cargar el archivo en modo solo datos (ignora fórmulas)
        wb = load_workbook(filename=file_path, data_only=True)
        ws = wb.active
        
        for row in ws.iter_rows(values_only=True):
            # Convertir None a cadena vacía para evitar errores
            processed_row = [cell if cell is not None else "" for cell in row]
            
            # Detectar sección Gene
            if self._is_gene_header_row(processed_row):
                self._handle_gene_section_start()
                self._detect_formula_columns(processed_row)
                continue
                
            # Detectar sección Allele
            if self._is_allele_header_row(processed_row):
                self._handle_allele_section_start(processed_row)
                continue
                
            # Procesar cuerpo Gene (Alleles)
            if hasattr(self, 'processing_gene') and self.processing_gene:
                if self._is_gene_data_row(processed_row):
                    self._process_gene_row(processed_row)
                else:
                    self._finalize_gene_section()
            
            # Procesar cuerpo Allele (Alleles_Reference)
            elif hasattr(self, 'processing_allele') and self.processing_allele:
                if any(cell != "" for cell in processed_row):
                    self._process_allele_row(processed_row)
    
    def _is_gene_header_row(self, row):
        return row and str(row[0]).startswith("Gene") and "Protein change" in str(row[1])

    def _is_allele_header_row(self, row):
        return "dbSNP" in [str(cell) for cell in row]

    def _is_gene_data_row(self, row):
        return len(row) > 3 and str(row[4]).strip()

    def _detect_formula_columns(self, row):
        """Detecta las columnas de fórmula basadas en los números de grupo"""
        self.formula_groups = defaultdict(list)
        
        for idx, cell in enumerate(row):
            cell_str = str(cell)
            if cell_str.strip().isdigit():
                group = int(cell_str)
                self.formula_groups[group].append(idx)
        
        # Valores por defecto si no se detectan grupos
        if not self.formula_groups:
            self.formula_groups = {
                0: list(range(16, 21)),
                1: list(range(21, 37)),
                2: list(range(46, 52)),
                3: list(range(53, 58)),
                4: list(range(38, 45)) #1a at the end
            }

    def _process_formula(self, row):
        """Procesa la fórmula según el formato requerido"""
        formula_parts = []
        
        for group in sorted(self.formula_groups.keys()):
            group_values = []
            
            for col_idx in self.formula_groups[group]:
                if col_idx < len(row):
                    cell_value = str(row[col_idx]).strip()
                    if cell_value:
                        group_values.append(f'"{cell_value}"')
                    else:
                        group_values.append(f'*')
            
            if group_values:
                formula_parts.append(f'@{"|".join(group_values)}')
        
        # Unir todas las partes y reemplazar comillas escapadas
        formula = ''.join(formula_parts)
        # Reemplazar \" por " simplemente
        return formula.replace('\"', '')

    def _handle_gene_section_start(self):
        self.processing_gene = True
        self.processing_allele = False
        self.current_gene = None
        self.gene_created = False
        self.alleles_count = 0

    def _handle_allele_section_start(self, row):
        self._finalize_gene_section()
        self.processing_gene = False
        self.processing_allele = True
        self.current_allele = str(row[0]) if row and row[0] else "Unknown_Allele"
        self.allele_refs_count = 0

    def _process_gene_row(self, row):
        if not self.current_gene:
            self.current_gene = str(row[0]) if row and row[0] else ""
            self._create_or_get_gene()
            self.snp_counter = 0  # Reiniciar contador para cada nuevo gen
        
        # Procesar fórmula
        formula = self._process_formula(row)
        
        # Crear registro en Alleles
        allele_data = {
            'protein_change': str(row[1]) if len(row) > 1 and row[1] is not None else '',
            'nucleotide_change': str(row[2]) if len(row) > 2 and row[2] is not None else '',
            'allele': str(row[3]) if len(row) > 3 and row[3] is not None else '',
            'marker': str(row[4]) if len(row) > 4 and row[4] is not None else '',
            'genotype': str(row[5]) if len(row) > 5 and row[5] is not None else '',
            'formula': formula,
            'snp': self.snp_counter,  
            'gene': self.current_gene_obj
        }
        
        Alleles.objects.update_or_create(
            marker=allele_data['marker'],
            gene=self.current_gene_obj,
            defaults=allele_data
        )
        self.alleles_count += 1
        self.snp_counter += 1  # Incrementar contador para el próximo alelo

    def _process_allele_row(self, row):
        if not self.current_gene_obj:
            return
            
        ref_data = {
            'allele_ref': str(row[0]) if len(row) > 0 else '',
            'dbsnp': str(row[12]) if len(row) > 1 else '',
            'gene': self.current_gene_obj
        }
        
        Alleles_Reference.objects.update_or_create(
            dbsnp=ref_data['dbsnp'],
            gene=self.current_gene_obj,
            defaults=ref_data
        )
        self.allele_refs_count += 1

    def _create_or_get_gene(self):
        try:
            self.current_gene_obj = Genes.objects.get(name=self.current_gene)
            self.gene_created = False
        except ObjectDoesNotExist:
            self.current_gene_obj = Genes.objects.create(name=self.current_gene)
            self.gene_created = True
            self.total_genes += 1  # Incrementar contador de genes nuevos

    def _finalize_gene_section(self):
        if hasattr(self, 'processing_gene'):
            self.processing_gene = False
            if self.current_gene:
                print(f"Procesadas {self.alleles_count} líneas Alleles para gen {self.current_gene}")
                self.total_alleles += self.alleles_count
                self.total_allele_refs += self.allele_refs_count
            self.alleles_count = 0
            self.allele_refs_count = 0
