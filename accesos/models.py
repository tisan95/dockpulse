from django.db import models
from django.utils import timezone


# ── MAESTROS ─────────────────────────────────────────────────────────────────

class Hub(models.Model):
    """Centro logístico de origen (MAS1, MAS2, ITA1…)"""
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    entidad = models.CharField(max_length=150, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    poblacion = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=50, default='ESPAÑA')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Hub'


class Agencia(models.Model):
    """Agencia / transportista"""
    nick = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    cif = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    contacto = models.CharField(max_length=100, blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nick

    class Meta:
        ordering = ['nick']
        verbose_name = 'Agencia'


class Cliente(models.Model):
    """Cliente destinatario de una expedición"""
    TIPO_CHOICES = [
        ('TRD', 'Gran cuenta (TRD)'),
        ('BLK', 'Distribuidores (BLK)'),
        ('BDP', 'Paquetería (BDP)'),
        ('EXW', 'Exportación (EXW)'),
    ]
    nombre = models.CharField(max_length=200)
    sucursal = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES, default='BLK')
    direccion = models.CharField(max_length=200, blank=True)
    cp = models.CharField(max_length=10, blank=True)
    poblacion = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=50, default='ESPAÑA')
    necesita_plataforma = models.BooleanField(default=False)
    accede_trailer = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return self.sucursal or self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'


class Chofer(models.Model):
    """Base de datos de choferes"""
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    matricula_habitual = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.dni})"

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Chofer'


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
        return 'LIBRE' if v is None else v.estado

    def __str__(self):
        return f"Muelle {self.numero} ({self.get_tipo_display()})"

    class Meta:
        ordering = ['numero']
        verbose_name = 'Muelle'


# ── EXPEDICIÓN (cita previa) ──────────────────────────────────────────────────

class Expedicion(models.Model):
    """
    Expedición registrada con antelación en el sistema.
    Representa una cita: sabemos qué camión viene, cuándo y a qué muelle.
    """
    TIPO_CHOICES = [
        ('TRD', 'TRD — Gran cuenta nacional'),
        ('BLK', 'BLK — Distribuidores / Bulk'),
        ('BDP', 'BDP — Paquetería pequeña'),
        ('EXW', 'EXW — Exportación internacional'),
        ('ENT', 'ENT — Entrada / Recepción'),
    ]
    ESTADO_CHOICES = [
        ('PENDIENTE',   'Pendiente'),
        ('GESTIONADO',  'Gestionado'),
        ('LANZADO',     'Lanzado'),
        ('PREPARADO',   'Preparado — listo para cargar'),
        ('MUELLE',      'En muelle'),
        ('ENVIADA',     'Enviada'),
        ('ANULADA',     'Anulada'),
    ]

    numero     = models.CharField(max_length=20, unique=True)
    tipo       = models.CharField(max_length=5, choices=TIPO_CHOICES)
    hub_origen = models.ForeignKey(Hub, on_delete=models.PROTECT,
                                   related_name='expediciones', null=True, blank=True)

    # Cita
    fecha_cita = models.DateField(null=True, blank=True)
    hora_cita  = models.TimeField(null=True, blank=True)

    # Logística
    cliente          = models.ForeignKey(Cliente, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='expediciones')
    cliente_nombre   = models.CharField(max_length=200, blank=True)  # fallback si no está en BD
    destino          = models.CharField(max_length=200, blank=True)
    agencia          = models.ForeignKey(Agencia, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='expediciones')
    agencia_nombre   = models.CharField(max_length=100, blank=True)  # fallback
    muelle           = models.ForeignKey(Muelle, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='expediciones')
    palets_previstos = models.PositiveIntegerField(null=True, blank=True)

    # Referencias sistema
    sga              = models.CharField(max_length=100, blank=True, verbose_name='Nº pedido SGA')
    albaran          = models.CharField(max_length=100, blank=True)
    observaciones    = models.TextField(blank=True)

    estado    = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='PENDIENTE')
    creada_en = models.DateTimeField(auto_now_add=True)

    @property
    def cliente_display(self):
        if self.cliente:
            return str(self.cliente)
        return self.cliente_nombre or '—'

    @property
    def agencia_display(self):
        if self.agencia:
            return str(self.agencia)
        return self.agencia_nombre or '—'

    @property
    def tiene_visita_activa(self):
        return self.visitas.filter(salida__isnull=True).exists()

    def __str__(self):
        return f"{self.numero} | {self.cliente_display} | {self.get_estado_display()}"

    class Meta:
        ordering = ['fecha_cita', 'hora_cita']
        verbose_name = 'Expedición'
        verbose_name_plural = 'Expediciones'


