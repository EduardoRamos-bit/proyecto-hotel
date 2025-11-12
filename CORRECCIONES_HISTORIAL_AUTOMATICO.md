# Correcciones: Historial Automático con Acompañantes

## Fecha: 8 de Noviembre de 2025

---

## 🎯 Objetivo

Implementar un sistema automático que al cambiar el estado de una reserva a **'ocupada'** o **'cancelada'**, se realice:
1. INSERT completo de todos los datos de `v_reservas_con_anticipos` a `historial_reservas`
2. Inclusión de datos de acompañantes en formato JSON
3. DELETE de la reserva de la tabla `reservas` y sus acompañantes

---

## 🔧 Cambios Implementados

### **1. Base de Datos - Estructura Ampliada de historial_reservas**

**Archivo: `fix_database.sql` (líneas 10-36)**

#### Antes:
```sql
CREATE TABLE `historial_reservas` (
  `id_historial` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `id_reserva` INT(11) DEFAULT NULL,
  `id_cliente` INT(11) DEFAULT NULL,
  `id_habitacion` INT(11) DEFAULT NULL,
  `fecha_entrada` DATETIME DEFAULT NULL,
  `fecha_salida` DATETIME DEFAULT NULL,
  `estado` VARCHAR(50) DEFAULT NULL,
  `nombre` VARCHAR(50) DEFAULT NULL,
  `apellido` VARCHAR(50) DEFAULT NULL,
  `numero_habitacion` VARCHAR(10) DEFAULT NULL,
  `fecha_registro` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### Ahora:
```sql
CREATE TABLE `historial_reservas` (
  `id_historial` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `id_reserva` INT(11) DEFAULT NULL,
  `id_cliente` INT(11) DEFAULT NULL,
  `id_habitacion` INT(11) DEFAULT NULL,
  `fecha_entrada` DATETIME DEFAULT NULL,
  `fecha_salida` DATETIME DEFAULT NULL,
  `monto_total` DECIMAL(10,2) DEFAULT NULL,
  `monto_anticipo` DECIMAL(10,2) DEFAULT NULL,
  `porcentaje_anticipo` DECIMAL(5,2) DEFAULT NULL,
  `monto_restante` DECIMAL(10,2) DEFAULT NULL,
  `dias_estadia` INT(11) DEFAULT NULL,
  `estado` VARCHAR(50) DEFAULT NULL,
  `nombre` VARCHAR(50) DEFAULT NULL,
  `apellido` VARCHAR(50) DEFAULT NULL,
  `dni_pasaporte_cpf` VARCHAR(50) DEFAULT NULL,
  `numero_habitacion` VARCHAR(10) DEFAULT NULL,
  `tipo_habitacion` VARCHAR(50) DEFAULT NULL,
  `acompanantes_json` TEXT DEFAULT NULL,
  `fecha_registro` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_fecha_entrada` (`fecha_entrada`),
  KEY `idx_id_reserva` (`id_reserva`),
  KEY `idx_estado` (`estado`)
);
```

**Nuevos campos agregados:**
- ✅ `monto_total`, `monto_anticipo`, `porcentaje_anticipo`, `monto_restante`
- ✅ `dias_estadia`
- ✅ `dni_pasaporte_cpf`
- ✅ `tipo_habitacion`
- ✅ `acompanantes_json` (formato TEXT para almacenar JSON)
- ✅ Índice adicional en `estado`

---

### **2. Vista v_reservas_con_anticipos - IDs Agregados**

**Archivo: `fix_database.sql` (líneas 38-60)**

#### Ahora incluye:
```sql
CREATE VIEW `v_reservas_con_anticipos` AS 
SELECT 
    `r`.`id` AS `id`, 
    `r`.`id_cliente` AS `id_cliente`,          -- ⭐ NUEVO
    `r`.`id_habitacion` AS `id_habitacion`,    -- ⭐ NUEVO
    `r`.`fecha_entrada` AS `fecha_entrada`, 
    `r`.`fecha_salida` AS `fecha_salida`, 
    `r`.`monto` AS `monto_total`, 
    -- ... resto de campos
```

---

### **3. Función archivar_y_eliminar_reserva - Totalmente Reescrita**

**Archivo: `database.py` (líneas 914-1002)**

#### Lógica implementada:

```python
def archivar_y_eliminar_reserva(id_reserva, motivo_archivo='cancelada'):
    """Copia una reserva con todos sus datos (incluyendo acompañantes) a historial_reservas 
    y la borra de reservas."""
    
    # 1. Obtener datos completos desde v_reservas_con_anticipos
    cursor.execute("SELECT * FROM v_reservas_con_anticipos WHERE id = %s", (id_reserva,))
    reserva = cursor.fetchone()
    
    # 2. Obtener acompañantes
    cursor.execute("SELECT nombre, dni FROM acompanantes WHERE id_reserva = %s", (id_reserva,))
    acompanantes = cursor.fetchall()
    
    # 3. Convertir acompañantes a JSON
    import json
    acompanantes_json = json.dumps(acompanantes, default=str) if acompanantes else None
    
    # 4. Insertar en historial_reservas con TODOS los datos
    cursor.execute("""
        INSERT INTO historial_reservas (
            id_reserva, id_cliente, id_habitacion, fecha_entrada, fecha_salida,
            monto_total, monto_anticipo, porcentaje_anticipo, monto_restante, dias_estadia,
            estado, nombre, apellido, dni_pasaporte_cpf, numero_habitacion, tipo_habitacion,
            acompanantes_json
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (...))
    
    # 5. Borrar acompañantes primero (foreign key)
    cursor.execute("DELETE FROM acompanantes WHERE id_reserva = %s", (id_reserva,))
    
    # 6. Borrar reserva
    cursor.execute("DELETE FROM reservas WHERE id = %s", (id_reserva,))
```

**Cambios clave:**
- ✅ Usa `v_reservas_con_anticipos` en lugar de JOIN manual
- ✅ Obtiene y almacena acompañantes en formato JSON
- ✅ INSERT con 17 campos (antes eran 9)
- ✅ Borra acompañantes antes de borrar reserva
- ✅ Mejor logging de errores

---

### **4. Función cambiar_estado_reserva - Archivado Automático**

**Archivo: `database.py` (líneas 648-679)**

#### Nueva lógica:

```python
def cambiar_estado_reserva(id_reserva, nuevo_estado):
    """Cambia el estado de una reserva. Si el nuevo estado es 'ocupada' o 'cancelada', 
    archiva automáticamente la reserva en historial y la elimina de reservas."""
    
    # Si el estado es 'ocupada' o 'cancelada', archivar y eliminar
    if nuevo_estado in ('ocupada', 'cancelada'):
        logger.info(f"Estado {nuevo_estado} detectado, archivando reserva {id_reserva}...")
        exito = archivar_y_eliminar_reserva(id_reserva, motivo_archivo=nuevo_estado)
        if exito:
            logger.info(f"Reserva {id_reserva} archivada exitosamente con estado {nuevo_estado}")
        return exito
    
    # Para otros estados (confirmada, vencida), solo actualizar
    cursor.execute("UPDATE reservas SET estado = %s WHERE id = %s", (nuevo_estado, id_reserva))
    # ...
```

**Comportamiento:**
- ✅ **Estado 'ocupada'**: Archiva → Borra de reservas
- ✅ **Estado 'cancelada'**: Archiva → Borra de reservas
- ✅ **Estado 'confirmada'**: Solo actualiza (no archiva)
- ✅ **Estado 'vencida'**: Solo actualiza (no archiva)

---

### **5. Función listar_historial - Campos Completos**

**Archivo: `database.py` (líneas 1017-1055)**

#### Ahora trae TODOS los campos:
```python
sql = """
    SELECT id_historial, id_reserva, id_cliente, id_habitacion,
           fecha_entrada, fecha_salida, 
           monto_total, monto_anticipo, porcentaje_anticipo, monto_restante, dias_estadia,
           estado, nombre, apellido, dni_pasaporte_cpf, 
           numero_habitacion, tipo_habitacion, acompanantes_json,
           fecha_registro
    FROM historial_reservas
    {where_sql}
    ORDER BY fecha_entrada DESC, id_historial DESC
"""
```

---

### **6. Template historial.html - Vista Completa con Acompañantes**

**Archivo: `templates/historial.html` (líneas 55-149)**

#### Nuevas funcionalidades:

**Tabla ampliada:**
- ✅ Columna **Monto** con monto total y anticipo
- ✅ Columna **Cliente** con DNI
- ✅ Columna **Habitación** con tipo
- ✅ Columna **Detalles** con botón para ver acompañantes

**Modales de acompañantes:**
```html
<button type="button" class="btn btn-sm btn-outline-info" 
        data-bs-toggle="modal" data-bs-target="#acompModal{{ r.id_historial }}">
  <i class="fas fa-users"></i> Ver
</button>

<!-- Modal -->
<div class="modal fade" id="acompModal{{ r.id_historial }}">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-body">
        <h6>Lista de Acompañantes:</h6>
        <ul class="list-group">
          {% set acomp_list = r.acompanantes_json | from_json %}
          {% for acomp in acomp_list %}
          <li class="list-group-item">
            <strong>{{ acomp.nombre }}</strong> - DNI: {{ acomp.dni }}
          </li>
          {% endfor %}
        </ul>
      </div>
    </div>
  </div>
</div>
```

---

### **7. Filtro JSON en Flask**

**Archivo: `app.py` (líneas 6, 16-25)**

```python
import json

@app.template_filter('from_json')
def from_json_filter(value):
    """Convierte un string JSON en objeto Python"""
    if not value:
        return []
    try:
        return json.loads(value)
    except:
        return []
```

**Permite en templates:**
```jinja2
{% set acomp_list = r.acompanantes_json | from_json %}
{% for acomp in acomp_list %}
    {{ acomp.nombre }} - {{ acomp.dni }}
{% endfor %}
```

---

## 🔄 Flujo Completo del Sistema

### **Cuando se cambia estado a 'ocupada' o 'cancelada':**

```
1. Usuario/Admin cambia estado → cambiar_estado_reserva(id, 'ocupada')
                                           ↓
2. Se detecta estado 'ocupada'/'cancelada'
                                           ↓
3. Se llama → archivar_y_eliminar_reserva(id, 'ocupada')
                                           ↓
4. Se obtienen datos de v_reservas_con_anticipos
                                           ↓
5. Se obtienen acompañantes de tabla acompanantes
                                           ↓
6. Se convierte acompañantes a JSON
                                           ↓
7. INSERT en historial_reservas (17 campos)
                                           ↓
8. DELETE de acompanantes (id_reserva = X)
                                           ↓
9. DELETE de reservas (id = X)
                                           ↓
10. ✅ Reserva archivada con todos los datos
```

---

## 📊 Datos Guardados en Historial

### **Información de Reserva:**
- ID de reserva, cliente y habitación
- Fechas de entrada y salida
- Días de estadía

### **Información Financiera:**
- Monto total
- Monto de anticipo
- Porcentaje de anticipo
- Monto restante

### **Información de Cliente:**
- Nombre y apellido
- DNI/Pasaporte/CPF

### **Información de Habitación:**
- Número de habitación
- Tipo de habitación

### **Información de Acompañantes:**
```json
[
  {"nombre": "Juan Pérez", "dni": "12345678"},
  {"nombre": "María García", "dni": "87654321"}
]
```

---

## ✅ Instrucciones de Aplicación

### **Paso 1: Ejecutar fix_database.sql**
```bash
# En phpMyAdmin o MySQL:
mysql -u root -p hotel < fix_database.sql
```

Este script:
- ✅ Recrea tabla `historial_reservas` con nueva estructura
- ✅ Actualiza vista `v_reservas_con_anticipos`
- ✅ Mantiene compatibilidad con datos existentes

### **Paso 2: Los cambios de código ya están aplicados**
- `database.py` - Funciones actualizadas
- `app.py` - Filtro JSON agregado
- `templates/historial.html` - Vista completa

### **Paso 3: Reiniciar aplicación**
```bash
python app.py
```

---

## 🎯 Comportamiento Actualizado

### **Estados de Reserva:**

| Estado | Acción | Archiva | Borra |
|--------|--------|---------|-------|
| **confirmada** | Solo actualiza | ❌ No | ❌ No |
| **ocupada** | Archiva y borra | ✅ Sí | ✅ Sí |
| **cancelada** | Archiva y borra | ✅ Sí | ✅ Sí |
| **vencida** | Solo actualiza | ❌ No | ❌ No |

### **Visualización en Historial:**
- ✅ Tabla con toda la información financiera
- ✅ Botón "Ver" para acompañantes (si existen)
- ✅ Modal con lista de acompañantes
- ✅ Filtrado por mes y año

---

## 🚨 Consideraciones Importantes

### **1. Respaldo de Datos**
Antes de ejecutar `fix_database.sql`, hacer backup:
```sql
mysqldump -u root -p hotel > hotel_backup_$(date +%Y%m%d).sql
```

### **2. Migración de Datos Antiguos**
Los registros antiguos en `historial_reservas` quedarán con campos nuevos en NULL. Si necesitas migrarlos:
```sql
UPDATE historial_reservas h
JOIN reservas r ON h.id_reserva = r.id
SET h.monto_total = r.monto,
    h.monto_anticipo = r.monto_anticipo
WHERE h.monto_total IS NULL;
```

### **3. Foreign Keys**
Asegúrate de que la tabla `acompanantes` permita borrado en cascada o manual antes de borrar reservas.

---

## 📝 Notas Técnicas

### **Formato JSON de Acompañantes:**
```json
[
  {
    "nombre": "Nombre Completo",
    "dni": "12345678"
  }
]
```

### **Recuperación de Acompañantes en Python:**
```python
import json
acompanantes_json = registro['acompanantes_json']
if acompanantes_json:
    acompanantes = json.loads(acompanantes_json)
    for acomp in acompanantes:
        print(f"{acomp['nombre']} - {acomp['dni']}")
```

### **Recuperación en Jinja2:**
```jinja2
{% set acomp_list = r.acompanantes_json | from_json %}
{% for acomp in acomp_list %}
    {{ acomp.nombre }} - {{ acomp.dni }}
{% endfor %}
```

---

## ✅ Resultado Final

**Ahora el sistema:**
- ✅ Archiva automáticamente reservas ocupadas/canceladas
- ✅ Guarda TODOS los datos financieros
- ✅ Incluye acompañantes en formato JSON
- ✅ Borra reserva y acompañantes de tablas activas
- ✅ Muestra historial completo con todos los detalles
- ✅ Permite ver acompañantes en modales
- ✅ Mantiene integridad referencial

---

**Desarrollado por**: Sistema de Gestión Hotelera  
**Última actualización**: 8 de Noviembre de 2025 - 10:45 AM
