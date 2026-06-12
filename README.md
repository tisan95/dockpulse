# DockPulse

Sistema de gestión de muelles y expediciones para plataformas logísticas. Digitaliza el flujo completo de entrada y salida de camiones — desde la cita previa hasta la generación del documento de transporte — sustituyendo hojas de cálculo y registros manuales.

---

## Qué hace

- **Expediciones** — Registro previo de citas: qué camión viene, cuándo y a qué muelle, con estado en tiempo real (Pendiente → Preparado → En muelle → Enviada)
- **Check-in** — Entrada de vehículos en 2 pasos: buscar por número de expedición o DNI del chofer → confirmar datos del vehículo (autocompleta nombre y matrícula desde la BD de choferes)
- **Check-out** — Salida con registro de palets reales, documentación y precinto
- **Pantalla TV** — Vista en tiempo real para almacén: grid de muelles con colores por estado + expediciones pendientes del día + alerta de tiempo por camión
- **Recepciones ASN** — Registro de llegada de mercancía con control de referencias y unidades (declaradas vs. recibidas), cierre y control de diferencias
- **Documentos** — DOC1 (nota de carga) para expediciones nacionales y CMR (carta de porte internacional) para exportaciones, listos para imprimir o guardar como PDF
- **Maestros** — CRUD de Clientes, Agencias y Choferes
- **Histórico y exportación** — Análisis por rango de fechas, top clientes/agencias, descarga CSV compatible con Excel

## Tipos de expedición

| Código | Tipo | Documento |
|--------|------|-----------|
| TRD | Gran cuenta nacional | DOC1 |
| BLK | Distribuidores / Bulk | DOC1 |
| BDP | Paquetería | DOC1 |
| EXW | Exportación internacional | CMR |
| ENT | Entrada / Recepción inbound | ASN |

---

## Instalación

**Requisitos:** Python 3.10+

```bash
# 1. Clonar
git clone https://github.com/tisan95/dockpulse.git
cd dockpulse

# 2. Entorno virtual
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install django openpyxl

# 3. Migrar base de datos
python manage.py migrate

# 4. Arrancar
python manage.py runserver
```

Abre el navegador en **http://127.0.0.1:8000**

---

## URLs principales

| Ruta | Descripción |
|------|-------------|
| `/` | Pantalla TV — estado en tiempo real |
| `/expediciones/` | Lista de expediciones con filtros |
| `/expediciones/nueva/` | Crear expedición |
| `/checkin/` | Registro de entrada de camión |
| `/checkout/` | Registro de salida de camión |
| `/asn/` | Recepciones ASN (inbound) |
| `/doc/doc1/<id>/` | Generar DOC1 imprimible |
| `/doc/cmr/<id>/` | Generar CMR imprimible |
| `/dashboard/` | Métricas del día |
| `/historico/` | Análisis histórico y exportación CSV |
| `/maestros/clientes/` | Gestión de clientes |
| `/maestros/agencias/` | Gestión de agencias |
| `/maestros/choferes/` | Gestión de choferes |
| `/api/chofer/?dni=…` | API autocompletado de chofer por DNI |

---

## Stack técnico

- **Backend:** Django 4.2 (Python)
- **Base de datos:** SQLite (desarrollo) — compatible con PostgreSQL en producción
- **Frontend:** HTML/CSS vanilla, sistema de diseño dark propio, sin dependencias externas
- **Despliegue:** compatible con cualquier servidor WSGI (Gunicorn + Nginx)

---

## Manual de uso

Ver [MANUAL.md](MANUAL.md) para la guía completa de operación: check-in/check-out, gestión de expediciones, recepciones ASN, generación de documentos y exportación de datos.

---

## Próximos pasos sugeridos

- Autenticación con roles (operador / administración / solo lectura)
- WebSockets para refresco en tiempo real sin meta-refresh
- Migración a PostgreSQL para entorno multi-usuario
- Importación masiva de clientes y choferes desde Excel
