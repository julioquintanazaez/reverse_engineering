import openpyxl 

from ..models.genes import Genes

class ExcelFileParseAllelesCombinationsUtils(): 

    def __inint__(self):
        pass

    
    def readAllelesCombinationsDataFromFile(self, file):
        wb = openpyxl.load_workbook(file)
        # The sheet containing the genes must be the first
        genes_wsh = wb['Genes']  
        return self.read_Genes_Alleles_References(genes_wsh)
        
        
    def read_Genes_Alleles_References(self, sheet):
        genes_list = []
        for col in sheet.iter_cols(values_only=True):
            gen_name = ""
            alleles_list = []
            for cel in col:
                if cel is None:
                    continue
                if "IF" in cel:
                    continue
                if Genes.objects.filter(name=cel).exists():
                    #print(f"Gene name: {cel}----------------------------") 
                    gen_name = cel
                else:
                    #print(f"Gene body: {cel}")  
                    alleles_list.append(cel)   

            dict_gen = {"gen": gen_name, "alleles_list": alleles_list}
            genes_list.append(dict_gen)

        result = {"gen_list": genes_list}        
        return result
        
            
