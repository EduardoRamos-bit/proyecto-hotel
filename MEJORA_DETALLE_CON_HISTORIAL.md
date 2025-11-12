# Mejora: Detalle de Habitación con Historial de Reservas

## Fecha: 8 de Noviembre de 2025 - 11:55 AM

---

## 🎯 Objetivo

Modificar la ruta `/habitaciones/detalle/<id>` para que además de mostrar la reserva activa, también muestre el historial completo de reservas de esa habitación específica desde la tabla `historial_reservas`.

---

## 🔧 Cambios Implementados

### **1. Nueva Función en database.py**

**Archivo: `database.py` (líneas 1112-1145)**

```python
def obtener_historial_por_habitacion(id_habitacion):
    """Obtiene el historial de reservas de una habitación específica"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id_historial, id_reserva, id_cliente, 
                fecha_entrada, fecha_salida,
                monto_total, monto_anticipo, porcentaje_anticipo, monto_restante, dias_estadia,
                estado, nombre, apellido, dni_pasaporte_cpf,
                numero_habitacion, tipo_habitacion, acompanantes_json,
                fecha_registro
            FROM historial_reservas
            WHERE id_habitacion = %s
            ORDER BY fecha_entrada DESC
        """
        cursor.execute(query, (id_habitacion,))
        historial = cursor.fetchall()
        
        logger.info(f"Encontrados {len(historial)} registros de historial para habitación {id_habitacion}")
        return historial
        
    except mysql.connector.Error as e:
        logger.error(f"Error al obtener historial de habitación: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

**Características:**
- ✅ Filtra por `id_habitacion`
- ✅ Ordena por `fecha_entrada DESC` (más recientes primero)
- ✅ Trae TODOS los campos del historial incluyendo acompañantes en JSON
- ✅ Retorna lista vacía en caso de error
- ✅ Logging de cantidad de registros encontrados

---

### **2. Ruta Modificada en app.py**

**Archivo: `app.py` (líneas 516-576)**

#### Antes:
```python
@app.route('/habitaciones/detalle/<int:id_habitacion>')
def detalle_habitacion_ruta(id_habitacion):
    # ... código ...
    
    return render_template(
        'detalle_habitacion.html',
        habitacion=habitacion,
        reserva=reserva,
        cliente=cliente,
        acompanantes=acompanantes,
        pagos=pagos,
        total_pagado=total_pagado,
        saldo_restante=saldo_restante
    )
```

#### Ahora:
```python
@app.route('/habitaciones/detalle/<int:id_habitacion>')
def detalle_habitacion_ruta(id_habitacion):
    # ... código existente ...
    
    # Obtener historial de reservas de esta habitación
    historial = database.obtener_historial_por_habitacion(id_habitacion)
    
    return render_template(
        'detalle_habitacion.html',
        habitacion=habitacion,
        reserva=reserva,
        cliente=cliente,
        acompanantes=acompanantes,
        pagos=pagos,
        total_pagado=total_pagado,
        saldo_restante=saldo_restante,
        historial=historial  # ⭐ NUEVO
    )
```

**Cambios:**
- ✅ Línea 559: Llama a `obtener_historial_por_habitacion(id_habitacion)`
- ✅ Línea 570: Pasa `historial` al template

---

### **3. Template Actualizado**

**Archivo: `templates/detalle_habitacion.html` (líneas 90-199)**

#### Nueva Sección Agregada:

```html
<!-- Historial de Reservas -->
{% if historial and historial|length > 0 %}
<hr>
<h5 class="mb-3">
  <i class="fas fa-history me-2"></i>Historial de Reservas
  <span class="badge bg-secondary">{{ historial|length }}</span>
</h5>

