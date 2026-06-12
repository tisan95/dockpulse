from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import Visit, Muelle, Incidencia, Expedicion, Chofer, Cliente, Agencia
from .forms import (BuscarExpedicionForm, ExpedicionForm,
                    CheckInForm, CheckOutForm, IncidenciaForm,
                    ClienteForm, AgenciaForm, ChoferForm)


# ── EXPEDICIONES ──────────────────────────────────────────────────────────────

def expediciones_lista(request):
    """Lista de expediciones del día con filtros."""
    qs = Expedicion.objects.select_related('cliente', 'agencia', 'muelle', 'hub_origen')

    # Filtros
    fecha = request.GET.get('fecha') or timezone.now().date().isoformat()
    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')

    if fecha:
        qs = qs.filter(fecha_cita=fecha)
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)

    return render(request, 'accesos/expediciones_lista.html', {
        'expediciones': qs,
        'fecha': fecha,
        'estado': estado,
        'tipo': tipo,
        'estados': Expedicion.ESTADO_CHOICES,
        'tipos': Expedicion.TIPO_CHOICES,
    })


def expedicion_crear(request):
    if request.method == 'POST':
        form = ExpedicionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expediciones_lista')
    else:
        form = ExpedicionForm()
    return render(request, 'accesos/expedicion_form.html', {'form': form, 'accion': 'Crear'})


def expedicion_editar(request, pk):
    exp = get_object_or_404(Expedicion, pk=pk)
    if request.method == 'POST':
        form = ExpedicionForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            return redirect('expediciones_lista')
    else:
        form = ExpedicionForm(instance=exp)
    return render(request, 'accesos/expedicion_form.html', {'form': form, 'accion': 'Editar', 'exp': exp})


def expedicion_estado(request, pk):
    """Cambiar estado de una expedición (POST)."""
    exp = get_object_or_404(Expedicion, pk=pk)
    nuevo = request.POST.get('estado')
    if nuevo in dict(Expedicion.ESTADO_CHOICES):
        exp.estado = nuevo
        exp.save()
    return redirect('expediciones_lista')


# ── CHECK-IN ──────────────────────────────────────────────────────────────────

def checkin(request):
    """
    Flujo de check-in en 2 pasos:
      1. Buscar expedición (por nº expedición o DNI chofer)
      2. Confirmar datos y crear Visit
    """
    buscar_form = BuscarExpedicionForm()
    checkin_form = None
    expedicion = None
    chofer = None
    error = None

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # ── PASO 1: Búsqueda ──
        if accion == 'buscar':
            busqueda = request.POST.get('busqueda', '').strip().upper()
            # Intentar por nº expedición
            expedicion = Expedicion.objects.filter(numero__iexact=busqueda).first()
            if not expedicion:
                # Intentar por DNI del chofer
                chofer = Chofer.objects.filter(dni__iexact=busqueda).first()
                if not chofer:
                    # Buscar expediciones que contengan esa cadena
                    expedicion = Expedicion.objects.filter(
                        numero__icontains=busqueda,
                        estado__in=['PENDIENTE', 'GESTIONADO', 'LANZADO', 'PREPARADO']
                    ).first()

            if not expedicion and not chofer:
                error = f"No se encontró expedición ni chofer con '{busqueda}'"
                buscar_form = BuscarExpedicionForm(initial={'busqueda': request.POST.get('busqueda')})
            else:
                # Pre-rellenar el form de check-in
                initial = {}
                if expedicion:
                    initial['muelle'] = expedicion.muelle_id
                if chofer:
                    initial['dni_chofer'] = chofer.dni
                    initial['nombre_chofer'] = chofer.nombre
                    initial['matricula_tractora'] = chofer.matricula_habitual
                elif expedicion and expedicion.estado in ['PENDIENTE', 'GESTIONADO', 'LANZADO', 'PREPARADO']:
                    pass  # sin datos de chofer previos
                checkin_form = CheckInForm(initial=initial)

        # ── PASO 2: Confirmar entrada ──
        elif accion == 'confirmar':
            exp_id = request.POST.get('expedicion_id')
            expedicion = Expedicion.objects.filter(id=exp_id).first() if exp_id else None
            checkin_form = CheckInForm(request.POST)

            if checkin_form.is_valid():
                visit = checkin_form.save(commit=False)
                visit.expedicion = expedicion
                visit.estado = 'ESPERANDO'

                # Buscar chofer en BD para linkear
                dni = checkin_form.cleaned_data.get('dni_chofer', '')
                ch = Chofer.objects.filter(dni__iexact=dni).first()
                if ch:
                    visit.chofer = ch

                visit.save()

                # Actualizar estado de la expedición
                if expedicion and expedicion.estado != 'MUELLE':
                    expedicion.estado = 'MUELLE'
                    if visit.muelle:
                        expedicion.muelle = visit.muelle
                    expedicion.save()

                return redirect('pantalla')

    return render(request, 'accesos/checkin.html', {
        'buscar_form': buscar_form,
        'checkin_form': checkin_form,
        'expedicion': expedicion,
        'chofer': chofer,
        'error': error,
    })