# ── VISITA (presencia física en muelle) ───────────────────────────────────────

class Visit(models.Model):
    """
    Registro de la presencia física del camión en planta.
    Puede estar vinculada a una Expedicion preregistrada (lo normal)
    o ser un walk-in sin cita previa.
    """
    ESTADO_CHOICES = [
        ('ESPERANDO', 'Esperando'),
        ('OPERANDO',  'Operando'),
        ('LISTO',     'Listo para salir'),
        ('SALIDO',    'Salido'),
    ]

    expedicion = models.ForeignKey(Expedicion, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='visitas')
    muelle     = models.ForeignKey(Muelle, on_delete=models.PROTECT,
                                   related_name='visitas', null=True, blank=True)
    estado     = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ESPERANDO')

    # Datos del conductor (se autocompletan desde BD_CHOFER si existe)
    chofer              = models.ForeignKey(Chofer, on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='visitas')
    dni_chofer          = models.CharField(max_length=20)
    nombre_chofer       = models.CharField(max_length=150)
    matricula_tractora  = models.CharField(max_length=20)
    matricula_remolque  = models.CharField(max_length=20, blank=True)

    # Timestamps
    entrada = models.DateTimeField(auto_now_add=True)
    salida  = models.DateTimeField(null=True, blank=True)

    # Check-out
    palets_reales    = models.PositiveIntegerField(null=True, blank=True)
    documentacion_ok = models.BooleanField(null=True, blank=True)
    precinto         = models.CharField(max_length=100, blank=True)
    observaciones    = models.TextField(blank=True)

    @property
    def tipo(self):
        if self.expedicion:
            return self.expedicion.tipo
        return 'ENT'

    @property
    def agencia_display(self):
        if self.expedicion:
            return self.expedicion.agencia_display
        return '—'

    @property
    def cliente_display(self):
        if self.expedicion:
            return self.expedicion.cliente_display
        return '—'

    @property
    def tiempo_en_planta(self):
        fin = self.salida or timezone.now()
        delta = fin - self.entrada
        h, r = divmod(int(delta.total_seconds()), 3600)
        return f"{h}h {r // 60}min"

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
        exp = self.expedicion.numero if self.expedicion else 'sin cita'
        return f"[{exp}] {self.matricula_tractora} — M{self.muelle.numero if self.muelle else '?'}"

    class Meta:
        ordering = ['-entrada']
        verbose_name = 'Visita'


class Incidencia(models.Model):
    CAUSANTE_CHOICES = [
        ('ADMINISTRACION', 'Administración'),
        ('AGENCIA',        'Agencia transportista'),
        ('ALMACEN',        'Almacén'),
        ('CLIENTE',        'Cliente'),
        ('CHOFER',         'Chofer'),
    ]
    TIPO_CHOICES = [
        ('BOOKING_INCORRECTO',  'Booking incorrecto'),
        ('DIRECCION_INCORRECTA','Dirección incorrecta'),
        ('ALBARAN_INCORRECTO',  'Albarán incorrecto'),
        ('DIFERENCIA_PALETS',   'Diferencia de palets'),
        ('AVERIA',              'Avería del vehículo'),
        ('PARALIZACIÓN',        'Paralización'),
        ('ESPERA_EXCESIVA',     'Espera excesiva'),
        ('OTRO',                'Otro'),
    ]
    COSTE_CHOICES = [
        ('ENVIO',        'Envío'),
        ('DEVOLUCION',   'Devolución'),
        ('PARALIZACION', 'Paralización'),
        ('MANIPULACION', 'Manipulación'),
        ('SIN_COSTE',    'Sin coste extra'),
    ]

    visita      = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='incidencias')
    causante    = models.CharField(max_length=15, choices=CAUSANTE_CHOICES, default='AGENCIA')
    tipo        = models.CharField(max_length=25, choices=TIPO_CHOICES)
    concepto_coste = models.CharField(max_length=15, choices=COSTE_CHOICES, default='SIN_COSTE')
    descripcion = models.TextField()
    urgente     = models.BooleanField(default=False)
    creada_en   = models.DateTimeField(auto_now_add=True)
    resuelta    = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.get_tipo_display()}] Visita #{self.visita_id}"

    class Meta:
        ordering = ['-urgente', '-creada_en']
        verbose_name = 'Incidencia'
