import sqlite3

def conectar():
    """Establece conexión con la base de datos local finanzas.db"""
    return sqlite3.connect("finanzas.db")

def crear_tablas():
    """Crea las tablas de ingresos, egresos y ahorros si no existen"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Tabla de Ingresos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            importe REAL NOT NULL
        )
    """)
    
    # TABLA DE EGRESOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT NOT NULL,
            importe REAL NOT NULL
        )
    """)
    
    # NUEVA TABLA: Metas globales de ahorro
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas_ahorro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            meta REAL NOT NULL,
            inicial REAL NOT NULL
        )
    """)
    
    # NUEVA TABLA: Historial de transacciones/depósitos a los ahorros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS depositos_ahorro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            tipo_ahorro TEXT NOT NULL,
            importe REAL NOT NULL,
            FOREIGN KEY (tipo_ahorro) REFERENCES metas_ahorro(nombre)
        )
    """)
    
    conexion.commit()
    conexion.close()

# =====================================================================
# MÓDULO DE INGRESOS
# =====================================================================

def insertar_ingreso(fecha, descripcion, importe):
    """Inserta un nuevo registro de ingreso"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO ingresos (fecha, descripcion, importe) VALUES (?, ?, ?)",
        (fecha, descripcion, importe)
    )
    conexion.commit()
    conexion.close()

def obtener_ingresos():
    """Trae todos los ingresos ordenados por ID de forma descendente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, fecha, descripcion, importe FROM ingresos ORDER BY id DESC")
    columnas = [column[0] for column in cursor.description]
    resultado = []
    for fila in cursor.fetchall():
        resultado.append(dict(zip(columnas, fila)))
    conexion.close()
    return resultado

def actualizar_ingreso(id_ingreso, fecha, descripcion, importe):
    """Actualiza un registro existente mediante su ID"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE ingresos SET fecha = ?, descripcion = ?, importe = ? WHERE id = ?",
        (fecha, descripcion, importe, id_ingreso)
    )
    conexion.commit()
    conexion.close()

def eliminar_ingreso_db(id_ingreso):
    """Elimina permanentemente un registro de la base de datos"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM ingresos WHERE id = ?", (id_ingreso,))
    conexion.commit()
    conexion.close()

def obtener_ingresos_por_mes_anio(mes, anio):
    """Trae los ingresos filtrados por un mes y año específicos (Formato de fecha: DD-MM-AAAA)"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, fecha, descripcion, importe 
        FROM ingresos 
        WHERE substr(fecha, 4, 2) = ? AND substr(fecha, 7, 4) = ?
        ORDER BY id DESC
    """, (mes, anio))
    columnas = [column[0] for column in cursor.description]
    resultado = []
    for fila in cursor.fetchall():
        resultado.append(dict(zip(columnas, fila)))
    conexion.close()
    return resultado

def obtener_totales_por_mes():
    """Trae la suma de ingresos agrupada por mes y año para la gráfica"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 
            substr(fecha, 7, 4) || '-' || substr(fecha, 4, 2) AS anio_mes,
            SUM(importe) AS total
        FROM ingresos
        GROUP BY anio_mes
        ORDER BY anio_mes ASC
    """)
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

# =====================================================================
# MÓDULO DE EGRESOS
# =====================================================================

def insertar_egreso(fecha, descripcion, categoria, importe):
    """Inserta un nuevo gasto en la base de datos"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO egresos (fecha, descripcion, categoria, importe)
        VALUES (?, ?, ?, ?)
    """, (fecha, descripcion, categoria, importe))
    conexion.commit()
    conexion.close()

def obtener_egresos_mes_actual(mes, anio):
    conexion = conectar()
    cursor = conexion.cursor()
    patron_fecha = f"%-{mes}-{anio}"
    cursor.execute("SELECT id, fecha, descripcion, categoria, importe FROM egresos WHERE fecha LIKE ?", (patron_fecha,))
    filas = cursor.fetchall()
    conexion.close()
    
    egresos = []
    for f in filas:
        egresos.append({
            "id": f[0],
            "fecha": f[1],
            "descripcion": f[2],
            "categoria": f[3],
            "importe": f[4]
        })
    return egresos

def actualizar_egreso(id_egreso, fecha, descripcion, categoria, importe):
    """Modifica un egreso existente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE egresos 
        SET fecha = ?, descripcion = ?, categoria = ?, importe = ?
        WHERE id = ?
    """, (fecha, descripcion, categoria, importe, id_egreso))
    conexion.commit()
    conexion.close()

def eliminar_egreso_db(id_egreso):
    """Elimina permanentemente un egreso"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM egresos WHERE id = ?", (id_egreso,))
    conexion.commit()
    conexion.close()

