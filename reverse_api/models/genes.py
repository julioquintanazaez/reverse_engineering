from django.db import models

# Create your models here.

class Genes(models.Model):
    name = models.TextField(max_length=25)

    def __str__(self):
        return self.name