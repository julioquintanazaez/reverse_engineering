
import openpyxl 

from ..models.genes import Genes
from ..models.alleles import Alleles
from ..models.allelesreference import Alleles_Reference
from ..utils.hendle_combinations import Handle_Alleles_Combinations

class ExcelFileParseUtils(): 

    def __inint__(self):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """        
        self._GENE_COLUMN = "Gene"
        self._GENE_PROTEIN_CHAIN = "Protein change"
        self._GENE_NUCLEOTIDE_CHAIN = "Nucleotide change"
        self._GENE_ALLELE = "Allele"
        self._GENE_MARKER = "Marker"
        self._GENE_GENOTYPE = "Genotype"
        self._GENE_FORMULA = "Formula"

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
        
    def readGenesChuncks(self, file):
        #print(f' The file name is: {file}')      
        wb = openpyxl.load_workbook(file)
        sheet = wb.active        
        #print(wb.sheetnames)
        #Como seleccionar una Sheet specifica en openpyxl
        genes_list = []
        geneIn = False
        genbody = 0
        tempGene = None
        gene_columns = []
        for row in sheet.iter_rows(min_row=1, values_only=True):
            if row[0] != None:
                if row[0].startswith("Gene"):
                    geneIn = True
                    tempGene = None
                    gene_columns = self.set_up_gene_columns_indexes(row)
                elif geneIn:
                    if row[0] not in genes_list: 
                        if len(genes_list) > 0:
                            #print(f"Gene {genes_list[len(genes_list)-1]} contains: {genbody} SNPs") 
                            genbody = 0 #Restarting the count of the gene body
                        genes_list.append(row[0])  
                        genbody = genbody + 1
                        #print(f"New gene {row[0]}") 
                        gene, created = Genes.objects.get_or_create(name=row[0])   
                        _, _ = Alleles.objects.get_or_create(
                                protein_change= "",#row[gene_columns["Protein change"]],
                                nucleotide_change = "",#row[gene_columns["Nucleotide change"]],
                                allele = row[gene_columns["Allele"]],
                                marker = row[gene_columns["Marker"]],
                                genotype = row[gene_columns["Genotype"]],
                                formula = row[gene_columns["Formula"]],
                                snp = genbody,
                                gene=gene
                            )                     
                        tempGene = gene                                               
                    else:
                        genbody = genbody + 1
                        #print(f"Body of gene {row[0]}")  
                        _, _ = Alleles.objects.get_or_create(
                                protein_change = row[gene_columns["Protein change"]],
                                nucleotide_change = row[gene_columns["Nucleotide change"]],
                                allele = row[gene_columns["Allele"]],
                                marker = row[gene_columns["Marker"]],
                                genotype = row[gene_columns["Genotype"]],
                                formula = row[gene_columns["Formula"]],
                                snp = genbody,
                                gene=tempGene
                            )                         
                else:    
                    pass
            else:
                geneIn = False

        #print(genes_list)

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
                            formula = row[gene_columns["Formula"]],
                            snp = genbody,
                            gene=gene
                        )  
                    
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
                    
    
                          
                    

   


        
    
       