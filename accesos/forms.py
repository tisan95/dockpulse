from django import forms
from .models import Visit, Expedicion, Incidencia, Cliente, Agencia, Chofer

W = {'class': 'dp-input'}


class BuscarExpedicionForm(forms.Form):
    """Paso 1 del check-in: buscar por nº expedición o DNI del chofer."""
    busqueda = forms.CharField(
        max_length=50,
        label='Nº expedición o DNI del chofer',
        widget=forms.TextInput(attrs={
            **W,
            'placeholder': '24TRD000123  /  12345678A',
            'autofocus': True,
            'autocomplete': 'off',
        }),
    )


class ExpedicionForm(forms.ModelForm):
    """Crear / editar una expedición (cita previa)."""
    class Meta:
        model  = Expedicion
        fields = [
            'numero', 'tipo', 'hub_origen',
            'fecha_cita', 'hora_cita',
            'cliente', 'cliente_nombre', 'destino',
            'agencia', 'agencia_nombre',
            'muelle', 'palets_previstos',
            'sga', 'albaran', 'observaciones',
        ]
        labels = {
            'numero':          'Nº expedición',
            'tipo':            'Tipo',
            'hub_origen':      'Hub de origen',
            'fecha_cita':      'Fecha de cita',
            'hora_cita':       'Hora de cita',
            'cliente':         'Cliente (BD)',
            'cliente_nombre':  'Cliente (texto libre)',
            'destino':         'Destino',
            'agencia':         'Agencia (BD)',
            'agencia_nombre':  'Agencia (texto libre)',
            'muelle':          'Muelle previsto',
            'palets_previstos':'Palets previstos',
            'sga':             'Nº pedido SGA',
            'albaran':         'Albarán',
            'observaciones':   'Observaciones',
        }
        widgets = {
            'numero':          forms.TextInput(attrs={**W, 'placeholder': '24TRD000001'}),
            'tipo':            forms.Select(attrs=W),
            'hub_origen':      forms.Select(attrs=W),
            'fecha_cita':      forms.DateInput(attrs={**W, 'type': 'date'}),
            'hora_cita':       forms.TimeInput(attrs={**W, 'type': 'time'}),
            'cliente':         forms.Select(attrs=W),
            'cliente_nombre':  forms.TextInput(attrs={**W, 'placeholder': 'Solo si no está en BD'}),
            'destino':         forms.TextInput(attrs={**W, 'placeholder': 'Ciudad o FC de destino'}),
            'agencia':         forms.Select(attrs=W),
            'agencia_nombre':  forms.TextInput(attrs={**W, 'placeholder': 'Solo si no está en BD'}),
            'muelle':          forms.Select(attrs=W),
            'palets_previstos':forms.NumberInput(attrs={**W, 'placeholder': '0'}),
            'sga':             forms.TextInput(attrs={**W, 'placeholder': 'B24001234-1'}),
            'albaran':         forms.TextInput(attrs={**W, 'placeholder': '24-000001'}),
            'observaciones':   forms.Textarea(attrs={**W, 'rows': 2}),
        }


class CheckInForm(forms.ModelForm):
    """Confirmar la llegada física: corregir/completar datos del vehículo."""
    class Meta:
        model  = Visit
        fields = ['muelle', 'dni_chofer', 'nombre_chofer',
                  'matricula_tractora', 'matricula_remolque', 'observaciones']
        labels = {
            'muelle':              'Muelle asignado',
            'dni_chofer':          'DNI del chofer',
            'nombre_chofer':       'Nombre del chofer',
            'matricula_tractora':  'Matrícula tractora',
            'matricula_remolque':  'Matrícula remolque (opcional)',
            'observaciones':       'Observaciones',
        }
        widgets = {
            'muelle':             forms.Select(attrs=W),
            'dni_chofer':         forms.TextInput(attrs={**W, 'placeholder': '12345678A'}),
            'nombre_chofer':      forms.TextInput(attrs={**W, 'placeholder': 'Nombre y apellidos'}),
            'matricula_tractora': forms.TextInput(attrs={**W, 'placeholder': '1234ABC'}),
            'matricula_remolque': forms.TextInput(attrs={**W, 'placeholder': 'R-5678XY'}),
            'observaciones':      forms.Textarea(attrs={**W, 'rows': 2}),
        }


