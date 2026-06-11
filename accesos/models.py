from django.db import models
from django.utils import timezone


class Muelle(models.Model):
    TIPO_CHOICES = [
        ('RECEPCION',  'Recepción'),
        ('EXPEDICION', 'Expedición'),
        ('MIXTO',      'Mixto'),
    ]
    numero = models.CharField(max_length=10, unique=True)
    tipo   = models.CharField(max_length=10, choices=TIPO_CHOICES, default='MIXTO')
    activo = models.BooleanField(default=True)

    @property
    def visita_activa(self):
        return self.visitas.filter(salida__isnull=True).first()

    @property
    def estado(self):
        v = self.visita_activa
        if v is None:
            return 'LIBRE'
        return v.estado

    def __str__(self):
        return f"Muelle {self.numero} ({self.get_tipo_display()})"

    class Meta:
        ordering = ['numero']


class Visit(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada — Recepción'),
        ('SALIDA',  'Salida — Expedición'),
    ]
    ESTADO_CHOICES = [
        ('ESPERANDO', 'Esperando'),
        ('OPERANDO',  'Operando'),
        ('LISTO',     'Listo para salir'),
        ('SALIDO',    'Salido'),
    ]
    TIPO_SALIDA_CHOICES = [
        ('GRAN_CUENTA', 'Gran cuenta'),
        ('PAQUETERIA',  'Paquetería'),
    ]

    # ── COMÚN ──────────────────────────────────────────────
    tipo               = models.CharField(max_length=10, choices=TIPO_CHOICES, default='ENTRADA')
    estado             = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ESPERANDO')
    muelle             = models.ForeignKey(Muelle, on_delete=models.PROTECT,
                                           related_name='visitas', null=True, blank=True)
    dni_chofer         = models.CharField(max_length=20)
    nombre_chofer      = models.CharField(max_length=150)
    matricula_tractora = models.CharField(max_length=20)
    matricula_remolque = models.CharField(max_length=20, blank=True)
    agencia            = models.CharField(max_length=150)
    entrada            = models.DateTimeField(auto_now_add=True)

    # ── ENTRADA (contenedor del puerto) ────────────────────
    numero_contenedor  = models.CharField(max_length=50, blank=True)
    orden_compra       = models.CharField(max_length=100, blank=True)
    puerto_origen      = models.CharField(max_length=100, blank=True)
    bultos_declarados  = models.PositiveIntegerField(null=True, blank=True)
    bultos_reales      = models.PositiveIntegerField(null=True, blank=True)

    # ── SALIDA (expedición) ────────────────────────────────
    tipo_salida        = models.CharField(max_length=15, choices=TIPO_SALIDA_CHOICES, blank=True)
    cliente            = models.CharField(max_length=150, blank=True)
    agencia_mensajeria = models.CharField(max_length=100, blank=True)
    num_pedidos        = models.PositiveIntegerField(null=True, blank=True)

    # ── CHECK-OUT ──────────────────────────────────────────
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

    @property
    def tiempo_total_segundos(self):
        fin = self.salida or timezone.now()
        return int((fin - self.entrada).total_seconds())

    @property
    def alerta_tiempo(self):
        s = self.tiempo_total_segundos
        if s > 4 * 3600:
            return 'rojo'
        if s > 2 * 3600:
            return 'amarillo'
        return 'verde'

    def __str__(self):
        muelle_str = f"M{self.muelle.numero}" if self.muelle else "sin muelle"
        return f"[{self.tipo}] {self.agencia} — {self.matricula_tractora} — {muelle_str}"

    class Meta:
        ordering = ['-entrada']


class Incidencia(models.Model):
    TIPO_CHOICES = [
        ('DOCUMENTACION', 'Documentación incorrecta'),
        ('BULTOS',        'Diferencia de bultos'),
        ('AVERIA',        'Avería del vehículo'),
        ('CARGA',         'Problema con la carga'),
        ('ESPERA',        'Espera excesiva'),
        ('OTRO',          'Otro'),
    ]

    visita    = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='incidencias')
    tipo      = models.CharField(max_length=15, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    urgente   = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    resuelta  = models.BooleanField(default=False)

    def __str__(self):
        return f"[{'URGENTE' if self.urgente else self.get_tipo_display()}] Visita #{self.visita_id}"

    class Meta:
        ordering = ['-urgente', '-creada_en']
