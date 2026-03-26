from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Count
from .models import Visit
from .forms import CheckInForm, CheckOutForm


# ─────────────────────────────────────────
# VISTA 1: CHECK-IN
# Formulario que rellena control de accesos
# cuando llega un camión a planta
# ─────────────────────────────────────────
def checkin(request):
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            # Guardamos el registro en la base de datos
            # La hora de entrada se asigna automáticamente (auto_now_add=True)
            form.save()
            # Redirigimos a la pantalla de almacén para ver el camión aparecido
            return redirect('pantalla')
    else:
        # GET: mostramos el formulario vacío
        form = CheckInForm()

    return render(request, 'accesos/checkin.html', {'form': form})


# ─────────────────────────────────────────
# VISTA 2: CHECK-OUT
# Dos pasos:
#   1. Buscar el vehículo por matrícula tractora
#   2. Confirmar salida con documentación y precinto
# ─────────────────────────────────────────
def checkout(request):
    visit = None      # el registro que encontremos
    error = None      # mensaje de error si no se encuentra

    if request.method == 'POST':

        # PASO 1: el usuario busca por matrícula
        if 'buscar' in request.POST:
            matricula = request.POST.get('matricula_tractora', '').strip()
            # Buscamos una visita activa (sin salida) con esa matrícula
            visit = Visit.objects.filter(
                matricula_tractora__iexact=matricula,
                salida__isnull=True  # solo vehículos que aún no han salido
            ).first()

            if not visit:
                error = f"No se encontró ningún vehículo activo con matrícula '{matricula}'"

        # PASO 2: el usuario confirma la salida
        elif 'confirmar' in request.POST:
            visit_id = request.POST.get('visit_id')
            visit = get_object_or_404(Visit, id=visit_id)

            # Rellenamos los campos de salida
            visit.documentacion_ok = 'documentacion_ok' in request.POST
            visit.precinto = request.POST.get('precinto', '')
            visit.salida = timezone.now()  # hora exacta de salida
            visit.save()

            return redirect('pantalla')

    return render(request, 'accesos/checkout.html', {
        'visit': visit,
        'error': error,
    })


# ─────────────────────────────────────────
# VISTA 3: PANTALLA DE ALMACÉN
# Vista para poner en una TV en planta
# Solo muestra vehículos activos (sin salida)
# Se recarga cada 30 segundos automáticamente
# ─────────────────────────────────────────
def pantalla(request):
    # Filtramos solo los que están en planta ahora mismo
    visitas_activas = Visit.objects.filter(
        salida__isnull=True
    ).order_by('entrada')  # ordenadas por hora de llegada, primero el más antiguo

    return render(request, 'accesos/pantalla.html', {
        'visitas': visitas_activas,
        'ahora': timezone.now(),  # para mostrar la hora actual en pantalla
    })


# ─────────────────────────────────────────
# VISTA 4: DASHBOARD DE MÉTRICAS
# Panel para operaciones y analítica:
#   - Vehículos en planta ahora
#   - Tiempo medio por agencia
#   - Visitas por día de la semana
#   - Incidencias de documentación
# ─────────────────────────────────────────
def dashboard(request):
    # --- OPERACIONAL ---
    # Vehículos actualmente en planta
    en_planta = Visit.objects.filter(salida__isnull=True).count()

    # Lista de visitas activas con su tiempo en planta
    visitas_activas = Visit.objects.filter(salida__isnull=True).order_by('entrada')

    # --- ANALÍTICO ---
    # Visitas completadas (con salida registrada)
    visitas_completadas = Visit.objects.filter(salida__isnull=False)

    # Total de visitas registradas
    total_visitas = Visit.objects.count()

    # Agencias que han pasado más veces
    agencias = (
        Visit.objects.values('agencia')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]  # top 5 agencias
    )

    # Incidencias: salidas con documentación incorrecta
    incidencias = visitas_completadas.filter(documentacion_ok=False).count()

    return render(request, 'accesos/dashboard.html', {
        'en_planta':         en_planta,
        'visitas_activas':   visitas_activas,
        'total_visitas':     total_visitas,
        'agencias':          agencias,
        'incidencias':       incidencias,
    })