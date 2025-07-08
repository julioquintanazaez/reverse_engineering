from django.db import models
from ..models.tests import Test

class Patient(models.Model):
    test = models.ForeignKey(Test, related_name='patients', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    data_json = models.JSONField()
    
    
    def __str__(self):
        return f"{self.code} (Test: {self.test.test_code})"

