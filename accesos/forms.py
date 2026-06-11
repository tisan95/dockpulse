from django import forms
from .models import Visit, Incidencia

W = {'class': 'dp-input'}


class CheckInEntradaForm(forms.ModelForm):
    class Meta:
        model  = Visit
        fields = [
            'dni_chofer', 'nombre_chofer',
            'matricula_tractora', 'matricula_remolque',
            'agencia', 'muelle',
            'numero_contenedor', 'orden_compra',
            'puerto_origen', 'bultos_declarados',
        ]
        labels = {
            'dni_chofer':          'DNI del chofer',
            'nombre_chofer':       'Nombre completo',
            'matricula_tractora':  'Matrícula tractora',
            'matricula_remolque':  'Matrícula remolque (opcional)',
            'agencia':             'Agencia transportista',
            'muelle':              'Muelle asignado',
            'numero_contenedor':   'Nº contenedor / BL',
            'orden_compra':        'Orden de compra (OC)',
            'puerto_origen':       'Puerto de origen',
            'bultos_declarados':   'Bultos declarados',
        }
        widgets = {
            'dni_chofer':         forms.TextInput(attrs={**W, 'placeholder': '12345678A'}),
            'nombre_chofer':      forms.TextInput(attrs={**W, 'placeholder': 'Nombre y apellidos'}),
            'matricula_tractora': forms.TextInput(attrs={**W, 'placeholder': '1234ABC'}),
            'matricula_remolque': forms.TextInput(attrs={**W, 'placeholder': 'R-5678XY'}),
            'agencia':            forms.TextInput(attrs={**W, 'placeholder': 'XPO Logistics'}),
            'numero_contenedor':  forms.TextInput(attrs={**W, 'placeholder': 'MRKU1234567'}),
            'orden_compra':       forms.TextInput(attrs={**W, 'placeholder': 'OC-2024-0001'}),
            'puerto_origen':      forms.TextInput(attrs={**W, 'placeholder': 'Valencia, Algeciras…'}),
            'bultos_declarados':  forms.NumberInput(attrs={**W, 'placeholder': '0'}),
        }


class CheckInSalidaForm(forms.ModelForm):
    class Meta:
        model  = Visit
        fields = [
            'dni_chofer', 'nombre_chofer',
            'matricula_tractora', 'matricula_remolque',
            'agencia', 'muelle',
            'tipo_salida', 'cliente',
            'agencia_mensajeria', 'num_pedidos',
        ]
        labels = {
            'dni_chofer':          'DNI del chofer',
            'nombre_chofer':       'Nombre completo',
            'matricula_tractora':  'Matrícula tractora',
            'matricula_remolque':  'Matrícula remolque (opcional)',
            'agencia':             'Agencia transportista',
            'muelle':              'Muelle asignado',
            'tipo_salida':         'Tipo de expedición',
            'cliente':             'Cliente / destinatario',
            'agencia_mensajeria':  'Agencia de mensajería',
            'num_pedidos':         'Nº de pedidos cargados',
        }
        widgets = {
            'dni_chofer':         forms.TextInput(attrs={**W, 'placeholder': '12345678A'}),
            'nombre_chofer':      forms.TextInput(attrs={**W, 'placeholder': 'Nombre y apellidos'}),
            'matricula_tractora': forms.TextInput(attrs={**W, 'placeholder': '1234ABC'}),
            'matricula_remolque': forms.TextInput(attrs={**W, 'placeholder': 'R-5678XY'}),
            'agencia':            forms.TextInput(attrs={**W, 'placeholder': 'XPO Logistics'}),
            'tipo_salida':        forms.Select(attrs=W),
            'cliente':            forms.TextInput(attrs={**W, 'placeholder': 'Mercadona, Amazon…'}),
            'agencia_mensajeria': forms.TextInput(attrs={**W, 'placeholder': 'GLS, SEUR, UPS…'}),
            'num_pedidos':        forms.NumberInput(attrs={**W, 'placeholder': '0'}),
        }


class CheckOutForm(forms.Form):
    matricula_tractora = forms.CharField(
        max_length=20,
        label='Matrícula tractora',
        widget=forms.TextInput(attrs={**W, 'placeholder': 'Buscar por matrícula…'}),
    )
    documentacion_ok = forms.BooleanField(required=False, label='Documentación correcta')
    precinto = forms.CharField(
        max_length=100, required=False, label='Precinto',
        widget=forms.TextInput(attrs={**W, 'placeholder': 'Número de precinto (si aplica)'}),
    )
    bultos_reales = forms.IntegerField(
        required=False, label='Bultos reales (solo entradas)',
        widget=forms.NumberInput(attrs={**W, 'placeholder': '0'}),
    )


class IncidenciaForm(forms.ModelForm):
    class Meta:
        model  = Incidencia
        fields = ['tipo', 'descripcion', 'urgente']
        labels = {
            'tipo':        'Tipo de incidencia',
            'descripcion': 'Descripción',
            'urgente':     'Marcar como urgente',
        }
        widgets = {
            'tipo':        forms.Select(attrs=W),
            'descripcion': forms.Textarea(attrs={**W, 'rows': 3, 'placeholder': 'Detalla la incidencia…'}),
        }