# ── CHECK-OUT ─────────────────────────────────────────────────────────────────

def checkout(request):
    visit = None
    error = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            matricula = request.POST.get('matricula_tractora', '').strip()
            visit = Visit.objects.filter(
                matricula_tractora__iexact=matricula,
                salida__isnull=True,
            ).select_related('expedicion', 'muelle').first()
            if not visit:
                error = f"No se encontró vehículo activo con matrícula '{matricula}'"

        elif 'confirmar' in request.POST:
            visit = get_object_or_404(Visit, id=request.POST.get('visit_id'))
            visit.documentacion_ok = 'documentacion_ok' in request.POST
            visit.precinto         = request.POST.get('precinto', '')
            visit.salida           = timezone.now()
            visit.estado           = 'SALIDO'
            if request.POST.get('palets_reales'):
                visit.palets_reales = int(request.POST.get('palets_reales'))
            visit.save()

            # Actualizar expedición
            if visit.expedicion:
                visit.expedicion.estado = 'ENVIADA'
                visit.expedicion.save()

            return redirect('pantalla')

    return render(request, 'accesos/checkout.html', {'visit': visit, 'error': error})


# ── ESTADOS ───────────────────────────────────────────────────────────────────

def cambiar_estado(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    nuevo = request.POST.get('estado')
    if nuevo in dict(Visit.ESTADO_CHOICES):
        visit.estado = nuevo
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


# ── API: búsqueda de chofer por DNI (para autocompletar en JS) ────────────────

def api_chofer(request):
    dni = request.GET.get('dni', '').strip()
    ch = Chofer.objects.filter(dni__iexact=dni).first()
    if ch:
        return JsonResponse({
            'found': True,
            'nombre': ch.nombre,
            'matricula': ch.matricula_habitual,
            'telefono': ch.telefono,
        })
    return JsonResponse({'found': False})


# ── PANTALLA ──────────────────────────────────────────────────────────────────

def pantalla(request):
    visitas_activas = (Visit.objects
                       .filter(salida__isnull=True)
                       .select_related('muelle', 'expedicion__cliente',
                                       'expedicion__agencia', 'expedicion__hub_origen')
                       .order_by('entrada'))
    muelles = Muelle.objects.filter(activo=True).prefetch_related('visitas')
    # Expediciones del día pendientes de llegar
    hoy = timezone.now().date()
    pendientes = (Expedicion.objects
                  .filter(fecha_cita=hoy, estado__in=['PENDIENTE','GESTIONADO','LANZADO','PREPARADO'])
                  .select_related('cliente', 'agencia', 'muelle')
                  .order_by('hora_cita'))
    return render(request, 'accesos/pantalla.html', {
        'visitas':    visitas_activas,
        'muelles':    muelles,
        'pendientes': pendientes,
        'ahora':      timezone.now(),
    })


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

def dashboard(request):
    hoy = timezone.now().date()
    en_planta       = Visit.objects.filter(salida__isnull=True).count()
    visitas_activas = (Visit.objects.filter(salida__isnull=True)
                       .select_related('muelle', 'expedicion__cliente').order_by('entrada'))
    total_visitas   = Visit.objects.count()

    incidencias_total    = Incidencia.objects.filter(resuelta=False).count()
    incidencias_urgentes = Incidencia.objects.filter(resuelta=False, urgente=True).count()
    doc_ko = Visit.objects.filter(salida__isnull=False, documentacion_ok=False).count()

    # Por tipo de expedición hoy
    exp_hoy = Expedicion.objects.filter(fecha_cita=hoy)
    trd_hoy = exp_hoy.filter(tipo='TRD').count()
    blk_hoy = exp_hoy.filter(tipo='BLK').count()
    bdp_hoy = exp_hoy.filter(tipo='BDP').count()
    exw_hoy = exp_hoy.filter(tipo='EXW').count()
    ent_hoy = exp_hoy.filter(tipo='ENT').count()

    top_agencias = (Expedicion.objects.values('agencia__nick', 'agencia_nombre')
                    .annotate(total=Count('id'))
                    .order_by('-total')[:5])

    return render(request, 'accesos/dashboard.html', {
        'en_planta':            en_planta,
        'visitas_activas':      visitas_activas,
        'total_visitas':        total_visitas,
        'incidencias_total':    incidencias_total,
        'incidencias_urgentes': incidencias_urgentes,
        'doc_ko':               doc_ko,
        'trd_hoy': trd_hoy, 'blk_hoy': blk_hoy,
        'bdp_hoy': bdp_hoy, 'exw_hoy': exw_hoy, 'ent_hoy': ent_hoy,
        'top_agencias':         top_agencias,
    })


# ── MAESTROS: CLIENTES ────────────────────────────────────────────────────────

def clientes_lista(request):
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    qs = Cliente.objects.all()
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(sucursal__icontains=q) | Q(poblacion__icontains=q))
    if tipo:
        qs = qs.filter(tipo=tipo)
    return render(request, 'accesos/maestros/clientes_lista.html', {
        'clientes': qs, 'q': q, 'tipo': tipo,
        'tipos': Cliente.TIPO_CHOICES,
    })


