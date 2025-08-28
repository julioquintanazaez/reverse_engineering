import json
from collections import defaultdict

def combine_patient_genotype_data(patient_data_list, patient_info_list=None):
    """
    Combina datos genéticos de múltiples pacientes en un formato tabular.
    
    Args:
        patient_data_list: Lista de diccionarios con datos genéticos por paciente
        patient_info_list: Lista opcional con información demográfica de cada paciente
        
    Returns:
        Diccionario con datos combinados en formato tabular
    """
    # Estructura para almacenar los datos combinados
    combined_data = defaultdict(dict)
    
    # Encabezados fijos
    headers = [
        "Accession number", "First name", "Last name", "Middle initial",
        "Ordering physician", "DOB", "SSN", "Gender", "Ethnicity",
        "Collection date", "Received date", "Report generated",
        "Specimen type", "Report format type", "Current medications",
        "MEDICATIONS THAT HAVE BEEN PROBLEMATIC", "MEDICATION ALLERGIES",
        "BRIEF MEDICAL HISTORY", "Renal function", "Smoker",
        "Daily or nearly daily alcohol intake", "Language"
    ]
    
    # Inicializar datos combinados con encabezados
    for header in headers:
        combined_data[header] = {}
    
    # Agregar información de pacientes si está disponible
    if patient_info_list:
        for i, info in enumerate(patient_info_list, 1):
            pat_key = f"Pat{i}"
            for header in headers:
                combined_data[header][pat_key] = info.get(header, "")
    else:
        # Si no hay info de pacientes, crear columnas vacías
        num_patients = len(patient_data_list)
        for i in range(1, num_patients + 1):
            pat_key = f"Pat{i}"
            for header in headers:
                combined_data[header][pat_key] = ""
    
    # Procesar datos genéticos de cada paciente
    markers_data = defaultdict(dict)
    print(len(patient_data_list))
    for i, patient_data in enumerate(patient_data_list, 1):
        pat_key = f"Pat{i}"
        #print(f"Procesando datos de Pat{i}")
        # Extraer datos de marcadores genéticos
        if 'response' in patient_data:
            for gene_data in patient_data['response']:
                for gene, markers in gene_data.items():
                    for marker in markers:
                        rs_id = marker.get('marker', '')
                        if rs_id and rs_id != 'None':
                            try:
                                # Simplificar el genotipo (aquí puedes personalizar según necesidades)
                                formula = limpiar_vector(marker.get('formula', ['']))[0]
                                genotype = formula if formula else 'Unknown'
                                markers_data[rs_id][pat_key] = genotype
                            except Exception as e:
                                # This is for NoneType objects
                                print(f"{'error:Combining data fail marker--------------------'}: {str(e)}")
    
    # Agregar marcadores genéticos a los datos combinados
    for rs_id, genotypes in markers_data.items():
        combined_data[rs_id] = genotypes
    
    return combined_data

def limpiar_vector(vector_sucio):
    # Filtrar elementos que no sean '*' ni cadena vacía
    vector_limpio = [elem for elem in vector_sucio if elem != '*' and elem != '']
    return vector_limpio