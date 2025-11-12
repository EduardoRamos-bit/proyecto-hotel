# Mejoras: Detalle de Habitación y Gestión de Historial

## Fecha: 8 de Noviembre de 2025 - 11:10 AM

---

## 🎯 Mejoras Implementadas

### **1. Botón para Liberar Habitación**

#### **Archivo: `database.py` (líneas 1057-1080)**

**Función mejorada:**
```python
def liberar_habitacion(id_habitacion):
    """Libera una habitación cambiando su estado a 'disponible'"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("UPDATE habitaciones SET estado='disponible' WHERE id=%s", (id_habitacion,))
        conn.commit()
        logger.info(f"Habitación {id_habitacion} liberada")
        return True

    except Exception as e:
        logger.error(f"Error al liberar habitación: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

**Características:**
- ✅ Cambia el estado de la habitación a 'disponible'
- ✅ Logging mejorado
- ✅ Manejo de errores con rollback
- ✅ Cierre seguro de conexiones

---

#### **Archivo: `app.py` (líneas 574-590)**

**Nueva ruta agregada:**
```python
@app.route('/habitaciones/liberar/<int:id_habitacion>', methods=['POST'])
def liberar_habitacion_ruta(id_habitacion):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        exito = database.liberar_habitacion(id_habitacion)
        if exito:
            flash('Habitación liberada exitosamente', 'success')
        else:
            flash('Error al liberar habitación', 'error')
    except Exception as e:
        logger.error(f"Error al liberar habitación: {e}")
        flash('Error al liberar habitación', 'error')
    
    return redirect(url_for('detalle_habitacion_ruta', id_habitacion=id_habitacion))
```

**Características:**
- ✅ Requiere sesión de admin
- ✅ Mensajes flash de éxito/error
- ✅ Redirección al detalle de habitación
- ✅ Manejo de excepciones

---

#### **Archivo: `templates/detalle_habitacion.html` (líneas 90-99)**

**Botón agregado:**
```html
<div class="text-center mt-4">
  <a href="{{ url_for('lista_habitaciones') }}" class="btn btn-secondary">Volver</a>
  
  {% if habitacion.estado != 'disponible' %}
  <form method="POST" action="{{ url_for('liberar_habitacion_ruta', id_habitacion=habitacion.id) }}" 
        style="display: inline;" 
        onsubmit="return confirm('¿Está seguro que desea liberar esta habitación?');">
    <button type="submit" class="btn btn-success">
      <i class="fas fa-unlock"></i> Liberar Habitación
    </button>
  </form>
  {% endif %}
</div>
```

**Características:**
- ✅ Solo se muestra si la habitación NO está disponible
- ✅ Confirmación antes de ejecutar
- ✅ Icono de candado abierto
- ✅ Color verde (success) para indicar acción positiva

---

### **2. Checkboxes para Eliminar del Historial**

#### **Archivo: `database.py` (líneas 1082-1110)**

**Nueva función agregada:**
```python
def eliminar_registros_historial(ids_historial):
    """Elimina uno o varios registros del historial_reservas por sus IDs"""
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        if not ids_historial or len(ids_historial) == 0:
            return False
        
        placeholders = ','.join(['%s'] * len(ids_historial))
        query = f"DELETE FROM historial_reservas WHERE id_historial IN ({placeholders})"
        cursor.execute(query, tuple(ids_historial))
        
        conn.commit()
        logger.info(f"Eliminados {cursor.rowcount} registros del historial")
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"Error al eliminar registros del historial: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

**Características:**
- ✅ Acepta lista de IDs
- ✅ DELETE con IN para múltiples registros
- ✅ Validación de lista vacía
- ✅ Logging del número de registros eliminados
- ✅ Transaccional con rollback

---

#### **Archivo: `app.py` (líneas 592-616)**

**Nueva ruta agregada:**
```python
@app.route('/historial/eliminar', methods=['POST'])
def eliminar_historial():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        # Obtener IDs seleccionados
        ids_str = request.form.getlist('ids_historial')
        ids_historial = [int(id_str) for id_str in ids_str if id_str.isdigit()]
        
        if not ids_historial:
            flash('No se seleccionó ningún registro para eliminar', 'warning')
            return redirect(url_for('historial'))
        
        exito = database.eliminar_registros_historial(ids_historial)
        if exito:
            flash(f'{len(ids_historial)} registro(s) eliminado(s) del historial', 'success')
        else:
            flash('Error al eliminar registros del historial', 'error')
    except Exception as e:
        logger.error(f"Error al eliminar del historial: {e}")
        flash('Error al eliminar registros del historial', 'error')
    
    return redirect(url_for('historial'))
```

