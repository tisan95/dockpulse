from django.db import models
from django.utils import timezone

class Visit(models.Model):
    # CHECK-IN
    cita_carga         = models.CharField(max_length=100)
    dni_chofer         = models.CharField(max_length=20)
    nombre_chofer      = models.CharField(max_length=150)
    matricula_tractora = models.CharField(max_length=20)
    matricula_remolque = models.CharField(max_length=20, blank=True)
    agencia            = models.CharField(max_length=150)
    muelle             = models.CharField(max_length=20)
    entrada            = models.DateTimeField(auto_now_add=True)

    # CHECK-OUT
    documentacion_ok   = models.BooleanField(null=True, blank=True)
    precinto           = models.CharField(max_length=100, blank=True)
    salida             = models.DateTimeField(null=True, blank=True)

    @property
    def tiempo_en_planta(self):
        fin = self.salida or timezone.now()
        delta = fin - self.entrada
        horas, resto = divmod(int(delta.total_seconds()), 3600)
        minutos = resto // 60
        return f"{horas}h {minutos}min"

    def __str__(self):
        return f"{self.agencia} — {self.matricula_tractora} — Muelle {self.muelle}"