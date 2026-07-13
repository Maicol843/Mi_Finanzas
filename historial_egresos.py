import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import database

class VistaHistorialEgresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.color_gastos = ["#FFCD39", "#ffc107"]
        
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.datos_totales_mes = []
        
        # Mapeo de meses en español al formato numérico de base de datos
        self.meses_dic = {
            "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
            "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
            "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
        }

        # Título Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Historial de Gastos", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(5, 15), anchor="center")

        # Barra de Filtros Superiores (Select Mes + Botón Buscar + Buscador por Descripción)
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.frame_filtros, text="Mes:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        self.combo_mes = ctk.CTkOptionMenu(
            self.frame_filtros,
            values=list(self.meses_dic.keys()),
            width=130,
            fg_color="gray30",
            button_color="gray40"
        )
        # Establecer por defecto el mes actual del sistema operativo
        mes_nombre_actual = list(self.meses_dic.keys())[int(datetime.today().strftime('%m')) - 1]
        self.combo_mes.set(mes_nombre_actual)
        self.combo_mes.pack(side="left", padx=5)

        self.btn_buscar = ctk.CTkButton(self.frame_filtros, text="Buscar", fg_color=self.color_gastos, text_color="black", hover_color=self.color_gastos, width=90, command=self.ejecutar_busqueda_mes)
        self.btn_buscar.pack(side="left", padx=5)

        # Buscador por descripción en la parte superior derecha de la tabla
        self.entry_buscar_desc = ctk.CTkEntry(self.frame_filtros, placeholder_text="Filtrar por descripción...", width=200)
        self.entry_buscar_desc.pack(side="right", padx=5)
        self.entry_buscar_desc.bind("<KeyRelease>", lambda event: self.filtrar_por_descripcion())

        # Contenedor dinámico de la Tabla
        self.frame_tabla_contenedor = ctk.CTkFrame(self)
        self.frame_tabla_contenedor.pack(fill="both", expand=True, padx=20, pady=10)

        # Cargar datos inicialmente
        self.ejecutar_busqueda_mes()

    def ejecutar_busqueda_mes(self):
        """Obtiene de la base de datos todos los egresos del mes seleccionado"""
        mes_seleccionado = self.combo_mes.get()
        num_mes = self.meses_dic[mes_seleccionado]
        anio_actual = datetime.today().strftime('%Y')
        
        # Realiza la consulta directa a SQLite
        self.datos_totales_mes = database.obtener_egresos_mes_actual(num_mes, anio_actual)
        self.pagina_actual = 1
        self.actualizar_tabla_historial()

    def filtrar_por_descripcion(self):
        self.pagina_actual = 1
        self.actualizar_tabla_historial()

    def obtener_datos_finales(self):
        busqueda = self.entry_buscar_desc.get().lower().strip()
        if not busqueda:
            return self.datos_totales_mes
        return [e for e in self.datos_totales_mes if busqueda in e["descripcion"].lower()]

    def actualizar_tabla_historial(self):
        for widget in self.frame_tabla_contenedor.winfo_children():
            widget.destroy()

        datos_filtrados = self.obtener_datos_finales()
        total_registros = len(datos_filtrados)
        total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)

        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas

        inicio_idx = (self.pagina_actual - 1) * self.registros_por_pagina
        datos_pagina = datos_filtrados[inicio_idx:inicio_idx + self.registros_por_pagina]

        # Cabeceras Estables de la Tabla Histórica
        headers = ["Fecha", "Descripción", "Categoría", "Importe"]
        frame_headers = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray20", height=35)
        frame_headers.pack(fill="x", side="top")
        frame_headers.pack_propagate(False)

        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(frame_headers, text=h, font=ctk.CTkFont(weight="bold"), anchor="w" if i != 3 else "e")
            lbl.place(
                relx=0.05 if i==0 else (0.25 if i==1 else (0.55 if i==2 else 0.85)), 
                rely=0.5, 
                anchor="w" if i != 3 else "e", 
                relwidth=0.18 if i==0 else (0.28 if i==1 else (0.22 if i==2 else 0.15))
            )

        # Filas de Datos Históricos
        for item in datos_pagina:
            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=35, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)

            ctk.CTkLabel(fila, text=item["fecha"], anchor="w").place(relx=0.05, rely=0.5, anchor="w")
            ctk.CTkLabel(fila, text=item["descripcion"], anchor="w").place(relx=0.28, rely=0.5, anchor="w")
            ctk.CTkLabel(fila, text=item["categoria"], anchor="w").place(relx=0.55, rely=0.5, anchor="w")
            ctk.CTkLabel(fila, text=f"$ {item['importe']:.2f}", anchor="e").place(relx=0.93, rely=0.5, anchor="e")

        # Fila de Totales Acumulados (Parte baja de la tabla)
        suma_total = sum(item["importe"] for item in datos_filtrados)
        frame_total = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_total.pack(fill="x", side="top", pady=(10, 0))

        lbl_total_txt = ctk.CTkLabel(frame_total, text="TOTAL GASTOS DEL MES:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_total_txt.place(relx=0.55, rely=0.5, anchor="w")

        lbl_total_num = ctk.CTkLabel(frame_total, text=f"$ {suma_total:.2f}", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.color_gastos[0])
        lbl_total_num.place(relx=0.93, rely=0.5, anchor="e")

        # Paginación Inferior (Hasta 10 elementos por página)
        frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_paginacion.pack(fill="x", side="bottom")

        btn_ant = ctk.CTkButton(frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_gastos, text_color="white", hover_color=self.color_gastos, state="normal" if self.pagina_actual > 1 else "disabled", command=self.pagina_anterior)
        btn_ant.place(relx=0.4, rely=0.5, anchor="e")

        lbl_paginas = ctk.CTkLabel(frame_paginacion, text=f"Página {self.pagina_actual} de {total_paginas}")
        lbl_paginas.place(relx=0.5, rely=0.5, anchor="center")

        btn_sig = ctk.CTkButton(frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_gastos, text_color="white", hover_color=self.color_gastos, state="normal" if self.pagina_actual < total_paginas else "disabled", command=self.pagina_siguiente)
        btn_sig.place(relx=0.6, rely=0.5, anchor="w")

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla_historial()

    def pagina_siguiente(self):
        datos_f = self.obtener_datos_finales()
        if self.pagina_actual < (len(datos_f) + self.registros_por_pagina - 1) // self.registros_por_pagina:
            self.pagina_actual += 1
            self.actualizar_tabla_historial()