def cliente_crear(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('clientes_lista')
    return render(request, 'accesos/maestros/cliente_form.html', {'form': form, 'accion': 'Nuevo'})


def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        return redirect('clientes_lista')
    return render(request, 'accesos/maestros/cliente_form.html', {'form': form, 'accion': 'Editar', 'obj': cliente})


# ── MAESTROS: AGENCIAS ────────────────────────────────────────────────────────

def agencias_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Agencia.objects.all()
    if q:
        qs = qs.filter(Q(nick__icontains=q) | Q(nombre__icontains=q))
    return render(request, 'accesos/maestros/agencias_lista.html', {'agencias': qs, 'q': q})


def agencia_crear(request):
    form = AgenciaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('agencias_lista')
    return render(request, 'accesos/maestros/agencia_form.html', {'form': form, 'accion': 'Nueva'})


def agencia_editar(request, pk):
    agencia = get_object_or_404(Agencia, pk=pk)
    form = AgenciaForm(request.POST or None, instance=agencia)
    if form.is_valid():
        form.save()
        return redirect('agencias_lista')
    return render(request, 'accesos/maestros/agencia_form.html', {'form': form, 'accion': 'Editar', 'obj': agencia})


def agencia_toggle(request, pk):
    agencia = get_object_or_404(Agencia, pk=pk)
    agencia.activa = not agencia.activa
    agencia.save()
    return redirect('agencias_lista')


# ── MAESTROS: CHOFERES ────────────────────────────────────────────────────────

def choferes_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Chofer.objects.all()
    if q:
        qs = qs.filter(Q(dni__icontains=q) | Q(nombre__icontains=q) | Q(matricula_habitual__icontains=q))
    return render(request, 'accesos/maestros/choferes_lista.html', {'choferes': qs, 'q': q})


def chofer_crear(request):
    form = ChoferForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('choferes_lista')
    return render(request, 'accesos/maestros/chofer_form.html', {'form': form, 'accion': 'Nuevo'})


def chofer_editar(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    form = ChoferForm(request.POST or None, instance=chofer)
    if form.is_valid():
        form.save()
        return redirect('choferes_lista')
    return render(request, 'accesos/maestros/chofer_form.html', {'form': form, 'accion': 'Editar', 'obj': chofer})


def chofer_toggle(request, pk):
    chofer = get_object_or_404(Chofer, pk=pk)
    chofer.activo = not chofer.activo
    chofer.save()
    return redirect('choferes_lista')
