from rest_framework import serializers
from ..models.patients import Patient
from ..models.tests import Test


class PacienteSerializer(serializers.ModelSerializer):
    test_code = serializers.CharField(read_only=True) #source='test.test_code',
    
    class Meta:
        model = Patient
        fields = ['id', 'code', 'data_json', 'test', 'test_code']
        extra_kwargs = {
            'test': {'write_only': True}
        }

    def create(self, validated_data):
        test_code = validated_data.pop('test_code')
        try:
            test = Test.objects.get(test_code=test_code)
        except Test.DoesNotExist:
            raise serializers.ValidationError("A test with that code dosent'n exist")
        
        validated_data['test'] = test
        return super().create(validated_data)
    
class PatientCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['code']