# =====================================================================
# MÓDULO DE AHORROS
# =====================================================================

def insertar_meta_ahorro(nombre, meta, inicial):
    """Guarda un nuevo objetivo/meta de ahorro en la base de datos"""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO metas_ahorro (nombre, meta, inicial)
            VALUES (?, ?, ?)
        """, (nombre, meta, inicial))
        conexion.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Ya existe una meta de ahorro con este nombre.")
    finally:
        conexion.close()

def insertar_deposito_ahorro(fecha, tipo_ahorro, importe):
    """Registra una transacción o aporte mensual a un ahorro existente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO depositos_ahorro (fecha, tipo_ahorro, importe)
        VALUES (?, ?, ?)
    """, (fecha, tipo_ahorro, importe))
    conexion.commit()
    conexion.close()

def obtener_metas_ahorro():
    """
    Retorna los datos sumando el Importe Inicial fijo de la meta 
    más todos los depósitos extras registrados en el historial.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Aquí hacemos la lógica matemática exacta: Inicial + Suma de depósitos posteriores
    cursor.execute("""
        SELECT 
            m.id, 
            m.nombre, 
            m.meta, 
            m.inicial,
            COALESCE(SUM(d.importe), 0) AS total_ahorrado
        FROM metas_ahorro m
        LEFT JOIN depositos_ahorro d ON m.nombre = d.tipo_ahorro
        GROUP BY m.id, m.nombre, m.meta, m.inicial
    """)
    
    filas = cursor.fetchall()
    conexion.close()
    
    resultado = []
    for f in filas:
        resultado.append({
            "id": f[0],
            "nombre": f[1],
            "meta": f[2],
            "inicial": f[3],
            "total_ahorrado": f[4]
        })
    return resultado

