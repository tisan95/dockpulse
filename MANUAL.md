# DockPulse — Manual de uso

## Índice

1. [Introducción](#1-introducción)
2. [Pantalla principal (TV de almacén)](#2-pantalla-principal-tv-de-almacén)
3. [Expediciones](#3-expediciones)
4. [Check-in — Entrada de vehículos](#4-check-in--entrada-de-vehículos)
5. [Check-out — Salida de vehículos](#5-check-out--salida-de-vehículos)
6. [Recepciones ASN (inbound)](#6-recepciones-asn-inbound)
7. [Documentos — DOC1 y CMR](#7-documentos--doc1-y-cmr)
8. [Maestros — Datos de referencia](#8-maestros--datos-de-referencia)
9. [Dashboard y Histórico](#9-dashboard-y-histórico)
10. [Exportación de datos](#10-exportación-de-datos)

---

## 1. Introducción

DockPulse es un sistema de gestión de muelles y expediciones para plataformas logísticas. Digitaliza el flujo completo de entrada y salida de camiones, sustituyendo hojas de cálculo y registros manuales.

**Flujo general:**

```
Expedición (cita previa) ──► Check-in (llegada física) ──► Operación en muelle ──► Check-out (salida)
                                                                                        │
                                                                                        └──► DOC1 / CMR
```

**Tipos de expedición que maneja el sistema:**

| Código | Nombre | Descripción |
|--------|--------|-------------|
| **TRD** | Gran cuenta | Envíos a grandes distribuidores nacionales |
| **BLK** | Distribuidores / Bulk | Envíos a distribuidores medianos |
| **BDP** | Paquetería | Envíos de pequeño volumen |
| **EXW** | Exportación | Salidas internacionales (genera CMR) |
| **ENT** | Entrada / Recepción | Llegada de mercancía al almacén |

---

## 2. Pantalla principal (TV de almacén)

**Ruta:** `/` o `/pantalla/`

Diseñada para mostrarse en una pantalla grande del almacén. Se refresca automáticamente cada 30 segundos.

### Grid de muelles

Cada tarjeta representa un muelle físico:

- **Verde** — Libre, sin camión asignado
- **Amarillo parpadeante** — Operando (camión en descarga/carga activa)
- **Rojo parpadeante** — Ocupado / en espera

Desde cada tarjeta ocupada se puede:
- Pulsar **▶ Iniciar** para pasar de ESPERANDO → OPERANDO
- Pulsar **✓ Listo** para pasar de OPERANDO → LISTO
- Pulsar **⚠** para registrar una incidencia
- Pulsar **Salida →** para ir directamente al check-out de ese vehículo

### Expediciones pendientes del día

Debajo del grid aparecen todas las expediciones con cita para hoy que aún no han llegado a muelle, ordenadas por hora de cita. Permite anticipar la carga de trabajo de la jornada.

### Tabla de vehículos en planta

Lista todos los camiones actualmente en las instalaciones con:
- Tipo de operación, muelle asignado, agencia, cliente
- Matrícula, nombre del chofer
- **Alerta de tiempo**: verde (<2h), amarillo (2–4h), rojo (>4h)
- Estado actual e incidencias abiertas

---

## 3. Expediciones

**Ruta:** `/expediciones/`

### Crear una expedición

Una expedición es una cita previa: sabemos que va a llegar un camión, cuándo y para qué.

1. Ir a **Expediciones → Nueva expedición**
2. Rellenar los campos obligatorios:
   - **Nº expedición** — Identificador único (ej: `24TRD000101`)
   - **Tipo** — TRD / BLK / BDP / EXW / ENT
   - **Fecha y hora de cita**
3. Seleccionar cliente y agencia de la base de datos (o escribir el nombre si no existe aún)
4. Asignar muelle previsto y palets estimados
5. Guardar

### Filtrar expediciones

La lista permite filtrar por:
- **Fecha** (por defecto muestra el día actual)
- **Estado** — Pendiente / Gestionado / Lanzado / Preparado / En muelle / Enviada / Anulada
- **Tipo** — TRD / BLK / BDP / EXW / ENT

### Estados de una expedición

```
PENDIENTE ──► GESTIONADO ──► LANZADO ──► PREPARADO ──► MUELLE ──► ENVIADA
                                                                  
                                              └──────────────────► ANULADA
```

- **PENDIENTE** — Cita registrada, sin gestionar
- **GESTIONADO** — Confirmada con la agencia
- **LANZADO** — Orden lanzada al almacén
- **PREPARADO** — Mercancía lista para cargar
- **MUELLE** — El camión ha llegado y está en muelle (se asigna automáticamente en el check-in)
- **ENVIADA** — El camión ha salido (se asigna automáticamente en el check-out)
- **ANULADA** — Cancelada

El estado se puede cambiar manualmente desde la lista usando el selector de cada fila.

---

## 4. Check-in — Entrada de vehículos

**Ruta:** `/checkin/`

Proceso en **2 pasos**:

### Paso 1 — Buscar

Introduce el **número de expedición** (ej: `24TRD000101`) o el **DNI del chofer**.

- Si se encuentra la expedición, aparece la ficha completa (cliente, destino, agencia, cita, palets) antes de confirmar
- Si se encuentra el chofer por DNI, se prerrellena su nombre y matrícula habitual automáticamente

### Paso 2 — Confirmar entrada

Revisa o corrige:
- **Muelle asignado**
- **DNI y nombre del chofer** — Al escribir el DNI y salir del campo, el sistema busca automáticamente al chofer en la base de datos y rellena nombre y matrícula
- **Matrícula tractora** y remolque
- **Observaciones**

Al pulsar **Registrar entrada**:
- Se crea la visita (presencia física)
- La expedición pasa automáticamente a estado **MUELLE**
- El vehículo aparece en la pantalla principal

---

## 5. Check-out — Salida de vehículos

**Ruta:** `/checkout/`

### Buscar el vehículo

Introduce la **matrícula tractora** del camión que quiere salir. El sistema muestra la ficha completa de la visita.

### Confirmar salida

Rellena:
- **Palets reales** cargados/descargados
- **Documentación correcta** — Marcar si la documentación está en regla
- **Nº precinto** — Si se ha precintado el vehículo

Al confirmar:
- Se registra la hora exacta de salida
- La expedición pasa automáticamente a estado **ENVIADA**
- El vehículo desaparece de la pantalla principal

---

## 6. Recepciones ASN (inbound)

**Ruta:** `/asn/` (menú Maestros → Recepciones ASN)

El ASN (Advanced Shipping Notice) registra la llegada de mercancía al almacén con control de referencias y unidades.

### Crear un ASN

1. Ir a **Maestros → Recepciones ASN → Nuevo ASN**
2. Seleccionar la **expedición ENT** vinculada
3. Rellenar datos del contenedor:
   - Número de contenedor, Bill of Lading, Orden de compra
   - Proveedor, puerto de origen
   - Bultos declarados y peso
4. Guardar

### Añadir líneas de producto

En la pantalla de detalle del ASN, sección **Añadir línea**:
- Introduce la referencia, descripción, unidades declaradas y lote
- Repite para cada referencia del contenedor

### Contar mercancía recibida

Al descargar el contenedor, para cada línea:
1. Pulsa **Contar** junto a la referencia
2. Introduce las **unidades reales recibidas**
3. Si hay diferencia, indica el motivo y marca si se acepta
4. Guarda

El sistema marca automáticamente:
- ✅ **OK** — Coincide con lo declarado
- 🔴 **Falta** — Se recibieron menos unidades
- 🟡 **Exceso** — Se recibieron más unidades

### Cerrar la recepción

Una vez contadas todas las líneas, en el panel lateral:
1. Introduce los **bultos reales** totales recibidos
2. Selecciona el **estado final**: Completada o Con incidencia
3. Pulsa **Cerrar recepción**

Al completar, la expedición ENT pasa automáticamente a ENVIADA.

---

## 7. Documentos — DOC1 y CMR

Los documentos se generan directamente desde la lista de expediciones. Son páginas HTML optimizadas para imprimir o guardar como PDF desde el navegador.

### DOC1 — Nota de carga

Para expediciones **TRD, BLK, BDP y ENT**.

Incluye:
- Datos del remitente (hub de origen)
- Datos del destinatario / cliente con dirección completa
- Datos del transportista y vehículo (si ya hizo check-in)
- Tabla de control de carga (palets previstos vs. reales)
- Referencias SGA y albarán
- Zona de firmas (almacén / chofer / destino)

**Cómo generar:** En la lista de expediciones, columna Acciones → botón **DOC1**

### CMR — Carta de porte internacional

Para expediciones **EXW** (exportación internacional).

Sigue el formato estándar del Convenio CMR (Ginebra 1956):
- Casillas numeradas según el convenio (1–25)
- Remitente, destinatario, lugar de carga/entrega
- Datos del transportista y vehículo
- Descripción de la mercancía
- Instrucciones especiales y condiciones de pago (EXW)
- Zona de firmas tripartita

**Cómo generar:** En la lista de expediciones → filtrar por tipo EXW → botón **CMR**

### Imprimir / Guardar PDF

En ambos documentos, el botón **Imprimir / Guardar PDF** abre el diálogo de impresión del navegador. Para guardar como PDF:
- **Chrome/Edge:** Seleccionar "Guardar como PDF" en la opción de impresora
- **Firefox:** Seleccionar "PDF" en el menú desplegable de impresora

---

## 8. Maestros — Datos de referencia

**Ruta:** Menú **Maestros ▾**

### Clientes

Registro de todos los destinatarios. Campos clave:
- **Nombre y sucursal** — Ej: `AMAZON [ES]` / `AMAZON MAD6 ILLESCAS`
- **Tipo** — TRD / BLK / BDP / EXW (determina la categoría de expedición)
- **Dirección completa** — Se usa en los documentos DOC1/CMR
- **Accede tráiler** — Si las instalaciones del cliente admiten tráilers completos
- **Necesita plataforma** — Si requiere plataforma elevadora para la descarga

### Agencias

Transportistas y operadores logísticos:
- **Nick** — Código corto que se usa en pantalla (ej: `LAOSA`)
- **Nombre completo**, CIF, email, teléfono, contacto
- **Activa / Inactiva** — Toggle para deshabilitar sin borrar

### Choferes

Base de datos de conductores:
- **DNI** — Identificador único; se usa en el check-in para autocompletar
- **Nombre completo**, teléfono
- **Matrícula habitual** — Se prerrellena automáticamente en el check-in
- **Activo / Inactivo** — Toggle para deshabilitar sin borrar

> **Tip:** Cuantos más choferes estén dados de alta, más rápido es el check-in. El operador solo escribe el DNI y el sistema rellena el resto.

---

## 9. Dashboard y Histórico

### Dashboard

**Ruta:** `/dashboard/`

Vista del día actual:
- Vehículos en planta ahora
- Incidencias abiertas (con alerta si hay urgentes)
- Documentación incorrecta
- Desglose de expediciones por tipo (TRD / BLK / BDP / EXW / ENT)
- Vehículos activos con estado y tiempo en planta
- Top agencias por volumen de expediciones

### Histórico

**Ruta:** `/historico/`

Análisis sobre cualquier rango de fechas:
- Totales de expediciones, visitas completadas, enviadas y anuladas
- Barra de distribución proporcional por tipo de expedición
- Top 10 clientes por volumen
- Top 10 agencias por volumen
- Incidencias agrupadas por causante

Selecciona el rango de fechas en los filtros y pulsa **Aplicar**.

---

## 10. Exportación de datos

**Ruta:** `/historico/` → sección Exportar datos, o directamente:

| Archivo | Ruta | Contenido |
|---------|------|-----------|
| `expediciones.csv` | `/export/expediciones/` | Todas las expediciones con filtro de fechas |
| `visitas.csv` | `/export/visitas/` | Historial de visitas con tiempos y resultado |
| `TRD.csv` | `/export/expediciones/?tipo=TRD` | Solo expediciones TRD |
| `EXW.csv` | `/export/expediciones/?tipo=EXW` | Solo exportaciones |
| `Recepciones.csv` | `/export/expediciones/?tipo=ENT` | Solo entradas |

Los CSV usan separador `;` y codificación UTF-8 con BOM — se abren directamente en Excel sin configuración adicional.

**Filtrar antes de exportar:** Aplica el filtro de fechas en `/historico/` y usa los botones de exportación — el rango seleccionado se pasa automáticamente a los CSV.

---

## Incidencias

Desde cualquier vehículo activo (pantalla principal o detalle de visita) se puede registrar una incidencia:

- **Causante** — Administración / Agencia / Almacén / Cliente / Chofer
- **Tipo** — Booking incorrecto / Dirección incorrecta / Albarán incorrecto / Diferencia de palets / Avería / Paralización / Espera excesiva / Otro
- **Concepto de coste** — Envío / Devolución / Paralización / Manipulación / Sin coste
- **Descripción** — Texto libre
- **Urgente** — Si está marcada aparece con badge rojo en pantalla y en el dashboard

Las incidencias urgentes abiertas se muestran siempre en el dashboard como alerta.
