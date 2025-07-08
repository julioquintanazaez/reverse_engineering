from django.db import models
from django.utils import timezone


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    user_code = models.TextField(max_length=100, db_index=True)  # Índice para búsquedas frecuentes
    test_code = models.TextField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']  # Ordenar por fecha descendente por defecto
        indexes = [
            models.Index(fields=['user_code', 'test_code']),  # Índice compuesto
        ]

    def __str__(self):
        return f"Test {self.test_code} by User {self.user_code}"