def obtener_historial_depositos():
    """Trae todos los registros de aportes/depósitos de ahorros ordenados por ID descendente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, fecha, tipo_ahorro, importe FROM depositos_ahorro ORDER BY id DESC")
    filas = cursor.fetchall()
    conexion.close()
    
    resultado = []
    for f in filas:
        resultado.append({
            "id": f[0],
            "fecha": f[1],
            "tipo_ahorro": f[2],
            "importe": f[3]
        })
    return resultado

def actualizar_meta_ahorro(id_ahorro, nuevo_nombre, nueva_meta, nuevo_inicial, nombre_anterior):
    """Actualiza la meta de ahorro global y renombra en cascada las transacciones del historial."""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        # Actualizamos la meta
        cursor.execute(
            "UPDATE metas_ahorro SET nombre = ?, meta = ?, inicial = ? WHERE id = ?",
            (nuevo_nombre, nueva_meta, nuevo_inicial, id_ahorro)
        )
        # Cambiamos las referencias del historial asociadas al nombre viejo
        cursor.execute(
            "UPDATE depositos_ahorro SET tipo_ahorro = ? WHERE tipo_ahorro = ?",
            (nuevo_nombre, nombre_anterior)
        )
        conexion.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Ya existe otra meta de ahorro con ese nombre.")
    finally:
        conexion.close()

def eliminar_meta_ahorro_db(id_ahorro, nombre_ahorro):
    """Elimina la meta global y borra en cascada todas las transacciones vinculadas."""
    conexion = conectar()
    cursor = conexion.cursor()
    # Borrar los depósitos del historial de ese tipo
    cursor.execute("DELETE FROM depositos_ahorro WHERE tipo_ahorro = ?", (nombre_ahorro,))
    # Borrar la meta global
    cursor.execute("DELETE FROM metas_ahorro WHERE id = ?", (id_ahorro,))
    conexion.commit()
    conexion.close()

# Inicializamos la base de datos al importar el script
crear_tablas()

def actualizar_deposito_ahorro(id_deposito, nueva_fecha, nuevo_tipo, nuevo_importe):
    """Actualiza un registro del historial. Si es el depósito inicial, actualiza también la meta global."""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # 1. Obtener los datos actuales antes de modificar
    cursor.execute("SELECT tipo_ahorro, importe FROM depositos_ahorro WHERE id = ?", (id_deposito,))
    fila = cursor.fetchone()
    
    if fila:
        tipo_ahorro_antiguo, importe_antiguo = fila
        
        # 2. Verificar si este registro corresponde al inicial de la meta global
        cursor.execute("SELECT id, inicial FROM metas_ahorro WHERE nombre = ?", (tipo_ahorro_antiguo,))
        meta = cursor.fetchone()
        
        if meta and meta[1] == importe_antiguo:
            # Comprobar si es el registro más antiguo (el primero insertado)
            cursor.execute("""
                SELECT id FROM depositos_ahorro 
                WHERE tipo_ahorro = ? 
                ORDER BY id ASC LIMIT 1
            """, (tipo_ahorro_antiguo,))
            primer_registro = cursor.fetchone()
            
            # Si efectivamente es el registro inicial, actualizamos también la meta global
            if primer_registro and primer_registro[0] == id_deposito:
                # Si el usuario cambió el nombre de la meta en el combo, buscamos la nueva meta destino
                cursor.execute("SELECT id FROM metas_ahorro WHERE nombre = ?", (nuevo_tipo,))
                nueva_meta = cursor.fetchone()
                if nueva_meta:
                    # Devolvemos a 0 la meta anterior y pasamos el valor inicial a la nueva
                    cursor.execute("UPDATE metas_ahorro SET inicial = 0.0 WHERE id = ?", (meta[0],))
                    cursor.execute("UPDATE metas_ahorro SET inicial = ? WHERE id = ?", (nuevo_importe, nueva_meta[0]))
                else:
                    # Si mantiene la misma meta, solo actualizamos el monto inicial
                    cursor.execute("UPDATE metas_ahorro SET inicial = ? WHERE id = ?", (nuevo_importe, meta[0]))

    # 3. Realizar la actualización normal en el historial
    cursor.execute("""
        UPDATE depositos_ahorro 
        SET fecha = ?, tipo_ahorro = ?, importe = ? 
        WHERE id = ?
    """, (nueva_fecha, nuevo_tipo, nuevo_importe, id_deposito))
    
    conexion.commit()
    conexion.close()

def eliminar_deposito_ahorro_db(id_deposito):
    """
    Verifica si el registro es el importe inicial. 
    Si lo es, cancela la operación y devuelve False. 
    Si no lo es, lo elimina y devuelve True.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener el tipo de ahorro e importe del registro que se quiere borrar
    cursor.execute("SELECT tipo_ahorro, importe FROM depositos_ahorro WHERE id = ?", (id_deposito,))
    fila = cursor.fetchone()
    
    if fila:
        tipo_ahorro, importe_borrado = fila
        
        # Verificar la meta global asociada
        cursor.execute("SELECT inicial FROM metas_ahorro WHERE nombre = ?", (tipo_ahorro,))
        meta = cursor.fetchone()
        
        if meta and meta[0] == importe_borrado:
            # Comprobar si es el primer registro insertado (el más antiguo) para esa meta
            cursor.execute("""
                SELECT id FROM depositos_ahorro 
                WHERE tipo_ahorro = ? 
                ORDER BY id ASC LIMIT 1
            """, (tipo_ahorro,))
            primer_registro = cursor.fetchone()
            
            # SI COINCIDE, ES EL INICIAL. CANCELAMOS EL BORRADO.
            if primer_registro and primer_registro[0] == id_deposito:
                conexion.close()
                return False

    # Si no es el inicial, procedemos a borrarlo normalmente
    cursor.execute("DELETE FROM depositos_ahorro WHERE id = ?", (id_deposito,))
    conexion.commit()
    conexion.close()
    return True

# =====================================================================
# MÓDULO DE DEUDAS
# =====================================================================

