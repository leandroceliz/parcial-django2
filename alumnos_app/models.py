from django.db import models
from django.contrib.auth.models import User # Importamos el modelo de Usuario de Django

class Alumno(models.Model):
    # 1. Relacion con el usuario (quien creo este registro)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    # 2. Campos requeridos (al menos 3 campos)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    legajo = models.CharField(max_length=20, unique=True) # ID unico del alumno

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.legajo})"

    class Meta:
        verbose_name_plural = "Alumnos"