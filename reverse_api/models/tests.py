from django.db import models
from django.utils import timezone


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    user_code = models.TextField(max_length=100, db_index=True)
    test_code = models.TextField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    #result_file = models.FileField(upload_to='reverse_engineering_results/', null=True, blank=True)
    #result_file = models.FileField(upload_to=lambda instance, filename: f'temp_results/{filename}')
    result_file = models.BinaryField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_code', 'test_code']),
        ]

    def __str__(self):
        return f"Test {self.test_code} by User {self.user_code}"

