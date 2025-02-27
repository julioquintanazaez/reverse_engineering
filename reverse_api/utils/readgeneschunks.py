
import openpyxl 

from ..models.genes import Genes
from ..models.alleles import Alleles
from ..models.allelesreference import Alleles_Reference
from .handle_combinations import Handle_Alleles_Combinations

from ..excel_features.features import load_gene_features, load_alleles_features


class ExcelFileParseUtils(): 
    
    def __inint__(self):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """        
        

    def set_up_gene_columns_indexes(self, row):
        columns_index = {}
        for i, i_row in enumerate(row):
            #print(f"Column {i_row} : {i}")
            if "Protein change" == i_row:
                columns_index["Protein change"] = i
            elif "Nucleotide change" == i_row:
                columns_index["Nucleotide change"] = i
            elif "Marker" == i_row:
                columns_index["Marker"] = i
            elif "Genotype" == i_row:
                columns_index["Genotype"] = i
            elif "Allele" == i_row:
                columns_index["Allele"] = i
            elif "Formula" == i_row:
                columns_index["Formula"] = i                
            else:
                pass
        #print(columns_index)
        return columns_index
    
    def set_up_gene_reference_columns_indexes(self, row):
        columns_index = {}
        for i, i_row in enumerate(row):
            #print(f"Column {i_row} : {i}")
            if "Reference" == i_row:
                columns_index["Reference"] = i
            elif "Allele" == i_row:
                columns_index["Allele"] = i
            elif "dbSNP" == i_row:
                columns_index["dbSNP"] = i                
            else:
                pass
        #print(columns_index)
        return columns_index
           
    def readDataFile(self, file):
        hac = Handle_Alleles_Combinations() # Handle Alleles Combinations
        #print(f' The file name is: {file}')      
        wb = openpyxl.load_workbook(file)
        #print(wb.sheetnames) 
        # sheet = wb.active  
        snps_wsh = wb['SNPs']  
        allelescomp_wsh = wb['AlleleComp']     
        # Read Genes and Alleles      
        self.read_Genes_And_Alleles(snps_wsh)    
        print("Read Genes and Alleles done......")            
        # Read References
        self.read_Genes_References(allelescomp_wsh)
        print("Read Genes References done......")     
        # Get alleles combinations
        hac.fill_Alleles_Combinations()
        print("Read Alleles combinations done......")     
        
    # Esta función lee de la sheet Genes en la cual *1 no está para casí nungún gen 
    def read_Genes_And_Alleles(self, sheet):
        genbody = 0
        gene_columns = []
        for row in sheet.iter_rows(min_row=1, values_only=True):
            if row[0] != None:
                if row[0].startswith("Gene"): #Linea que empieza con Gene
                    gene_columns = self.set_up_gene_columns_indexes(row) #Actualiza los indices de las columnas
                else: # Lineas que contiene informacion de genes
                    gene, created = Genes.objects.get_or_create(name=row[0]) #Creo un gen nuevo   
                    #if created:                                            
                        #print(f"El gen {row[0]} no existe")
                    #else:
                        #print(f"El gen {row[0]} existe!!!!")
                    genbody = genbody + 1  #Contador para incrementar el indice de cada snp 
                    #Adiciono los Alleles
                    _, _ = Alleles.objects.get_or_create(
                            protein_change = row[gene_columns["Protein change"]],
                            nucleotide_change = row[gene_columns["Nucleotide change"]],
                            allele = row[gene_columns["Allele"]],
                            marker = row[gene_columns["Marker"]],
                            genotype = row[gene_columns["Genotype"]],
                            formula = row[gene_columns["Formula"]],  # revisar formato de la formula para eliminar letras minúsculas
                            snp = genbody,
                            gene=gene
                        )  

    # Esta función lee de la sheet AlleleReference en la cual *1 si está para todos los genes   
    def read_Genes_References(self, sheet):
        gene_ref_columns = []
        for row in sheet.iter_rows(min_row=1, values_only=True):
            if row[0] != None:
                if row[0].startswith("Reference"): #Linea que empieza con Reference
                    gene_ref_columns = self.set_up_gene_reference_columns_indexes(row)
                else: # Lineas que contiene informacion de la referencias a los alleles de genes
                    gene, created = Genes.objects.get_or_create(name=row[0]) #Creo un gen nuevo   
                    #Adiciono las referencias a los Alleles
                    _, _ = Alleles_Reference.objects.get_or_create(
                            dbsnp = row[gene_ref_columns["dbSNP"]],
                            allele_ref = row[gene_ref_columns["Allele"]],
                            gene=gene
                        )  

    # Nuevo from META
    #         
    def readDataFileFromMETA(self, file):
        hac = Handle_Alleles_Combinations() # Handle Alleles Combinations
        #print(f' The file name is: {file}')      
        wb = openpyxl.load_workbook(file, data_only=True)
        #print(wb.sheetnames) 
        # sheet = wb.active  
        snps_wsh = wb['Genes']  
        print("Read Genes and Alleles..")
        self.read_Genes_And_Alleles_From_META(snps_wsh)
        print("Read Alleles references..")
        self.read_Alleles_Reference_From_META(snps_wsh)
        print("Read files done...")

    def cell_row_formula(self, row, input):
        index = (int)(input)
        temp = f"@{row[index]}|{row[index+1]}|{row[index+2]}|{row[index+3]}|{row[index+4]}"  
        return temp
    
    def set_up_formula(self, row, gene_desc):
        formula = self.cell_row_formula(row, gene_desc["Formula_0"])
        formula = formula + self.cell_row_formula(row, gene_desc["Formula_1"])
        formula = formula + self.cell_row_formula(row, gene_desc["Formula_2"])
        formula = formula + self.cell_row_formula(row, gene_desc["Formula_3"])  
        return formula
    
    def extended_cell_row_formula(self, row, begin, end):
        begin = (int)(begin)
        end = (int)(end)
        temp = f"@{row[begin]}"
        for i in range(begin+1, end+1):
            temp = f"{temp}|{row[i]}"
        return temp
    
    def get_begin_end(self, desc_being_end):
        begin = (int)(desc_being_end[0])
        end = (int)(desc_being_end[1])
        return begin, end
    
    def set_up_formula_extended(self, row, gene_desc):
        begin, end = self.get_begin_end(gene_desc["Formula_0"])
        formula = self.extended_cell_row_formula(row, begin, end)
        begin, end = self.get_begin_end(gene_desc["Formula_1"])
        formula = formula + self.extended_cell_row_formula(row, begin, end)
        begin, end = self.get_begin_end(gene_desc["Formula_2"])
        formula = formula + self.extended_cell_row_formula(row, begin, end)
        begin, end = self.get_begin_end(gene_desc["Formula_3"])
        formula = formula + self.extended_cell_row_formula(row, begin, end) 
        begin, end = self.get_begin_end(gene_desc["Formula_a"])
        formula = formula + self.extended_cell_row_formula(row, begin, end)  
        return formula
        
    def read_Genes_And_Alleles_From_META(self, sheet):
        for index, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            if row[0] != None:
                if row[0].startswith("Gene"):                     
                    gene_name, _ = self.extract_gene_body(index+1, sheet)

    def read_Alleles_Reference_From_META(self, sheet):
        for index, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            if row[0] != None and row[1] == None and row[2] == None and row[3] == None and row[4] == None:
                gene_name = row[0]
                #print(gene_name)
                self.extract_alleles_body(index+1, sheet, gene_name)
             
    def extract_gene_body(self, index, sheet):
        gene_desc = load_gene_features()
        genbody = 0
        gene_name = ""
        gene_protein = ""
        gene_chain = ""
        gene_marker = ""
        temp_name = ""
        temp_protein = ""
        temp_chain = ""
        temp_marker = ""
        for row in sheet.iter_rows(min_row=index, values_only=True):
            if row[gene_desc["Gene"]] == None and row[gene_desc["Allele"]] == None and row[gene_desc["Marker"]] == None:
                break    
            gene_name = row[gene_desc["Gene"]]  
            gene_protein = row[gene_desc["Protein change"]]  
            gene_chain = row[gene_desc["Genotype"]]  
            gene_marker = row[gene_desc["Marker"]]             
            if(row[gene_desc["Gene"]] != None and row[gene_desc["Marker"]] != None):
                #print("Copy to temp")
                temp_name = gene_name
                temp_protein = gene_protein
                temp_chain = gene_chain
                temp_marker = gene_marker
            else:
                #print("Update empty value")
                gene_name = temp_name
                gene_protein = temp_protein
                gene_chain = temp_chain  
                gene_marker = temp_marker

            allele = row[gene_desc["Allele"]]
            genotype = row[gene_desc["Genotype"]]
            print(f"Insertar datos con: {gene_name} {allele} {gene_marker} {gene_protein} {gene_chain} -------------")
            genbody = genbody + 1  
            gene, _ = Genes.objects.get_or_create(name=gene_name) 
            _, _ = Alleles.objects.get_or_create(
                    protein_change = gene_protein,
                    nucleotide_change = gene_chain,
                    allele = allele,
                    marker = gene_marker,
                    genotype = genotype,
                    formula = self.set_up_formula_extended(row, gene_desc),  
                    snp = genbody,
                    gene=gene
                )  
            #print(f"{gene_name} > {rs} > {gene_protein} > {gene_chain} > {al}")
        return gene_name, genbody

    def extract_alleles_body(self, index, sheet, gene_name):
        alleles_desc = load_alleles_features()
        for row in sheet.iter_rows(min_row=index, values_only=True):
            if row[0] == None:
                break
            gene, created = Genes.objects.get_or_create(name=gene_name) #Creo un gen nuevo   
            _, _ = Alleles_Reference.objects.get_or_create(
                    dbsnp = row[alleles_desc["dbSNP"]],
                    allele_ref = row[alleles_desc["allele"]],
                    gene=gene
                )  
            #a = alleles_desc["allele"]
            #s = alleles_desc["dbSNP"]
            #print(f"Gene name: {gene_name} con allele: {row[a]} y SNP: {row[s]}")
        

   


        
    
       