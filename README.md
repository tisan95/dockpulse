# DockPulse

Sistema de gestión de accesos y muelles para distribuidoras logísticas. Diseñado para el flujo real de una plataforma tipo Cecotec: recepción de contenedores desde el puerto y expedición hacia grandes cuentas y paquetería.

---

## ¿Qué hace?

DockPulse digitaliza el control de entrada y salida de camiones en un almacén, diferenciando dos flujos operativos:

- **Recepción**: camiones que llegan del puerto con contenedores. Se registra número de contenedor, orden de compra, puerto de origen y bultos declarados vs. reales.
- **Expedición**: camiones que salen con mercancía hacia clientes (gran cuenta como Mercadona o Amazon) o agencias de mensajería (GLS, SEUR, UPS…).

Cada vehículo se asigna a un muelle con estado en tiempo real, y el sistema alerta visualmente cuando un camión lleva demasiado tiempo en planta.

---

## Pantallas

### Pantalla de almacén (TV)
Vista en tiempo real para poner en una pantalla grande del almacén. Muestra:
- Grid de muelles con colores por estado (verde = libre, amarillo = operando, rojo = ocupado/en espera)
- Tabla de vehículos activos con alerta de tiempo (verde < 2h, amarillo 2–4h, rojo > 4h)
- Botones para avanzar el estado del muelle sin salir de la pantalla

### Check-in
Formulario bifurcado según el tipo de operación:
- **Recepción**: datos del vehículo + nº contenedor, OC, puerto de origen, bultos declarados
- **Expedición**: datos del vehículo + tipo (gran cuenta / paquetería), cliente, agencia mensajería, nº pedidos

### Check-out
Búsqueda por matrícula tractora. Muestra toda la información del vehículo y permite:
- Confirmar salida con hora exacta
- Registrar bultos reales descargados (entradas)
- Indicar si la documentación es correcta
- Añadir número de precinto

### Dashboard
Métricas operativas del día:
- Vehículos en planta, recepciones y expediciones del día
- Incidencias abiertas (con alerta si hay urgentes)
- Documentación incorrecta
- Vehículos activos con su estado
- Top 5 agencias por volumen de visitas

### Incidencias
Desde cualquier vehículo activo se puede registrar una incidencia con tipo (documentación, bultos, avería, carga, espera, otro), descripción y flag de urgente.

---

## Modelos de datos

### `Muelle`
| Campo | Descripción |
|---|---|
| `numero` | Identificador del muelle (M01, M02…) |
| `tipo` | RECEPCION / EXPEDICION / MIXTO |
| `activo` | Habilitado o no |

El estado del muelle (`LIBRE`, `ESPERANDO`, `OPERANDO`, `LISTO`) se calcula dinámicamente desde la visita activa asignada.

### `Visit`
| Campo | Descripción |
|---|---|
| `tipo` | ENTRADA (recepción) / SALIDA (expedición) |
| `estado` | ESPERANDO → OPERANDO → LISTO → SALIDO |
| `muelle` | FK a Muelle |
| `dni_chofer`, `nombre_chofer` | Datos del conductor |
| `matricula_tractora`, `matricula_remolque` | Vehículo |
| `agencia` | Transportista |
| `entrada` | Timestamp automático de llegada |
| — *Solo ENTRADA* — | |
| `numero_contenedor` | Nº contenedor o Bill of Lading |
| `orden_compra` | OC asociada |
| `puerto_origen` | Puerto de procedencia |
| `bultos_declarados` / `bultos_reales` | Control de merma |
| — *Solo SALIDA* — | |
| `tipo_salida` | GRAN_CUENTA / PAQUETERIA |
| `cliente` | Destinatario |
| `agencia_mensajeria` | GLS, SEUR, UPS… |
| `num_pedidos` | Pedidos cargados |
| — *Check-out* — | |
| `documentacion_ok` | Boolean |
| `precinto` | Número de precinto |
| `salida` | Timestamp de salida |

### `Incidencia`
| Campo | Descripción |
|---|---|
| `visita` | FK a Visit |
| `tipo` | DOCUMENTACION / BULTOS / AVERIA / CARGA / ESPERA / OTRO |
| `descripcion` | Texto libre |
| `urgente` | Boolean |
| `resuelta` | Boolean |

---

## Instalación y arranque

**Requisitos**: Python 3.10+

```bash
# 1. Clonar el repositorio
git clone https://github.com/tisan95/dockpulse.git
cd dockpulse

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install django

# 3. Aplicar migraciones
python manage.py migrate

# 4. Cargar muelles iniciales (M01–M08)
python manage.py shell -c "
from accesos.models import Muelle
muelles = [
    ('01','RECEPCION'),('02','RECEPCION'),('03','RECEPCION'),
    ('04','EXPEDICION'),('05','EXPEDICION'),('06','EXPEDICION'),
    ('07','MIXTO'),('08','MIXTO'),
]
for num, tipo in muelles:
    Muelle.objects.get_or_create(numero=num, defaults={'tipo': tipo})
print('Muelles creados:', Muelle.objects.count())
"

# 5. Arrancar el servidor
python manage.py runserver
```

Abre el navegador en **http://127.0.0.1:8000**

---

## URLs

| Ruta | Vista | Descripción |
|---|---|---|
| `/` | Pantalla almacén | Página principal — para TV |
| `/pantalla/` | Pantalla almacén | Igual que `/` |
| `/checkin/` | Check-in | Registro de entrada de camión |
| `/checkout/` | Check-out | Registro de salida |
| `/dashboard/` | Dashboard | Métricas operativas |
| `/visita/<id>/estado/` | Cambiar estado | Avanza el estado del muelle (POST) |
| `/visita/<id>/incidencia/` | Nueva incidencia | Formulario de incidencia |

---

## Stack técnico

- **Backend**: Django 4.2 (Python)
- **Base de datos**: SQLite (desarrollo) — fácilmente sustituible por PostgreSQL en producción
- **Frontend**: HTML/CSS vanilla con sistema de diseño dark propio, sin dependencias externas
- **Despliegue**: compatible con cualquier servidor WSGI (Gunicorn + Nginx)

---

## Próximos pasos sugeridos

- [ ] Autenticación: roles por pantalla (control de accesos, operaciones, solo lectura)
- [ ] Exportación de histórico a Excel/CSV
- [ ] Citas previas: registrar camiones esperados antes de que lleguen
- [ ] WebSockets para refresco en tiempo real sin meta-refresh
- [ ] Tiempo medio por muelle y por agencia en el dashboard
