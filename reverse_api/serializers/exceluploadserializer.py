from rest_framework import serializers 

class ExcelUploadSerializer(serializers.Serializer):
    file_uploaded = serializers.FileField()

    def validate_file(self, value):
        if not(value.endswith('xls') or value.endswith('xlsx')):
            raise serializers.ValidationError("Only alowed Excel files")
        return value