class CheckOutForm(forms.Form):
    matricula_tractora = forms.CharField(
        max_length=20, label='Matrícula tractora',
        widget=forms.TextInput(attrs={**W, 'placeholder': 'Buscar por matrícula…'}),
    )
    documentacion_ok = forms.BooleanField(required=False, label='Documentación correcta')
    precinto = forms.CharField(
        max_length=100, required=False, label='Nº precinto',
        widget=forms.TextInput(attrs={**W, 'placeholder': 'PRE-00123'}),
    )
    palets_reales = forms.IntegerField(
        required=False, label='Palets reales',
        widget=forms.NumberInput(attrs={**W, 'placeholder': '0'}),
    )


class IncidenciaForm(forms.ModelForm):
    class Meta:
        model  = Incidencia
        fields = ['causante', 'tipo', 'concepto_coste', 'descripcion', 'urgente']
        labels = {
            'causante':      'Causante',
            'tipo':          'Tipo de incidencia',
            'concepto_coste':'Concepto de coste extra',
            'descripcion':   'Descripción',
            'urgente':       'Marcar como urgente',
        }
        widgets = {
            'causante':      forms.Select(attrs=W),
            'tipo':          forms.Select(attrs=W),
            'concepto_coste':forms.Select(attrs=W),
            'descripcion':   forms.Textarea(attrs={**W, 'rows': 3,
                             'placeholder': 'Detalla la incidencia…'}),
        }


# ── MAESTROS ──────────────────────────────────────────────────────────────────

class ClienteForm(forms.ModelForm):
    class Meta:
        model  = Cliente
        fields = ['nombre', 'sucursal', 'tipo', 'direccion', 'cp',
                  'poblacion', 'provincia', 'pais',
                  'necesita_plataforma', 'accede_trailer', 'observaciones']
        labels = {
            'nombre': 'Nombre / razón social',
            'sucursal': 'Sucursal / FC',
            'tipo': 'Tipo de cliente',
            'direccion': 'Dirección',
            'cp': 'Código postal',
            'poblacion': 'Población',
            'provincia': 'Provincia',
            'pais': 'País',
            'necesita_plataforma': 'Necesita plataforma',
            'accede_trailer': 'Accede tráiler',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'nombre':     forms.TextInput(attrs={**W, 'placeholder': 'AMAZON [ES]'}),
            'sucursal':   forms.TextInput(attrs={**W, 'placeholder': 'AMAZON MAD6 ILLESCAS'}),
            'tipo':       forms.Select(attrs=W),
            'direccion':  forms.TextInput(attrs=W),
            'cp':         forms.TextInput(attrs={**W, 'placeholder': '28000'}),
            'poblacion':  forms.TextInput(attrs=W),
            'provincia':  forms.TextInput(attrs=W),
            'pais':       forms.TextInput(attrs={**W, 'placeholder': 'ESPAÑA'}),
            'observaciones': forms.Textarea(attrs={**W, 'rows': 2}),
        }


class AgenciaForm(forms.ModelForm):
    class Meta:
        model  = Agencia
        fields = ['nick', 'nombre', 'cif', 'email', 'telefono', 'contacto']
        labels = {
            'nick':     'Código / nick',
            'nombre':   'Nombre completo',
            'cif':      'CIF',
            'email':    'Email',
            'telefono': 'Teléfono',
            'contacto': 'Persona de contacto',
        }
        widgets = {
            'nick':     forms.TextInput(attrs={**W, 'placeholder': 'LAOSA'}),
            'nombre':   forms.TextInput(attrs={**W, 'placeholder': 'LAOSA TRANSPORTES'}),
            'cif':      forms.TextInput(attrs={**W, 'placeholder': 'B12345678'}),
            'email':    forms.EmailInput(attrs={**W, 'placeholder': 'info@agencia.es'}),
            'telefono': forms.TextInput(attrs={**W, 'placeholder': '963 000 000'}),
            'contacto': forms.TextInput(attrs={**W, 'placeholder': 'Nombre del operador'}),
        }


class ChoferForm(forms.ModelForm):
    class Meta:
        model  = Chofer
        fields = ['dni', 'nombre', 'telefono', 'matricula_habitual']
        labels = {
            'dni':               'DNI / NIE',
            'nombre':            'Nombre completo',
            'telefono':          'Teléfono',
            'matricula_habitual':'Matrícula habitual',
        }
        widgets = {
            'dni':               forms.TextInput(attrs={**W, 'placeholder': '12345678A', 'autocomplete': 'off'}),
            'nombre':            forms.TextInput(attrs={**W, 'placeholder': 'Nombre y apellidos'}),
            'telefono':          forms.TextInput(attrs={**W, 'placeholder': '600 000 000'}),
            'matricula_habitual':forms.TextInput(attrs={**W, 'placeholder': '1234ABC'}),
        }
