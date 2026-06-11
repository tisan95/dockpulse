from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count
from .models import Visit, Muelle, Incidencia
from .forms import CheckInEntradaForm, CheckInSalidaForm, CheckOutForm, IncidenciaForm


def checkin(request):
    tipo = request.GET.get('tipo', '')

    if request.method == 'POST':
        tipo = request.POST.get('tipo', '')
        FormClass = CheckInEntradaForm if tipo == 'ENTRADA' else CheckInSalidaForm
        form = FormClass(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.tipo   = tipo
            visita.estado = 'ESPERANDO'
            visita.save()
            return redirect('pantalla')
    else:
        if tipo == 'ENTRADA':
            form = CheckInEntradaForm()
        elif tipo == 'SALIDA':
            form = CheckInSalidaForm()
        else:
            form = None

    return render(request, 'accesos/checkin.html', {
        'form': form,
        'tipo': tipo,
    })


def checkout(request):
    visit = None
    error = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            matricula = request.POST.get('matricula_tractora', '').strip()
            visit = Visit.objects.filter(
                matricula_tractora__iexact=matricula,
                salida__isnull=True,
            ).first()
            if not visit:
                error = f"No se encontró ningún vehículo activo con matrícula '{matricula}'"

        elif 'confirmar' in request.POST:
            visit = get_object_or_404(Visit, id=request.POST.get('visit_id'))
            visit.documentacion_ok = 'documentacion_ok' in request.POST
            visit.precinto         = request.POST.get('precinto', '')
            visit.salida           = timezone.now()
            visit.estado           = 'SALIDO'
            if visit.tipo == 'ENTRADA' and request.POST.get('bultos_reales'):
                visit.bultos_reales = int(request.POST.get('bultos_reales'))
            if visit.muelle:
                visit.muelle = visit.muelle
            visit.save()
            return redirect('pantalla')

    return render(request, 'accesos/checkout.html', {'visit': visit, 'error': error})


def cambiar_estado(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Visit.ESTADO_CHOICES):
        visit.estado = nuevo_estado
        visit.save()
    return redirect('pantalla')


def incidencia_crear(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            inc = form.save(commit=False)
            inc.visita = visit
            inc.save()
            return redirect('pantalla')
    else:
        form = IncidenciaForm()
    return render(request, 'accesos/incidencia_form.html', {'form': form, 'visit': visit})


def pantalla(request):
    visitas_activas = Visit.objects.filter(salida__isnull=True).select_related('muelle').order_by('entrada')
    muelles = Muelle.objects.filter(activo=True).prefetch_related('visitas')
    return render(request, 'accesos/pantalla.html', {
        'visitas': visitas_activas,
        'muelles': muelles,
        'ahora':   timezone.now(),
    })


def dashboard(request):
    en_planta        = Visit.objects.filter(salida__isnull=True).count()
    visitas_activas  = Visit.objects.filter(salida__isnull=True).select_related('muelle').order_by('entrada')
    total_visitas    = Visit.objects.count()
    visitas_completadas = Visit.objects.filter(salida__isnull=False)
    incidencias_total   = Incidencia.objects.filter(resuelta=False).count()
    incidencias_urgentes = Incidencia.objects.filter(resuelta=False, urgente=True).count()
    doc_ko = visitas_completadas.filter(documentacion_ok=False).count()

    agencias = (
        Visit.objects.values('agencia')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    entradas_hoy = Visit.objects.filter(
        tipo='ENTRADA',
        entrada__date=timezone.now().date(),
    ).count()
    salidas_hoy = Visit.objects.filter(
        tipo='SALIDA',
        entrada__date=timezone.now().date(),
    ).count()

    return render(request, 'accesos/dashboard.html', {
        'en_planta':            en_planta,
        'visitas_activas':      visitas_activas,
        'total_visitas':        total_visitas,
        'agencias':             agencias,
        'incidencias_total':    incidencias_total,
        'incidencias_urgentes': incidencias_urgentes,
        'doc_ko':               doc_ko,
        'entradas_hoy':         entradas_hoy,
        'salidas_hoy':          salidas_hoy,
    })
