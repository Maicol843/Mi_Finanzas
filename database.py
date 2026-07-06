import sqlite3

def conectar():
    """Establece conexión con la base de datos local finanzas.db"""
    return sqlite3.connect("finanzas.db")

def crear_tablas():
    """Crea las tablas de ingresos y egresos si no existen"""
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
    
    # TABLA DE EGRESOS (Faltaba añadir esta sección)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT NOT NULL,
            importe REAL NOT NULL
        )
    """)
    
    conexion.commit()
    conexion.close()

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
    # En DD-MM-AAAA: 
    # El mes empieza en el caracter 4 y dura 2 posiciones (substr(fecha, 4, 2))
    # El año empieza en el caracter 7 y dura 4 posiciones (substr(fecha, 7, 4))
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
    # Extraemos el mes (pos 4, long 2) y el año (pos 7, long 4) de la fecha 'DD-MM-AAAA'
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
    
    # Retorna una lista de tuplas, ej: [('2026-05', 450.0), ('2026-06', 1970.5)]
    return resultado

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
    # Busca fechas que terminen con el formato '-MM-AAAA'
    patron_fecha = f"%-{mes}-{anio}"
    cursor.execute("SELECT id, fecha, descripcion, categoria, importe FROM egresos WHERE fecha LIKE ?", (patron_fecha,))
    filas = cursor.fetchall()
    conexion.close()
    
    # Mapea a un diccionario legible por la tabla
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

# Inicializamos la base de datos al importar el script
crear_tablas()