**Características:**
- ✅ Obtiene lista de IDs desde formulario
- ✅ Valida que sean números enteros
- ✅ Mensaje específico de cuántos se eliminaron
- ✅ Validación de lista vacía
- ✅ Redirección al historial

---

#### **Archivo: `templates/historial.html` (líneas 55-134)**

**Tabla mejorada con checkboxes:**
```html
<form method="POST" action="{{ url_for('eliminar_historial') }}" id="formEliminar">
  <div class="d-flex justify-content-between align-items-center mb-2">
    <div>
      <input type="checkbox" id="seleccionarTodos" class="form-check-input me-2">
      <label for="seleccionarTodos" class="form-check-label">Seleccionar todos</label>
    </div>
    <button type="submit" class="btn btn-danger btn-sm" 
            onclick="return confirm('¿Está seguro que desea eliminar los registros seleccionados?');">
      <i class="fas fa-trash"></i> Eliminar Seleccionados
    </button>
  </div>

  <div class="table-responsive">
    <table class="table table-striped table-hover align-middle">
      <thead class="table-dark">
        <tr>
          <th style="width: 40px;">
            <input type="checkbox" id="checkAllTable" class="form-check-input">
          </th>
          <th>#</th>
          <th>Cliente</th>
          <!-- ... más columnas ... -->
        </tr>
      </thead>
      <tbody>
        {% for r in registros %}
        <tr>
          <td>
            <input type="checkbox" name="ids_historial" 
                   value="{{ r.id_historial }}" 
                   class="form-check-input checkbox-item">
          </td>
          <td>{{ r.id_historial }}</td>
          <!-- ... más datos ... -->
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</form>
```

**Características:**
- ✅ Checkbox en cada fila
- ✅ Checkbox "Seleccionar todos" (2 ubicaciones)
- ✅ Botón "Eliminar Seleccionados" con icono
- ✅ Confirmación antes de eliminar
- ✅ Formulario envía IDs seleccionados

---

#### **JavaScript para manejo de checkboxes (líneas 176-211)**

```javascript
// Manejar selección de todos los checkboxes
document.getElementById('seleccionarTodos').addEventListener('change', function() {
  const checkboxes = document.querySelectorAll('.checkbox-item');
  checkboxes.forEach(checkbox => {
    checkbox.checked = this.checked;
  });
});

document.getElementById('checkAllTable').addEventListener('change', function() {
  const checkboxes = document.querySelectorAll('.checkbox-item');
  checkboxes.forEach(checkbox => {
    checkbox.checked = this.checked;
  });
  document.getElementById('seleccionarTodos').checked = this.checked;
});

// Sincronizar checkbox "Seleccionar todos" si alguno cambia
document.querySelectorAll('.checkbox-item').forEach(checkbox => {
  checkbox.addEventListener('change', function() {
    const total = document.querySelectorAll('.checkbox-item').length;
    const checked = document.querySelectorAll('.checkbox-item:checked').length;
    document.getElementById('seleccionarTodos').checked = (total === checked);
    document.getElementById('checkAllTable').checked = (total === checked);
  });
});

// Validar que al menos un checkbox esté seleccionado al eliminar
document.getElementById('formEliminar').addEventListener('submit', function(e) {
  const checked = document.querySelectorAll('.checkbox-item:checked').length;
  if (checked === 0) {
    e.preventDefault();
    alert('Debe seleccionar al menos un registro para eliminar');
    return false;
  }
});
```

**Características:**
- ✅ Sincronización entre checkboxes "Seleccionar todos"
- ✅ Actualiza estado de "Seleccionar todos" si se deselecciona alguno
- ✅ Validación de al menos un checkbox seleccionado
- ✅ Previene envío de formulario vacío

---

## 🔄 Flujos de Uso

### **Flujo: Liberar Habitación**

```
1. Admin entra a detalle de habitación → /habitaciones/detalle/10
                        ↓
2. Si habitación NO está disponible, ve botón "Liberar Habitación"
                        ↓
3. Hace clic en el botón → Confirmación
                        ↓
4. POST a /habitaciones/liberar/10
                        ↓
5. database.liberar_habitacion(10)
                        ↓
6. UPDATE habitaciones SET estado='disponible' WHERE id=10
                        ↓
7. Flash: "Habitación liberada exitosamente"
                        ↓
8. Redirección a detalle de habitación (ya muestra "disponible")
```

---

### **Flujo: Eliminar del Historial**

