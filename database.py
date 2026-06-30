import sqlite3

def conectar():
    """Establece conexión con la base de datos local finanzas.db"""
    return sqlite3.connect("finanzas.db")

def crear_tablas():
    """Crea la tabla de ingresos si no existe"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
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

# Inicializamos la base de datos al importar el script
crear_tablas()