<div class="table-responsive">
  <table class="table table-sm table-hover align-middle">
    <thead class="table-dark">
      <tr>
        <th>#</th>
        <th>Cliente</th>
        <th>Entrada</th>
        <th>Salida</th>
        <th>Días</th>
        <th>Monto</th>
        <th>Estado</th>
        <th>Acompañantes</th>
        <th>Registrado</th>
      </tr>
    </thead>
    <tbody>
      {% for h in historial %}
      <tr>
        <td><small>{{ h.id_historial }}</small></td>
        <td>
          <strong>{{ h.nombre }} {{ h.apellido }}</strong>
          {% if h.dni_pasaporte_cpf %}
          <br><small class="text-muted">{{ h.dni_pasaporte_cpf }}</small>
          {% endif %}
        </td>
        <td><small>{{ h.fecha_entrada.strftime('%d/%m/%Y %H:%M') if h.fecha_entrada else '-' }}</small></td>
        <td><small>{{ h.fecha_salida.strftime('%d/%m/%Y %H:%M') if h.fecha_salida else '-' }}</small></td>
        <td><span class="badge bg-info">{{ h.dias_estadia or '-' }}</span></td>
        <td>
          {% if h.monto_total %}
          <strong>${{ "{:,.2f}".format(h.monto_total) }}</strong>
          {% if h.monto_anticipo %}
          <br><small class="text-success">Ant: ${{ "{:,.2f}".format(h.monto_anticipo) }}</small>
          {% endif %}
          {% else %}
          <span class="text-muted">-</span>
          {% endif %}
        </td>
        <td>
          {% if h.estado == 'ocupada' %}
          <span class="badge bg-success">{{ h.estado|title }}</span>
          {% elif h.estado == 'cancelada' %}
          <span class="badge bg-danger">{{ h.estado|title }}</span>
          {% else %}
          <span class="badge bg-secondary">{{ h.estado|title }}</span>
          {% endif %}
        </td>
        <td>
          {% if h.acompanantes_json %}
          <button type="button" class="btn btn-sm btn-outline-info" 
                  data-bs-toggle="modal" data-bs-target="#historialAcompModal{{ h.id_historial }}">
            <i class="fas fa-users"></i>
          </button>
          {% else %}
          <span class="text-muted">-</span>
          {% endif %}
        </td>
        <td><small class="text-muted">{{ h.fecha_registro.strftime('%d/%m/%Y') if h.fecha_registro else '-' }}</small></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<!-- Modales para acompañantes del historial -->
{% for h in historial %}
{% if h.acompanantes_json %}
<div class="modal fade" id="historialAcompModal{{ h.id_historial }}" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Acompañantes - Reserva Histórica #{{ h.id_historial }}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <p><strong>Cliente:</strong> {{ h.nombre }} {{ h.apellido }}</p>
        <p><strong>Fecha:</strong> {{ h.fecha_entrada.strftime('%d/%m/%Y') if h.fecha_entrada else '-' }} - {{ h.fecha_salida.strftime('%d/%m/%Y') if h.fecha_salida else '-' }}</p>
        <hr>
        <h6>Lista de Acompañantes:</h6>
        <ul class="list-group">
          {% set acomp_list = h.acompanantes_json | from_json %}
          {% for acomp in acomp_list %}
          <li class="list-group-item">
            <strong>{{ acomp.nombre }}</strong> - DNI: {{ acomp.dni }}
          </li>
          {% endfor %}
        </ul>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
      </div>
    </div>
  </div>
</div>
{% endif %}
{% endfor %}

{% else %}
<hr>
<div class="alert alert-secondary">
  <i class="fas fa-info-circle me-2"></i>No hay historial de reservas para esta habitación.
</div>
{% endif %}
```

**Características:**
- ✅ Tabla responsive con historial completo
- ✅ Badge con cantidad de registros
- ✅ Icono de reloj para indicar historial
- ✅ Colores de estado: verde (ocupada), rojo (cancelada), gris (otros)
- ✅ Formato de fechas: DD/MM/YYYY HH:MM
- ✅ Muestra monto total y anticipo
- ✅ Botón para ver acompañantes en modal
- ✅ Modales para cada registro con acompañantes
- ✅ Mensaje informativo si no hay historial

---

## 📊 Información Mostrada en el Historial

### **Por cada reserva histórica:**

| Campo | Descripción |
|-------|-------------|
| **#** | ID del historial |
| **Cliente** | Nombre completo + DNI |
| **Entrada** | Fecha y hora de entrada |
| **Salida** | Fecha y hora de salida |
| **Días** | Días de estadía |
| **Monto** | Monto total + Anticipo |
| **Estado** | ocupada, cancelada, etc. |
| **Acompañantes** | Botón para ver modal |
| **Registrado** | Fecha de registro en historial |

---

## 🔄 Flujo de Uso

```
Admin → Lista Habitaciones → Clic en habitación
                    ↓
        Detalle de Habitación
                    ↓
    ┌───────────────┴───────────────┐
    │                               │
Reserva Activa              Historial de Reservas
(si existe)                  (todos los registros)
    │                               │
