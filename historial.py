import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import database

class ModuloHistorial(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.color_primario = ["#FFCD39", "#ffc107"]
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.texto_busqueda = tk.StringVar()
        self.datos_historial = []

        # Diccionario para mapear los meses al formato numérico de base de datos
        self.meses_dicc = {
            "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
            "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
            "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
        }

        # Título Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Historial de Ingresos", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(10, 20), anchor="center")

        # Barra de selección de mes y búsqueda histórica
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(fill="x", padx=20, pady=5)

        self.lbl_select = ctk.CTkLabel(self.frame_filtros, text="Seleccionar Mes:", font=ctk.CTkFont(size=14))
        self.lbl_select.pack(side="left", padx=5)

        # Menú desplegable para los meses
        self.combo_mes = ctk.CTkOptionMenu(
            self.frame_filtros, 
            values=list(self.meses_dicc.keys()),
            fg_color="gray30",
            button_color="gray40",
            button_hover_color="gray50"
        )
        self.combo_mes.pack(side="left", padx=5)
        # Selecciona por defecto el nombre del mes actual
        mes_letras = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.combo_mes.set(mes_letras[int(datetime.today().strftime('%m')) - 1])

        self.btn_buscar = ctk.CTkButton(
            self.frame_filtros, 
            text="Buscar", 
            fg_color=self.color_primario, 
            text_color="black", 
            hover_color=self.color_primario, 
            width=90, 
            command=self.cargar_datos_mes
        )
        self.btn_buscar.pack(side="left", padx=5)

        # Buscador por descripción en la zona superior derecha
        self.entry_buscar = ctk.CTkEntry(self.frame_filtros, placeholder_text="Buscar por descripcion", width=200)
        self.entry_buscar.pack(side="right", padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.detectar_busqueda())

        # Contenedor para los resultados de la tabla
        self.frame_tabla_contenedor = ctk.CTkFrame(self)
        self.frame_tabla_contenedor.pack(fill="both", expand=True, padx=20, pady=10)

        # Cargamos los datos inicialmente
        self.cargar_datos_mes()

    def cargar_datos_mes(self):
        """Busca en SQLite los registros según el mes seleccionado y el año actual del sistema"""
        mes_seleccionado = self.combo_mes.get()
        codigo_mes = self.meses_dicc[mes_seleccionado]
        
        # Al extraer el '%Y' dinámico, si estás en el 2027, buscará el mes elegido pero del 2027.
        # Evitando por completo mezclar registros del año viejo (2026).
        anio_actual = datetime.today().strftime('%Y')
        
        # Consultamos a la base de datos con ambos filtros bien definidos
        self.datos_historial = database.obtener_ingresos_por_mes_anio(codigo_mes, anio_actual)
        self.pagina_actual = 1
        self.actualizar_tabla()

    def detectar_busqueda(self):
        self.texto_busqueda.set(self.entry_buscar.get())
        self.pagina_actual = 1
        self.actualizar_tabla()

    def obtener_datos_filtrados(self):
        busqueda = self.texto_busqueda.get().lower().strip()
        if not busqueda:
            return self.datos_historial
        return [i for i in self.datos_historial if busqueda in i["descripcion"].lower()]

    def actualizar_tabla(self):
        for widget in self.frame_tabla_contenedor.winfo_children():
            widget.destroy()

        datos_filtrados = self.obtener_datos_filtrados()
        total_registros = len(datos_filtrados)
        total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)

        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas

        inicio_idx = (self.pagina_actual - 1) * self.registros_por_pagina
        datos_pagina = datos_filtrados[inicio_idx:inicio_idx + self.registros_por_pagina]

        # Cabeceras
        headers = ["Fecha", "Descripción", "Importe"]
        frame_headers = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray20", height=35)
        frame_headers.pack(fill="x", side="top")
        frame_headers.pack_propagate(False)

        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(frame_headers, text=h, font=ctk.CTkFont(weight="bold"), anchor="w" if i != 2 else "e")
            lbl.place(relx=0.05 if i==0 else (0.35 if i==1 else 0.75), rely=0.5, anchor="w" if i != 2 else "e", relwidth=0.25 if i!=1 else 0.35)

        # Filas del historial
        for item in datos_pagina:
            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=35, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)

            lbl_f = ctk.CTkLabel(fila, text=item["fecha"], anchor="w")
            lbl_f.place(relx=0.05, rely=0.5, anchor="w")

            lbl_d = ctk.CTkLabel(fila, text=item["descripcion"], anchor="w")
            lbl_d.place(relx=0.35, rely=0.5, anchor="w")

            lbl_i = ctk.CTkLabel(fila, text=f"$ {item['importe']:.2f}", anchor="e")
            lbl_i.place(relx=0.95, rely=0.5, anchor="e")

        # Fila del Total Histórico Calculado
        suma_total = sum(item["importe"] for item in datos_filtrados)
        frame_total = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_total.pack(fill="x", side="top", pady=(10, 0))

        lbl_total_txt = ctk.CTkLabel(frame_total, text=f"TOTAL {self.combo_mes.get().upper()}:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_total_txt.place(relx=0.35, rely=0.5, anchor="w")

        lbl_total_num = ctk.CTkLabel(frame_total, text=f"$ {suma_total:.2f}", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.color_primario[0])
        lbl_total_num.place(relx=0.95, rely=0.5, anchor="e")

        # Barra de Paginación
        frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_paginacion.pack(fill="x", side="bottom")

        btn_ant = ctk.CTkButton(frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_primario, text_color="black", hover_color=self.color_primario, state="normal" if self.pagina_actual > 1 else "disabled", command=self.pagina_anterior)
        btn_ant.place(relx=0.4, rely=0.5, anchor="e")

        lbl_paginas = ctk.CTkLabel(frame_paginacion, text=f"Página {self.pagina_actual} de {total_paginas}")
        lbl_paginas.place(relx=0.5, rely=0.5, anchor="center")

        btn_sig = ctk.CTkButton(frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_primario, text_color="black", hover_color=self.color_primario, state="normal" if self.pagina_actual < total_paginas else "disabled", command=self.pagina_siguiente)
        btn_sig.place(relx=0.6, rely=0.5, anchor="w")

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        if self.pagina_actual < len(self.obtener_datos_filtrados()) // self.registros_por_pagina + 1:
            self.pagina_actual += 1
            self.actualizar_tabla()