from rest_framework import serializers 

class ExcelSerializer(serializers.Serializer):
    file_uploaded = serializers.FileField()

    def validate_file(self, value):
        if not(value.endswith('xls') or value.endswith('xlsx')):
            raise serializers.ValidationError("Only alowed Excel files")
        
            #Validar en contenido del fichero, debe ser valores separados por coma
            # itero por las columnas y mando a comprobar que:
            # 1.- los genes existen genes (en los nombres de las columnas)
            # 2.- Que los pares de alleles existen 
        return value
    
class InputTestSerializer(serializers.Serializer):
    userid = serializers.CharField()
    testid = serializers.CharField()
    file_uploaded = serializers.FileField()

    def validate(self, attrs):
        file_uploaded = attrs.get('file_uploaded')
        ExcelSerializer().validate(file_uploaded)
        return super().validate(attrs)