def crear_tablas_deudas():
    """Crea las tablas de deudas y pagos si no existen"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deudas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            total REAL NOT NULL,
            pago_mensual REAL NOT NULL,
            interes REAL NOT NULL,
            meses_a_pagar INTEGER NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos_deudas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            nombre_deuda TEXT NOT NULL,
            importe REAL NOT NULL,
            FOREIGN KEY (nombre_deuda) REFERENCES deudas(nombre)
        )
    """)
    conexion.commit()
    conexion.close()

# Inicializamos las tablas de deudas de forma automática
crear_tablas_deudas()

def insertar_deuda(nombre, total, pago_mensual, interes, meses_a_pagar):
    """Inserta una nueva obligación o préstamo"""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO deudas (nombre, total, pago_mensual, interes, meses_a_pagar)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, total, pago_mensual, interes, meses_a_pagar))
        conexion.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Ya existe una deuda registrada con este nombre.")
    finally:
        conexion.close()

def obtener_deudas_con_pagos():
    """Trae todas las deudas calculando cuántos meses se han pagado dinámicamente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 
            d.id, 
            d.nombre, 
            d.total, 
            d.pago_mensual, 
            d.interes, 
            d.meses_a_pagar,
            COALESCE(COUNT(p.id), 0) AS meses_pagados
        FROM deudas d
        LEFT JOIN pagos_deudas p ON d.nombre = p.nombre_deuda
        GROUP BY d.id, d.nombre, d.total, d.pago_mensual, d.interes, d.meses_a_pagar
        ORDER BY d.id DESC
    """)
    filas = cursor.fetchall()
    conexion.close()
    
    resultado = []
    for f in filas:
        resultado.append({
            "id": f[0],
            "nombre": f[1],
            "total": f[2],
            "pago_mensual": f[3],
            "interes": f[4],
            "meses_a_pagar": f[5],
            "meses_pagados": f[6]
        })
    return resultado

def actualizar_deuda_db(id_deuda, nuevo_nombre, nuevo_total, nuevo_pago, nuevo_interes, nuevos_meses, nombre_anterior):
    """Actualiza los parámetros de una deuda y migra sus registros de pagos en cascada"""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            UPDATE deudas 
            SET nombre = ?, total = ?, pago_mensual = ?, interes = ?, meses_a_pagar = ? 
            WHERE id = ?
        """, (nuevo_nombre, nuevo_total, nuevo_pago, nuevo_interes, nuevos_meses, id_deuda))
        
        cursor.execute("UPDATE pagos_deudas SET nombre_deuda = ? WHERE nombre_deuda = ?", (nuevo_nombre, nombre_anterior))
        conexion.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Ya existe otra deuda con ese nombre.")
    finally:
        conexion.close()

def eliminar_deuda_db(id_deuda, nombre_deuda):
    """Elimina la deuda y su historial completo de pagos"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM pagos_deudas WHERE nombre_deuda = ?", (nombre_deuda,))
    cursor.execute("DELETE FROM deudas WHERE id = ?", (id_deuda,))
    conexion.commit()
    conexion.close()

def registrar_pago_deuda_db(fecha, nombre_deuda, importe):
    """Registra el pago mensual de una cuota"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO pagos_deudas (fecha, nombre_deuda, importe)
        VALUES (?, ?, ?)
    """, (fecha, nombre_deuda, importe))
    conexion.commit()
    conexion.close()

def obtener_historial_pagos():
    """Trae todos los registros de pagos de deudas ordenados por ID descendente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, fecha, nombre_deuda, importe FROM pagos_deudas ORDER BY id DESC")
    filas = cursor.fetchall()
    conexion.close()
    
    resultado = []
    for f in filas:
        resultado.append({
            "id": f[0],
            "fecha": f[1],
            "tipo_deuda": f[2],  # Lo mapeamos como 'tipo_deuda' para que coincida con tu vista externa
            "importe": f[3]
        })
    return resultado

def actualizar_fecha_pago_db(id_pago, nueva_fecha):
    """Actualiza únicamente la fecha de un registro de pago de deuda mediante su ID"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE pagos_deudas SET fecha = ? WHERE id = ?",
        (nueva_fecha, id_pago)
    )
    conexion.commit()
    conexion.close()

def eliminar_pago_deuda_db(id_pago):
    """Elimina permanentemente un registro de pago de deuda mediante su ID"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM pagos_deudas WHERE id = ?", (id_pago,))
    conexion.commit()
    conexion.close()