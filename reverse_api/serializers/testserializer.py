from rest_framework import serializers
from ..models.tests import Test


class TestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['user_code', 'test_code']
        extra_kwargs = {
            'user_code': {'required': True},
            'test_code': {'required': True},
        }
    """
    def validate_test_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("test_data debe ser un objeto JSON válido")
        return value
    """

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'user_code', 'test_code', 'created_at']
        read_only_fields = ['id', 'created_at']
