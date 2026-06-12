from django.urls import path
from . import views

urlpatterns = [
    # Pantalla y dashboard
    path('',                                  views.pantalla,            name='home'),
    path('pantalla/',                         views.pantalla,            name='pantalla'),
    path('dashboard/',                        views.dashboard,           name='dashboard'),

    # Expediciones (citas previas)
    path('expediciones/',                     views.expediciones_lista,  name='expediciones_lista'),
    path('expediciones/nueva/',               views.expedicion_crear,    name='expedicion_crear'),
    path('expediciones/<int:pk>/editar/',     views.expedicion_editar,   name='expedicion_editar'),
    path('expediciones/<int:pk>/estado/',     views.expedicion_estado,   name='expedicion_estado'),

    # Check-in / check-out
    path('checkin/',                          views.checkin,             name='checkin'),
    path('checkout/',                         views.checkout,            name='checkout'),

    # Acciones sobre visitas
    path('visita/<int:visit_id>/estado/',     views.cambiar_estado,      name='cambiar_estado'),
    path('visita/<int:visit_id>/incidencia/', views.incidencia_crear,    name='incidencia_crear'),

    # API interna
    path('api/chofer/',                       views.api_chofer,          name='api_chofer'),

    # Maestros — Clientes
    path('maestros/clientes/',                views.clientes_lista,      name='clientes_lista'),
    path('maestros/clientes/nuevo/',          views.cliente_crear,       name='cliente_crear'),
    path('maestros/clientes/<int:pk>/editar/',views.cliente_editar,      name='cliente_editar'),

    # Maestros — Agencias
    path('maestros/agencias/',                views.agencias_lista,      name='agencias_lista'),
    path('maestros/agencias/nueva/',          views.agencia_crear,       name='agencia_crear'),
    path('maestros/agencias/<int:pk>/editar/',views.agencia_editar,      name='agencia_editar'),
    path('maestros/agencias/<int:pk>/toggle/',views.agencia_toggle,      name='agencia_toggle'),

    # Maestros — Choferes
    path('maestros/choferes/',                views.choferes_lista,      name='choferes_lista'),
    path('maestros/choferes/nuevo/',          views.chofer_crear,        name='chofer_crear'),
    path('maestros/choferes/<int:pk>/editar/',views.chofer_editar,       name='chofer_editar'),
    path('maestros/choferes/<int:pk>/toggle/',views.chofer_toggle,       name='chofer_toggle'),

    # Documentos (imprimibles)
    path('doc/doc1/<int:exp_pk>/',            views.doc_doc1,            name='doc_doc1'),
    path('doc/cmr/<int:exp_pk>/',             views.doc_cmr,             name='doc_cmr'),

    # Histórico y exportación (Fase 5)
    path('historico/',                        views.historico,           name='historico'),
    path('export/expediciones/',              views.export_expediciones_csv, name='export_expediciones'),
    path('export/visitas/',                   views.export_visitas_csv,  name='export_visitas'),

    # ASN / Recepción inbound
    path('asn/',                              views.asn_lista,           name='asn_lista'),
    path('asn/nuevo/',                        views.asn_crear,           name='asn_crear'),
    path('asn/<int:pk>/',                     views.asn_detalle,         name='asn_detalle'),
    path('asn/<int:pk>/editar/',              views.asn_editar,          name='asn_editar'),
    path('asn/<int:pk>/cerrar/',              views.asn_cerrar,          name='asn_cerrar'),
    path('asn/<int:pk>/linea/',               views.asn_linea_agregar,   name='asn_linea_agregar'),
    path('asn/linea/<int:linea_id>/contar/',  views.asn_linea_contar,    name='asn_linea_contar'),
    path('asn/linea/<int:linea_id>/eliminar/',views.asn_linea_eliminar,  name='asn_linea_eliminar'),
]
