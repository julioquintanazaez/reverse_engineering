from rest_framework import serializers
from ..models.patiencestest import PatiencesTest


class PatiencesTestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatiencesTest
        fields = ['user_code', 'test_code', 'test_data']
        extra_kwargs = {
            'user_code': {'required': True},
            'test_code': {'required': True},
            'test_data': {'required': True}
        }

    def validate_test_data(self, value):
        """Validación básica para asegurar que es un JSON válido"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("test_data debe ser un objeto JSON válido")
        return value

class PatiencesTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatiencesTest
        fields = ['id', 'user_code', 'test_code', 'test_data', 'created_at']
        read_only_fields = ['id', 'created_at']
