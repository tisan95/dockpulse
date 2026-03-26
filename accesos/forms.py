from django import forms
from .models import Visit

# Formulario para el CHECK-IN
# Lo rellena control de accesos cuando llega el camión
class CheckInForm(forms.ModelForm):
    class Meta:
        model = Visit
        # Solo mostramos los campos de entrada, no los de salida
        fields = [
            'cita_carga',
            'dni_chofer',
            'nombre_chofer',
            'matricula_tractora',
            'matricula_remolque',  # opcional, puede venir vacío
            'agencia',
            'muelle',
        ]
        # Etiquetas en español para que el formulario sea claro
        labels = {
            'cita_carga':          'Cita de carga',
            'dni_chofer':          'DNI del chofer',
            'nombre_chofer':       'Nombre completo',
            'matricula_tractora':  'Matrícula tractora',
            'matricula_remolque':  'Matrícula remolque (opcional)',
            'agencia':             'Agencia transportista',
            'muelle':              'Muelle asignado',
        }
        # Estilos básicos para cada campo (clase CSS que usaremos después)
        widgets = {
            'cita_carga':         forms.TextInput(attrs={'class': 'dp-input', 'placeholder': 'Ej: CITA-2024-001'}),
            'dni_chofer':         forms.TextInput(attrs={'class': 'dp-input', 'placeholder': 'Ej: 12345678A'}),
            'nombre_chofer':      forms.TextInput(attrs={'class': 'dp-input', 'placeholder': 'Nombre y apellidos'}),
            'matricula_tractora': forms.TextInput(attrs={'class': 'dp-input', 'placeholder': 'Ej: 1234ABC'}),
            'matricula_remolque': forms.TextInput(attrs={'class': 'dp-input', 'placeholder': 'Ej: R-5678XY'}),
            'agencia':            forms.TextInput(attrs={'class': 'dp-input', 'placeholder': 'Ej: XPO Logistics'}),
            'muelle':             forms.TextInput(attrs={'class': 'dp-input', 'placeholder': 'Ej: M-03'}),
        }


# Formulario para el CHECK-OUT
# Lo rellena control de accesos cuando el camión sale
class CheckOutForm(forms.Form):
    # Buscamos el vehículo por matrícula tractora (campo de búsqueda)
    matricula_tractora = forms.CharField(
        max_length=20,
        label='Matrícula tractora',
        widget=forms.TextInput(attrs={
            'class': 'dp-input',
            'placeholder': 'Buscar por matrícula...'
        })
    )
    # ¿La documentación estaba en orden al salir?
    documentacion_ok = forms.BooleanField(
        required=False,  # False porque puede no estar marcado (= documentación KO)
        label='Documentación correcta',
    )
    # Número o referencia del precinto del remolque
    precinto = forms.CharField(
        max_length=100,
        required=False,  # No todos los vehículos llevan precinto
        label='Precinto',
        widget=forms.TextInput(attrs={
            'class': 'dp-input',
            'placeholder': 'Número de precinto (si aplica)'
        })
    )