import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import database  # Asegúrate de mapear estas funciones en tu archivo database.py

class ModuloAhorros(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent
        self.color_ahorros = ["#4CAF50", "#45a049"]  # Tonalidad verde para identificar ahorros
        self.ahorro_seleccionado_id = None
        
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.texto_busqueda = tk.StringVar()

        # Encabezado Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Mis Ahorros", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(10, 5), anchor="center")
        
        self.lbl_desc = ctk.CTkLabel(
            self, 
            text="Aquí ingresarás tus reservas para el futuro con el fin de cubrir imprevistos, viajes, realizar grandes compras o invertir.",
            font=ctk.CTkFont(size=13),
            wraplength=600
        )
        self.lbl_desc.pack(pady=(0, 20), anchor="center")

        # Barra de Acciones (Botones Principales)
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=20, pady=5)
        
        self.btn_nuevo = ctk.CTkButton(self.frame_acciones, text="Nuevo", fg_color=self.color_ahorros, text_color="white", hover_color=self.color_ahorros[1], width=90, command=self.abrir_ventana_nuevo)
        self.btn_nuevo.pack(side="left", padx=3)
        
        self.btn_registrar = ctk.CTkButton(self.frame_acciones, text="Registrar", fg_color="gray30", hover_color="gray40", width=90, command=self.abrir_ventana_registrar)
        self.btn_registrar.pack(side="left", padx=3)
        
        self.btn_historial = ctk.CTkButton(self.frame_acciones, text="Historial", fg_color="gray30", hover_color="gray40", width=90, command=self.ir_a_historial)
        self.btn_historial.pack(side="left", padx=3)
        
        # MODIFICADO: Ahora ejecuta self.ir_a_grafica para cambiar de módulo
        self.btn_grafica = ctk.CTkButton(self.frame_acciones, text="Gráficas", fg_color="gray30", hover_color="gray40", width=90, command=self.ir_a_grafica)
        self.btn_grafica.pack(side="left", padx=3)

        # Buscador por Nombre de Ahorro (Arriba de la tabla, alineado a la derecha)
        self.entry_buscar = ctk.CTkEntry(self.frame_acciones, placeholder_text="Buscar por ahorro...", width=200)
        self.entry_buscar.pack(side="right", padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.detectar_cambio_filtro())

        # Contenedor dinámico para la tabla
        self.frame_tabla_contenedor = ctk.CTkFrame(self)
        self.frame_tabla_contenedor.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.actualizar_tabla()

    def ir_a_historial(self):
        from historial_ahorros import ModuloHistorialAhorros
        # Limpiamos el frame actual y cargamos el historial
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        historial_frame = ModuloHistorialAhorros(self.parent)
        historial_frame.pack(fill="both", expand=True)

    # MODIFICADO: Redirige dinámicamente limpiando la interfaz para mostrar el gráfico completo
    def ir_a_grafica(self):
        from grafica_ahorros import ModuloGraficaAhorros
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        grafica_frame = ModuloGraficaAhorros(self.parent)
        grafica_frame.pack(fill="both", expand=True)

    def detectar_cambio_filtro(self):
        self.texto_busqueda.set(self.entry_buscar.get())
        self.pagina_actual = 1
        self.actualizar_tabla()

    def obtener_datos_filtrados(self):
        try:
            todas_las_metas = database.obtener_metas_ahorro()
        except AttributeError:
            todas_las_metas = []
        
        busqueda = self.texto_busqueda.get().lower().strip()
        if busqueda:
            todas_las_metas = [a for a in todas_las_metas if busqueda in a["nombre"].lower()]
            
        return todas_las_metas

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

        # Cabeceras de la Tabla de Ahorros
        headers = ["Ahorro", "Meta", "Imp. Inicial", "Total Ahorrado", "Progreso"]
        frame_headers = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray20", height=35)
        frame_headers.pack(fill="x", side="top")
        frame_headers.pack_propagate(False)
        
        for i, h in enumerate(headers):
            anchor_lbl = "w" if i == 0 or i == 4 else "e"
            lbl = ctk.CTkLabel(frame_headers, text=h, font=ctk.CTkFont(weight="bold"), anchor=anchor_lbl)
            lbl.place(
                relx=0.05 if i==0 else (0.25 if i==1 else (0.42 if i==2 else (0.60 if i==3 else 0.78))), 
                rely=0.5, 
                anchor="w" if i == 0 or i == 4 else "e",
                relwidth=0.18 if i==0 else (0.15 if i==1 else (0.15 if i==2 else (0.15 if i==3 else 0.20)))
            )

        # Dibujar Filas de Datos
        for item in datos_pagina:
            bg_match = self.color_ahorros if self.ahorro_seleccionado_id == item["id"] else "transparent"
            txt_color = "white" if self.ahorro_seleccionado_id == item["id"] else ["gray10", "white"]
            
            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color=bg_match, height=45, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)
            
            # Nombre
            lbl_n = ctk.CTkLabel(fila, text=item["nombre"], text_color=txt_color, anchor="w")
            lbl_n.place(relx=0.05, rely=0.5, anchor="w")
            
            # Meta
            lbl_m = ctk.CTkLabel(fila, text=f"$ {item['meta']:.2f}", text_color=txt_color, anchor="e")
            lbl_m.place(relx=0.25, rely=0.5, anchor="e")
            
            # Importe Inicial
            lbl_ii = ctk.CTkLabel(fila, text=f"$ {item['inicial']:.2f}", text_color=txt_color, anchor="e")
            lbl_ii.place(relx=0.42, rely=0.5, anchor="e")
            
            # Total Ahorrado (Inicial + Depósitos realizados)
            lbl_ta = ctk.CTkLabel(fila, text=f"$ {item['total_ahorrado']:.2f}", text_color=txt_color, anchor="e")
            lbl_ta.place(relx=0.60, rely=0.5, anchor="e")
            
            # Cálculo de progreso con tope en 100%
            porcentaje = (item['total_ahorrado'] * 100) / item['meta'] if item['meta'] > 0 else 0
            porcentaje_barra = min(1.0, porcentaje / 100)
            
            # Contenedor del progreso (Barra de progreso + Texto %)
            frame_progreso = ctk.CTkFrame(fila, fg_color="transparent")
            frame_progreso.place(relx=0.78, rely=0.5, anchor="w", relwidth=0.20)
            
            p_bar = ctk.CTkProgressBar(frame_progreso, width=100, progress_color=self.color_ahorros[0])
            p_bar.set(porcentaje_barra)
            p_bar.pack(side="left", padx=(0, 5))
            
            lbl_p = ctk.CTkLabel(frame_progreso, text=f"{porcentaje:.1f}%", text_color=txt_color, font=ctk.CTkFont(size=11, weight="bold"))
            lbl_p.pack(side="left")
            
            # Bind para seleccionar fila
            id_actual = item["id"]
            fila.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))

        # Paginación Inferior (Hasta 10 ahorros por página)
        frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_paginacion.pack(fill="x", side="bottom")
        
        btn_ant = ctk.CTkButton(frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], state="normal" if self.pagina_actual > 1 else "disabled", command=self.pagina_anterior)
        btn_ant.place(relx=0.4, rely=0.5, anchor="e")
        
        lbl_paginas = ctk.CTkLabel(frame_paginacion, text=f"Página {self.pagina_actual} de {total_paginas}")
        lbl_paginas.place(relx=0.5, rely=0.5, anchor="center")
        
        btn_sig = ctk.CTkButton(frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], state="normal" if self.pagina_actual < total_paginas else "disabled", command=self.pagina_siguiente)
        btn_sig.place(relx=0.6, rely=0.5, anchor="w")

    def seleccionar_fila(self, id_ahorro):
        self.ahorro_seleccionado_id = None if self.ahorro_seleccionado_id == id_ahorro else id_ahorro
        self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        datos_f = self.obtener_datos_filtrados()
        if self.pagina_actual < (len(datos_f) + self.registros_por_pagina - 1) // self.registros_por_pagina:
            self.pagina_actual += 1
            self.actualizar_tabla()

    # FORMULARIO: Botón Nuevo (Meta de Ahorros)
    def abrir_ventana_nuevo(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Nueva Meta de Ahorro")
        ventana.geometry("400x380")
        ventana.grab_set()
        ventana.resizable(False, False)
        
        ctk.CTkLabel(ventana, text="Nueva Meta de Ahorro", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(ventana, text="Nombre del Ahorro:", anchor="w").pack(fill="x", padx=40)
        entry_nombre = ctk.CTkEntry(ventana, placeholder_text="Ej: Viaje, Auto, Inversión...")
        entry_nombre.pack(fill="x", padx=40, pady=(0, 10))
        
        ctk.CTkLabel(ventana, text="Meta (Importe a llegar $):", anchor="w").pack(fill="x", padx=40)
        entry_meta = ctk.CTkEntry(ventana)
        entry_meta.pack(fill="x", padx=40, pady=(0, 10))
        
        ctk.CTkLabel(ventana, text="Importe Inicial ($):", anchor="w").pack(fill="x", padx=40)
        entry_inicial = ctk.CTkEntry(ventana)
        entry_inicial.pack(fill="x", padx=40, pady=(0, 20))

        def guardar_meta():
            nombre = entry_nombre.get().strip()
            meta_str = entry_meta.get().strip()
            inicial_str = entry_inicial.get().strip()
            
            if not nombre or not meta_str or not inicial_str:
                messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=ventana)
                return
            try:
                meta = float(meta_str)
                inicial = float(inicial_str)
            except ValueError:
                messagebox.showerror("Error", "Los importes deben ser valores numéricos válidos.", parent=ventana)
                return
                
            try:
                # 1. Guardamos la meta global en la base de datos
                database.insertar_meta_ahorro(nombre, meta, inicial)
                
                # CORRECCIÓN: Si el importe inicial es mayor a 0, se impacta simultáneamente en el historial de transacciones
                if inicial > 0:
                    fecha_hoy = datetime.today().strftime('%d-%m-%Y')
                    database.insertar_deposito_ahorro(fecha_hoy, nombre, inicial)
                    
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=ventana)
                return
            except AttributeError:
                pass
                
            self.actualizar_tabla()
            ventana.destroy()

        frame_btns = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btns.pack(fill="x", padx=40)
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray30", width=100, command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Guardar", fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], width=100, command=guardar_meta).pack(side="right", padx=5)

    # FORMULARIO: Botón Registrar (Depósitos Mensuales)
    def abrir_ventana_registrar(self):
        try:
            metas_existentes = database.obtener_metas_ahorro()
        except AttributeError:
            metas_existentes = []

        if not metas_existentes:
            messagebox.showwarning("Atención", "Primero debes crear una meta de ahorro usando el botón 'Nuevo'.")
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Registrar Depósito de Ahorro")
        ventana.geometry("400x380")
        ventana.grab_set()
        ventana.resizable(False, False)
        
        ctk.CTkLabel(ventana, text="Registrar Ahorro", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(ventana, text="Fecha (DD-MM-AAAA):", anchor="w").pack(fill="x", padx=40)
        entry_fecha = ctk.CTkEntry(ventana)
        entry_fecha.pack(fill="x", padx=40, pady=(0, 10))
        entry_fecha.insert(0, datetime.today().strftime('%d-%m-%Y'))
        
        ctk.CTkLabel(ventana, text="Tipo de Ahorro:", anchor="w").pack(fill="x", padx=40)
        nombres_ahorros = [m["nombre"] for m in metas_existentes]
        combo_tipo = ctk.CTkOptionMenu(ventana, values=nombres_ahorros, fg_color="gray30", button_color="gray40")
        combo_tipo.pack(fill="x", padx=40, pady=(0, 10))
        
        ctk.CTkLabel(ventana, text="Importe a ingresar ($):", anchor="w").pack(fill="x", padx=40)
        entry_importe = ctk.CTkEntry(ventana)
        entry_importe.pack(fill="x", padx=40, pady=(0, 20))

        def guardar_registro():
            fecha = entry_fecha.get().strip()
            tipo_ahorro = combo_tipo.get()
            importe_str = entry_importe.get().strip()
            
            if not fecha or not importe_str:
                messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=ventana)
                return
            try:
                datetime.strptime(fecha, "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Error", "El formato de fecha debe ser DD-MM-AAAA.", parent=ventana)
                return
            try:
                importe = float(importe_str)
            except ValueError:
                messagebox.showerror("Error", "El importe debe ser un número válido.", parent=ventana)
                return
                
            try:
                database.insertar_deposito_ahorro(fecha, tipo_ahorro, importe)
            except AttributeError:
                pass
                
            self.actualizar_tabla()
            ventana.destroy()

        frame_btns = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btns.pack(fill="x", padx=40)
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray30", width=100, command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Registrar", fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], width=100, command=guardar_registro).pack(side="right", padx=5)