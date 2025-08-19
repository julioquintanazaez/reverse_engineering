
from reverse_api.utils.formulaprocessor import FormulaProcessor


# Create an instance of the class

handleF = FormulaProcessor()

formula = ["G/G", "C/C", "0", "WT", "a/A", "a/a", "G/g"]

assert(handleF.filter_lowercase(formula))