```
1. Admin entra a historial → /historial
                        ↓
2. Ve checkboxes en cada registro
                        ↓
3. Selecciona uno o varios registros (o "Seleccionar todos")
                        ↓
4. Hace clic en "Eliminar Seleccionados" → Confirmación
                        ↓
5. POST a /historial/eliminar con ids_historial=[5, 12, 18]
                        ↓
6. database.eliminar_registros_historial([5, 12, 18])
                        ↓
7. DELETE FROM historial_reservas WHERE id_historial IN (5, 12, 18)
                        ↓
8. Flash: "3 registro(s) eliminado(s) del historial"
                        ↓
9. Redirección a /historial (ya sin los registros eliminados)
```

---

## 📊 Resumen de Mejoras

### **Archivos Modificados:**

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `database.py` | Función eliminar_registros_historial agregada | 1082-1110 |
| `database.py` | Función liberar_habitacion mejorada | 1057-1080 |
| `app.py` | Ruta liberar_habitacion_ruta agregada | 574-590 |
| `app.py` | Ruta eliminar_historial agregada | 592-616 |
| `templates/detalle_habitacion.html` | Botón liberar habitación agregado | 90-99 |
| `templates/historial.html` | Checkboxes y formulario agregado | 55-134 |
| `templates/historial.html` | JavaScript de checkboxes agregado | 176-211 |

---

### **Funcionalidades Nuevas:**

✅ **Liberar Habitación desde Detalle**
- Botón visible solo si habitación NO está disponible
- Confirmación antes de ejecutar
- Actualiza estado a 'disponible'
- Mensajes flash de éxito/error

✅ **Eliminar Registros del Historial**
- Checkboxes en cada fila
- Seleccionar todos (2 checkboxes sincronizados)
- Botón "Eliminar Seleccionados"
- Confirmación antes de eliminar
- Eliminación en lote (múltiples registros)
- Validación de selección vacía
- Mensajes de cuántos se eliminaron

---

## 🔧 Correcciones de Lógica

### **detalle_habitacion_ruta (ya existente)**

La función ya estaba implementada correctamente:
- ✅ Verifica sesión de admin
- ✅ Obtiene habitación por ID
- ✅ Obtiene reserva activa
- ✅ Obtiene datos de cliente
- ✅ Lista acompañantes
- ✅ Lista pagos
- ✅ Calcula total pagado y saldo restante
- ✅ Manejo de excepciones

**No requirió correcciones adicionales** - La lógica estaba bien implementada.

---

## 🎨 Mejoras de UI

### **Detalle de Habitación:**
- Botón "Liberar Habitación" con icono de candado
- Color verde (success) para indicar acción positiva
- Confirmación con diálogo nativo

### **Historial:**
- Checkboxes bien alineados
- Checkbox "Seleccionar todos" en 2 ubicaciones (arriba de la tabla y en el header)
- Botón rojo (danger) para eliminar con icono de basura
- JavaScript interactivo y responsive

---

## ✅ Pruebas Recomendadas

### **Liberar Habitación:**
1. Ir a detalle de una habitación ocupada
2. Verificar que aparece el botón "Liberar Habitación"
3. Hacer clic y confirmar
4. Verificar mensaje de éxito
5. Verificar que el estado cambió a "disponible"
6. Verificar que el botón ya no aparece

### **Eliminar del Historial:**
1. Ir a historial con varios registros
2. Seleccionar checkbox "Seleccionar todos"
3. Verificar que todos se marcan
4. Deseleccionar uno
5. Verificar que "Seleccionar todos" se desmarca
6. Seleccionar 2-3 registros manualmente
7. Hacer clic en "Eliminar Seleccionados"
8. Confirmar eliminación
9. Verificar mensaje de "X registro(s) eliminado(s)"
10. Verificar que ya no aparecen en la lista

---

## 🚀 Uso del Sistema

### **Para Liberar Habitación:**
```
Admin → Lista Habitaciones → Clic en habitación → Detalle
      → Botón "Liberar Habitación" → Confirmar → ✅ Liberada
```

### **Para Eliminar del Historial:**
```
Admin → Historial → Marcar checkboxes → "Eliminar Seleccionados"
      → Confirmar → ✅ Registros eliminados
```

---

## 📝 Notas Técnicas

### **Seguridad:**
- ✅ Todas las rutas requieren sesión de admin
- ✅ Validación de datos en backend
- ✅ Confirmaciones en frontend
- ✅ Manejo de errores con rollback

### **Rendimiento:**
- ✅ Eliminación en lote (un solo query para múltiples registros)
- ✅ Queries optimizados
- ✅ Cierre apropiado de conexiones

### **UX:**
- ✅ Confirmaciones para acciones destructivas
- ✅ Mensajes claros de éxito/error
- ✅ Redirecciones lógicas
- ✅ Interfaz intuitiva

---

**Desarrollado por**: Sistema de Gestión Hotelera  
**Última actualización**: 8 de Noviembre de 2025 - 11:15 AM
