
from reverse_api.utils.handle_formula import HandleFormulaUtils


# Create an instance of the class

handleF = HandleFormulaUtils()

formula = ["G/G", "C/C", "0", "WT", "a/A", "a/a", "G/g"]

assert(handleF.filter_lower_case_formula(formula))

