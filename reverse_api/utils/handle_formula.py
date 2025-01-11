
import re

class HandleFormulaUtils(): 

    def __inint__(self):
        pass

    def only_genotype(self, text_cleaned):
        formula_list_cleaned = text_cleaned.split("SI")
        genotypes = []
        for item in formula_list_cleaned:
            step_genotype = item.split(";")
            temp_geno = ""
            for geno in step_genotype:
                if geno.startswith("F"):
                    #print(geno)
                    temp_geno = temp_geno + geno + "$"
            temp_geno = temp_geno[:-1]  # Remover el último caracter "$"
            if (temp_geno != ""):
                genotypes.append(temp_geno.replace("F8=", ""))
        return genotypes     

    def proccess_entry_formula(self, formula, frec):
        #Replace unneeded string characters
        text_formula = formula.replace("(", "").replace(")", "").replace("O", "").replace(";0;", "").replace("\'", "")
        #Clean the genotypes and generate a list of genotypes
        genotypes = self.only_genotype(text_formula)
        formula = genotypes[frec - 1]  # Restamos 1 debido a que el Counter no considera la aparición =0
        formula = re.sub(r'F\w*=', '', formula)
        formula = re.sub(r'"', '', formula)
        #Return the index of ocurrence of allele genotype
        formula = formula.split("$")
        return formula
    
    def filter_lower_case_formula(self, formula):  # Find a regular expression to remove from the formula the lowercase parts
        res = []
        const_char = "abcdefghijklmnñopqrstuvwxyz-"
        for item in formula:
            flagwords = [''.join(r) for r in item if r in const_char]  # Unir las partes capturadas
            if flagwords == []:
                res.append(item)
        
        return res