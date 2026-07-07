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
    Retorna los datos calculados de los ahorros: nombre, meta, inicial, 
    y el total ahorrado acumulando dinámicamente los depósitos.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Realizamos un LEFT JOIN agrupado por ID para sumar todos los depósitos
    # individuales al importe inicial configurado por la meta.
    cursor.execute("""
        SELECT 
            m.id, 
            m.nombre, 
            m.meta, 
            m.inicial,
            (m.inicial + COALESCE(SUM(d.importe), 0)) AS total_ahorrado
        FROM metas_ahorro m
        LEFT JOIN depositos_ahorro d ON m.nombre = d.tipo_ahorro
        GROUP BY m.id
        ORDER BY m.id DESC
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

# Inicializamos la base de datos al importar el script
crear_tablas()