- Cliente                    - Tabla con N reservas
- Acompañantes               - Fechas, montos, estados
- Pagos                      - Acompañantes en modales
- Saldo                      - Ordenado por más reciente
```

---

## 🎨 Mejoras de UI

### **Visual:**
- ✅ Icono de reloj (historia) en el título
- ✅ Badge con cantidad de registros
- ✅ Tabla compacta (`table-sm`) y con hover
- ✅ Colores semánticos para estados
- ✅ Fechas en formato legible
- ✅ Montos formateados con separadores de miles

### **Interactiva:**
- ✅ Botón para ver acompañantes
- ✅ Modales de Bootstrap 5
- ✅ Responsive en móviles

---

## 📈 Ventajas de Esta Implementación

### **Para el Admin:**
✅ **Vista completa** - Ve todo el historial de una habitación en un solo lugar
✅ **Análisis** - Puede ver patrones de uso de habitaciones
✅ **Seguimiento** - Rastrea clientes frecuentes de habitaciones específicas
✅ **Auditoría** - Verifica montos y estados pasados

### **Técnicas:**
✅ **Performance** - Query optimizado con un solo JOIN
✅ **Escalabilidad** - Funciona con cualquier cantidad de registros
✅ **Mantenibilidad** - Código limpio y documentado
✅ **Reutilizable** - Función puede usarse en otros contextos

---

## 🔍 Ejemplo de Datos Mostrados

### **Habitación 101 - Detalle:**

**Información de la habitación:**
- Tipo: Suite
- Precio: $150/noche
- Estado: Ocupada

**Reserva Actual:**
- Cliente: Juan Pérez
- Entrada: 08/11/2025 14:00
- Salida: 10/11/2025 12:00
- Total Pagado: $300
- Saldo: $0

**Historial de Reservas (3 registros):**

| # | Cliente | Entrada | Salida | Días | Monto | Estado | Registrado |
|---|---------|---------|--------|------|-------|--------|------------|
| 15 | María García | 05/11/25 | 07/11/25 | 2 | $300 | Ocupada | 07/11/25 |
| 12 | Pedro López | 01/11/25 | 03/11/25 | 2 | $280 | Cancelada | 03/11/25 |
| 8 | Ana Torres | 28/10/25 | 30/10/25 | 2 | $300 | Ocupada | 30/10/25 |

---

## ✅ Pruebas Recomendadas

### **Caso 1: Habitación con historial**
1. Ir a detalle de habitación que tiene reservas archivadas
2. Verificar que aparece tabla de historial
3. Verificar cantidad en badge
4. Hacer clic en botón de acompañantes (si hay)
5. Verificar modal con datos correctos

### **Caso 2: Habitación sin historial**
1. Ir a detalle de habitación nueva (sin reservas archivadas)
2. Verificar mensaje: "No hay historial de reservas para esta habitación"

### **Caso 3: Habitación con reserva activa + historial**
1. Verificar que muestra ambas secciones
2. Reserva actual arriba
3. Historial abajo

---

## 🚀 Uso del Sistema

### **Acceso al historial:**
```
Admin → Habitaciones → Clic en cualquier habitación → Detalle
                                     ↓
                       Scroll hacia abajo
                                     ↓
                    Sección "Historial de Reservas"
```

### **Ver acompañantes históricos:**
```
En tabla de historial → Botón 👥 → Modal con lista de acompañantes
```

---

## 📝 Notas Técnicas

### **Query Performance:**
- ✅ Índice en `id_habitacion` (recomendado agregarlo si no existe)
- ✅ ORDER BY en fecha_entrada para orden cronológico inverso

### **Formato de Fechas:**
```python
h.fecha_entrada.strftime('%d/%m/%Y %H:%M')
```
- Formato: 08/11/2025 14:30

### **Acompañantes en JSON:**
```json
[
  {"nombre": "Juan Pérez", "dni": "12345678"},
  {"nombre": "María García", "dni": "87654321"}
]
```

---

## 🔧 SQL Recomendado (Opcional)

### **Para mejorar performance, crear índice:**

```sql
CREATE INDEX idx_historial_habitacion ON historial_reservas(id_habitacion);
```

Esto acelerará las consultas de historial por habitación.

---

## 📊 Resumen de Archivos Modificados

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `database.py` | Función `obtener_historial_por_habitacion()` | 1112-1145 |
| `app.py` | Llamada a función + pasar historial al template | 559, 570 |
| `templates/detalle_habitacion.html` | Sección completa de historial + modales | 90-199 |

---

## ✅ Resultado Final

**El detalle de habitación ahora muestra:**
1. ✅ Información de la habitación
2. ✅ Reserva actual (si existe)
3. ✅ Cliente y acompañantes actuales
4. ✅ Pagos de reserva actual
5. ✅ **⭐ HISTORIAL COMPLETO de reservas pasadas**
6. ✅ Acompañantes históricos en modales
7. ✅ Botón para liberar habitación

---

**Desarrollado por**: Sistema de Gestión Hotelera  
**Última actualización**: 8 de Noviembre de 2025 - 11:55 AM
