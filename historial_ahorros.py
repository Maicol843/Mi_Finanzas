import tkinter as tk
import customtkinter as ctk
import database

class ModuloHistorialAhorros(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent
        self.color_ahorros = ["#4CAF50", "#45a049"] # Verde principal y verde hover
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        
        # Diccionario para convertir nombres de meses a números de dos dígitos
        self.meses_dict = {
            "Todos": "Todos", "Enero": "01", "Febrero": "02", "Marzo": "03", 
            "Abril": "04", "Mayo": "05", "Junio": "06", "Julio": "07", 
            "Agosto": "08", "Septiembre": "09", "Octubre": "10", 
            "Noviembre": "11", "Diciembre": "12"
        }

        # Inicializamos las variables en "Todos" para mostrar absolutamente todo al cargar la vista
        self.filtro_tipo = tk.StringVar(value="Todos")
        self.filtro_mes = tk.StringVar(value="Todos")

        # Título Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Historial de Ahorros", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(15, 20), anchor="center")

        # CONTENEDOR DE FILTROS (Arriba de la tabla)
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(fill="x", padx=20, pady=5)
        
        # Botón Buscar (Alineado a la derecha)
        self.btn_buscar = ctk.CTkButton(self.frame_filtros, text="Buscar", fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], width=90, command=self.ejecutar_busqueda)
        self.btn_buscar.pack(side="right", padx=(5, 0))

        # Selector de Meses (CAMBIADO A COLOR VERDE)
        opciones_meses = list(self.meses_dict.keys())
        self.combo_mes = ctk.CTkOptionMenu(
            self.frame_filtros, 
            values=opciones_meses, 
            variable=self.filtro_mes, 
            width=120,
            fg_color=self.color_ahorros[0],         # Fondo verde igual al de Buscar
            button_color=self.color_ahorros[0],     # Flecha del mismo verde
            button_hover_color=self.color_ahorros[1]# Tonalidad hover correspondiente
        )
        self.combo_mes.pack(side="right", padx=5)
        self.combo_mes.set("Todos") 
        
        self.lbl_mes = ctk.CTkLabel(self.frame_filtros, text="Mes:")
        self.lbl_mes.pack(side="right", padx=(10, 2))

        # Selector de Tipo de Ahorro (CAMBIADO A COLOR VERDE)
        try:
            metas = database.obtener_metas_ahorro()
            opciones_tipo = ["Todos"] + [m["nombre"] for m in metas]
        except Exception:
            opciones_tipo = ["Todos"]

        self.combo_tipo = ctk.CTkOptionMenu(
            self.frame_filtros, 
            values=opciones_tipo, 
            variable=self.filtro_tipo, 
            width=140,
            fg_color=self.color_ahorros[0],         # Fondo verde igual al de Buscar
            button_color=self.color_ahorros[0],     # Flecha del mismo verde
            button_hover_color=self.color_ahorros[1]# Tonalidad hover correspondiente
        )
        self.combo_tipo.pack(side="right", padx=5)
        self.combo_tipo.set("Todos") 
        
        self.lbl_tipo = ctk.CTkLabel(self.frame_filtros, text="Ahorro:")
        self.lbl_tipo.pack(side="right", padx=(10, 2))

        # Contenedor para la tabla de historial
        self.frame_tabla_contenedor = ctk.CTkFrame(self)
        self.frame_tabla_contenedor.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.actualizar_tabla()

    def ejecutar_busqueda(self):
        """Aplica los filtros únicamente cuando haces clic en Buscar"""
        self.pagina_actual = 1
        self.actualizar_tabla()

    def obtener_datos_filtrados(self):
        try:
            todos_los_depositos = database.obtener_historial_depositos()
        except Exception:
            todos_los_depositos = []

        tipo_sel = self.filtro_tipo.get()
        mes_nombre_sel = self.filtro_mes.get()
        mes_num_sel = self.meses_dict[mes_nombre_sel]

        resultado = []
        for d in todos_los_depositos:
            # Filtro por tipo/nombre de ahorro
            if tipo_sel != "Todos" and d["tipo_ahorro"] != tipo_sel:
                continue
            
            # Filtro por mes (extrayendo el número desde la fecha DD-MM-AAAA o D-M-AAAA)
            if mes_num_sel != "Todos":
                try:
                    partes_fecha = d["fecha"].split("-")
                    mes_registro = partes_fecha[1].zfill(2) 
                    if mes_registro != mes_num_sel:
                        continue
                except IndexError:
                    continue
                    
            resultado.append(d)
            
        return resultado

    def actualizar_tabla(self):
        for widget in self.frame_tabla_contenedor.winfo_children():
            widget.destroy()
            
        datos_filtrados = self.obtener_datos_filtrados()
        total_registros = len(datos_filtrados)
        total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)
        
        # NUEVO: Calcular la suma total acumulada de los registros que coinciden con la búsqueda actual
        suma_total_importe = sum(float(item["importe"]) for item in datos_filtrados)
        
        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas
            
        inicio_idx = (self.pagina_actual - 1) * self.registros_por_pagina
        datos_pagina = datos_filtrados[inicio_idx:inicio_idx + self.registros_por_pagina]

        # Cabeceras de la Tabla de Historial
        headers = ["Fecha", "Tipo de Ahorro", "Importe"]
        frame_headers = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray20", height=35)
        frame_headers.pack(fill="x", side="top")
        frame_headers.pack_propagate(False)
        
        for i, h in enumerate(headers):
            anchor_lbl = "w" if i < 2 else "e"
            lbl = ctk.CTkLabel(frame_headers, text=h, font=ctk.CTkFont(weight="bold"), anchor=anchor_lbl)
            lbl.place(
                relx=0.10 if i == 0 else (0.45 if i == 1 else 0.85), 
                rely=0.5, 
                anchor=anchor_lbl,
                relwidth=0.25 if i == 0 else (0.35 if i == 1 else 0.25)
            )

        # Dibujar Filas de Historial
        for item in datos_pagina:
            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)
            
            # Fecha
            lbl_f = ctk.CTkLabel(fila, text=item["fecha"], anchor="w")
            lbl_f.place(relx=0.10, rely=0.5, anchor="w")
            
            # Tipo (Nombre del ahorro)
            lbl_t = ctk.CTkLabel(fila, text=item["tipo_ahorro"], anchor="w")
            lbl_t.place(relx=0.45, rely=0.5, anchor="w")
            
            # Importe
            lbl_i = ctk.CTkLabel(fila, text=f"$ {item['importe']:.2f}", text_color=self.color_ahorros[0], font=ctk.CTkFont(weight="bold"), anchor="e")
            lbl_i.place(relx=0.85, rely=0.5, anchor="e")

        # NUEVO: Fila de Suma Total (Posicionada al final de los registros y arriba de la paginación)
        frame_total = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray25", height=35, corner_radius=4)
        frame_total.pack(fill="x", pady=(5, 2), padx=2)
        frame_total.pack_propagate(False)

        lbl_total_texto = ctk.CTkLabel(frame_total, text="TOTAL ACUMULADO:", font=ctk.CTkFont(weight="bold", size=13), anchor="w")
        lbl_total_texto.place(relx=0.45, rely=0.5, anchor="w")

        lbl_total_valor = ctk.CTkLabel(frame_total, text=f"$ {suma_total_importe:.2f}", text_color=self.color_ahorros[0], font=ctk.CTkFont(weight="bold", size=14), anchor="e")
        lbl_total_valor.place(relx=0.85, rely=0.5, anchor="e")

        # Paginación Inferior (Hasta 10 registros por página)
        frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_paginacion.pack(fill="x", side="bottom")
        
        btn_ant = ctk.CTkButton(frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], state="normal" if self.pagina_actual > 1 else "disabled", command=self.pagina_anterior)
        btn_ant.place(relx=0.4, rely=0.5, anchor="e")
        
        lbl_paginas = ctk.CTkLabel(frame_paginacion, text=f"Página {self.pagina_actual} de {total_paginas}")
        lbl_paginas.place(relx=0.5, rely=0.5, anchor="center")
        
        btn_sig = ctk.CTkButton(frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], state="normal" if self.pagina_actual < total_paginas else "disabled", command=self.pagina_siguiente)
        btn_sig.place(relx=0.6, rely=0.5, anchor="w")

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        datos_f = self.obtener_datos_filtrados()
        if self.pagina_actual < (len(datos_f) + self.registros_por_pagina - 1) // self.registros_por_pagina:
            self.pagina_actual += 1
            self.actualizar_tabla()