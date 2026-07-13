import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import database

class ModuloDeudas(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent
        self.color_deudas = ["#FFCD39", "#ffc107"] # Tonalidad naranja corporativa
        self.deuda_seleccionada_id = None
        
        # Variables para Control de Paginación y Búsqueda
        self.pagina_actual = 1
        self.items_por_pagina = 10
        self.filtro_busqueda = ""
        
        # Encabezado Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Mis Deudas", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(10, 5), anchor="center")
        
        self.lbl_desc = ctk.CTkLabel(
            self, 
            text="Aquí encontrarás tus obligaciones a pagar, préstamos, tarjetas de crédito, etc.",
            font=ctk.CTkFont(size=13),
            wraplength=600
        )
        self.lbl_desc.pack(pady=(0, 20), anchor="center")

        # Barra de Acciones y Buscador
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=20, pady=5)
        
        # Contenedor izquierdo para botones de acción
        self.frame_btns_izquierda = ctk.CTkFrame(self.frame_acciones, fg_color="transparent")
        self.frame_btns_izquierda.pack(side="left", fill="y")
        
        self.btn_nuevo = ctk.CTkButton(self.frame_btns_izquierda, text="Nuevo", fg_color=self.color_deudas, text_color="black", hover_color=self.color_deudas[1], width=90, command=self.abrir_ventana_nuevo)
        self.btn_nuevo.pack(side="left", padx=3)
        
        self.btn_editar = ctk.CTkButton(self.frame_btns_izquierda, text="Editar", fg_color="gray30", hover_color="gray40", width=90, command=self.abrir_ventana_editar)
        self.btn_editar.pack(side="left", padx=3)

        self.btn_eliminar = ctk.CTkButton(self.frame_btns_izquierda, text="Eliminar", fg_color="gray30", hover_color="gray40", text_color="white", width=90, command=self.confirmar_eliminacion)
        self.btn_eliminar.pack(side="left", padx=3)
        
        self.btn_registrar = ctk.CTkButton(self.frame_btns_izquierda, text="Registrar", fg_color="gray30", hover_color="gray40", width=90, command=self.abrir_ventana_registrar)
        self.btn_registrar.pack(side="left", padx=3)
        
        self.btn_historial = ctk.CTkButton(self.frame_btns_izquierda, text="Historial", fg_color="gray30", hover_color="gray40", width=90, command=self.ir_a_historial)
        self.btn_historial.pack(side="left", padx=3)
        
        self.btn_grafica = ctk.CTkButton(self.frame_btns_izquierda, text="Gráficas", fg_color="gray30", hover_color="gray40", width=90, command=self.ir_a_grafica)
        self.btn_grafica.pack(side="left", padx=3)

        # Buscador alineado a la derecha superior de la tabla
        self.entry_buscar = ctk.CTkEntry(self.frame_acciones, placeholder_text="Buscar deuda...", width=200)
        self.entry_buscar.pack(side="right", padx=3)
        self.entry_buscar.bind("<KeyRelease>", self.filtrar_deudas)

        # Contenedor para la estructura de la tabla
        self.frame_tabla_contenedor = ctk.CTkFrame(self)
        self.frame_tabla_contenedor.pack(fill="both", expand=True, padx=20, pady=(10, 5))
        
        # Barra de Paginación General (Empaquetada de forma interna abajo de la tabla)
        self.frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        self.frame_paginacion.pack(fill="x", side="bottom")
        
        self.btn_anterior = ctk.CTkButton(self.frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], text_color="white", command=self.pagina_anterior)
        self.btn_anterior.place(relx=0.4, rely=0.5, anchor="e")
        
        self.lbl_info_pag = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_info_pag.place(relx=0.5, rely=0.5, anchor="center")
        
        self.btn_siguiente = ctk.CTkButton(self.frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], text_color="white", command=self.pagina_siguiente)
        self.btn_siguiente.place(relx=0.6, rely=0.5, anchor="w")
        
        self.actualizar_tabla()

    def ir_a_historial(self):
        from historial_deudas import ModuloHistorialDeudas
        # Destruir la vista actual de Mis Deudas
        self.destroy()
        # Instanciar el historial en el mismo contenedor padre
        historial_vista = ModuloHistorialDeudas(self.parent)
        historial_vista.pack(fill="both", expand=True)

    def ir_a_grafica(self):
        from grafica_deudas import ModuloGraficaDeudas
        # Destruir la vista actual de Mis Deudas
        self.destroy()
        # Instanciar el módulo de gráficas en el mismo contenedor padre
        grafica_vista = ModuloGraficaDeudas(self.parent)
        grafica_vista.pack(fill="both", expand=True)

    def seleccionar_fila(self, id_deuda):
        self.deuda_seleccionada_id = None if self.deuda_seleccionada_id == id_deuda else id_deuda
        self.actualizar_tabla()

    def filtrar_deudas(self, event):
        self.filtro_busqueda = self.entry_buscar.get().strip().lower()
        self.pagina_actual = 1
        self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        deudas_todas = database.obtener_deudas_con_pagos()
        if self.filtro_busqueda:
            deudas_filtradas = [d for d in deudas_todas if self.filtro_busqueda in d["nombre"].lower()]
        else:
            deudas_filtradas = deudas_todas
            
        if self.pagina_actual < (len(deudas_filtradas) + self.items_por_pagina - 1) // self.items_por_pagina:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def actualizar_tabla(self):
        # Limpiar filas previas manteniendo la estructura
        for widget in self.frame_tabla_contenedor.winfo_children():
            if widget != self.frame_paginacion:
                widget.destroy()

        # Cabeceras
        headers = ["Deuda", "Deuda Total", "Pago Mensual", "Interés", "Cuota Tot.", "Cuota Rest.", "Progreso"]
        frame_headers = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray20", height=35)
        frame_headers.pack(fill="x", side="top")
        frame_headers.pack_propagate(False)
        
        posiciones_x = [0.03, 0.28, 0.41, 0.53, 0.64, 0.76, 0.88]
        anchos_rel = [0.23, 0.11, 0.11, 0.08, 0.09, 0.10, 0.12]

        for i, h in enumerate(headers):
            anchor_lbl = "w" if i == 0 or i == 6 else "e"
            lbl = ctk.CTkLabel(frame_headers, text=h, font=ctk.CTkFont(weight="bold"), anchor=anchor_lbl)
            lbl.place(
                relx=posiciones_x[i], 
                rely=0.5, 
                anchor="w" if i == 0 or i == 6 else "e",
                relwidth=anchos_rel[i]
            )

        # Cargar registros desde la base de datos real
        deudas_todas = database.obtener_deudas_con_pagos()

        # Aplicar filtro de búsqueda si existe
        if self.filtro_busqueda:
            deudas_filtradas = [d for d in deudas_todas if self.filtro_busqueda in d["nombre"].lower()]
        else:
            deudas_filtradas = deudas_todas

        # Lógica de Paginación
        total_items = len(deudas_filtradas)
        total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        
        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas

        indice_inicio = (self.pagina_actual - 1) * self.items_por_pagina
        indice_fin = indice_inicio + self.items_por_pagina
        deudas_pagina = deudas_filtradas[indice_inicio:indice_fin]

        self.lbl_info_pag.configure(text=f"Página {self.pagina_actual} de {total_paginas}")
        
        # Control visual de estados nativos para Anterior y Siguiente
        if self.pagina_actual == 1:
            self.btn_anterior.configure(state="disabled")
        else:
            self.btn_anterior.configure(state="normal")
            
        if self.pagina_actual == total_paginas:
            self.btn_siguiente.configure(state="disabled")
        else:
            self.btn_siguiente.configure(state="normal")

        # Renderizar deudas de la página actual
        for item in deudas_pagina:
            bg_match = self.color_deudas if self.deuda_seleccionada_id == item["id"] else "transparent"
            txt_color = "black" if self.deuda_seleccionada_id == item["id"] else ["gray10", "white"]
            
            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color=bg_match, height=45, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)
            
            meses_restantes = max(0, item["meses_a_pagar"] - item["meses_pagados"])
            porcentaje = (item["meses_pagados"] * 100) / item["meses_a_pagar"] if item["meses_a_pagar"] > 0 else 0
            porcentaje_barra = min(1.0, porcentaje / 100)

            lbl_n = ctk.CTkLabel(fila, text=item["nombre"], text_color=txt_color, anchor="w")
            lbl_n.place(relx=posiciones_x[0], rely=0.5, anchor="w", relwidth=anchos_rel[0])
            
            lbl_dt = ctk.CTkLabel(fila, text=f"$ {item['total']:.2f}", text_color=txt_color, anchor="e")
            lbl_dt.place(relx=posiciones_x[1], rely=0.5, anchor="e", relwidth=anchos_rel[1])
            
            lbl_pm = ctk.CTkLabel(fila, text=f"$ {item['pago_mensual']:.2f}", text_color=txt_color, anchor="e")
            lbl_pm.place(relx=posiciones_x[2], rely=0.5, anchor="e", relwidth=anchos_rel[2])
            
            lbl_int = ctk.CTkLabel(fila, text=f"{item['interes']}%", text_color=txt_color, anchor="e")
            lbl_int.place(relx=posiciones_x[3], rely=0.5, anchor="e", relwidth=anchos_rel[3])
            
            lbl_mt = ctk.CTkLabel(fila, text=str(item["meses_a_pagar"]), text_color=txt_color, anchor="e")
            lbl_mt.place(relx=posiciones_x[4], rely=0.5, anchor="e", relwidth=anchos_rel[4])
            
            lbl_mr = ctk.CTkLabel(fila, text=str(meses_restantes), text_color=txt_color, anchor="e")
            lbl_mr.place(relx=posiciones_x[5], rely=0.5, anchor="e", relwidth=anchos_rel[5])
            
            frame_progreso = ctk.CTkFrame(fila, fg_color="transparent")
            frame_progreso.place(relx=posiciones_x[6], rely=0.5, anchor="w", relwidth=anchos_rel[6])
            
            p_bar = ctk.CTkProgressBar(frame_progreso, width=55, progress_color=self.color_deudas[0] if self.deuda_seleccionada_id != item["id"] else "white")
            p_bar.set(porcentaje_barra)
            p_bar.pack(side="left", padx=(0, 4))
            
            lbl_p = ctk.CTkLabel(frame_progreso, text=f"{porcentaje:.1f}%", text_color=txt_color, font=ctk.CTkFont(size=11, weight="bold"))
            lbl_p.pack(side="left")
            
            id_actual = item["id"]
            for componente in [fila, lbl_n, lbl_dt, lbl_pm, lbl_int, lbl_mt, lbl_mr]:
                componente.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))

    def abrir_ventana_nuevo(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Nueva Deuda")
        ventana.geometry("400x520")
        ventana.grab_set()
        ventana.resizable(False, False)
        
        ctk.CTkLabel(ventana, text="Nueva Deuda", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(ventana, text="Fecha Inicial (DD-MM-AAAA):", anchor="w").pack(fill="x", padx=40)
        entry_fecha = ctk.CTkEntry(ventana)
        entry_fecha.pack(fill="x", padx=40, pady=(0, 10))
        entry_fecha.insert(0, datetime.today().strftime('%d-%m-%Y'))
        
        ctk.CTkLabel(ventana, text="Nombre de la Deuda:", anchor="w").pack(fill="x", padx=40)
        entry_nombre = ctk.CTkEntry(ventana, placeholder_text="Ej: Tarjeta Visa, Crédito...")
        entry_nombre.pack(fill="x", padx=40, pady=(0, 10))
        
        ctk.CTkLabel(ventana, text="Deuda Total ($):", anchor="w").pack(fill="x", padx=40)
        entry_total = ctk.CTkEntry(ventana)
        entry_total.pack(fill="x", padx=40, pady=(0, 10))
        
        ctk.CTkLabel(ventana, text="Pago Mensual ($):", anchor="w").pack(fill="x", padx=40)
        entry_pago = ctk.CTkEntry(ventana)
        entry_pago.pack(fill="x", padx=40, pady=(0, 10))
        
        ctk.CTkLabel(ventana, text="Interés (% porcentaje):", anchor="w").pack(fill="x", padx=40)
        entry_interes = ctk.CTkEntry(ventana)
        entry_interes.pack(fill="x", padx=40, pady=(0, 10))
        
        ctk.CTkLabel(ventana, text="Meses a Pagar:", anchor="w").pack(fill="x", padx=40)
        entry_meses = ctk.CTkEntry(ventana)
        entry_meses.pack(fill="x", padx=40, pady=(0, 20))

        def guardar():
            try:
                datetime.strptime(entry_fecha.get().strip(), "%d-%m-%Y")
                total = float(entry_total.get().strip())
                pago = float(entry_pago.get().strip())
                interes = float(entry_interes.get().strip())
                meses = int(entry_meses.get().strip())
                nombre = entry_nombre.get().strip()
                
                if not nombre: raise ValueError("Nombre vacío")
                
                database.insertar_deuda(nombre, total, pago, interes, meses)
                self.actualizar_tabla()
                ventana.destroy()
            except ValueError:
                messagebox.showerror("Error", "Campos inválidos. Compruebe fechas y montos numéricos.", parent=ventana)

        frame_btns = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btns.pack(fill="x", padx=40)
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray30", width=100, command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Guardar", fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], text_color="black", width=100, command=guardar).pack(side="right", padx=5)

    def abrir_ventana_editar(self):
        if self.deuda_seleccionada_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla para editar.")
            return

        deudas = database.obtener_deudas_con_pagos()
        deuda_actual = next((d for d in deudas if d["id"] == self.deuda_seleccionada_id), None)
        if not deuda_actual: return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar Deuda")
        ventana.geometry("400x460")
        ventana.grab_set()
        ventana.resizable(False, False)
        
        ctk.CTkLabel(ventana, text="Editar Deuda", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(ventana, text="Nombre de la Deuda:", anchor="w").pack(fill="x", padx=40)
        entry_nombre = ctk.CTkEntry(ventana)
        entry_nombre.pack(fill="x", padx=40, pady=(0, 10))
        entry_nombre.insert(0, deuda_actual["nombre"])
        
        ctk.CTkLabel(ventana, text="Deuda Total ($):", anchor="w").pack(fill="x", padx=40)
        entry_total = ctk.CTkEntry(ventana)
        entry_total.pack(fill="x", padx=40, pady=(0, 10))
        entry_total.insert(0, str(deuda_actual["total"]))
        
        ctk.CTkLabel(ventana, text="Pago Mensual ($):", anchor="w").pack(fill="x", padx=40)
        entry_pago = ctk.CTkEntry(ventana)
        entry_pago.pack(fill="x", padx=40, pady=(0, 10))
        entry_pago.insert(0, str(deuda_actual["pago_mensual"]))
        
        ctk.CTkLabel(ventana, text="Interés (%):", anchor="w").pack(fill="x", padx=40)
        entry_interes = ctk.CTkEntry(ventana)
        entry_interes.pack(fill="x", padx=40, pady=(0, 10))
        entry_interes.insert(0, str(deuda_actual["interes"]))
        
        ctk.CTkLabel(ventana, text="Meses a Pagar:", anchor="w").pack(fill="x", padx=40)
        entry_meses = ctk.CTkEntry(ventana)
        entry_meses.pack(fill="x", padx=40, pady=(0, 20))
        entry_meses.insert(0, str(deuda_actual["meses_a_pagar"]))

        def guardar_cambios():
            try:
                nuevo_n = entry_nombre.get().strip()
                tot = float(entry_total.get().strip())
                pag = float(entry_pago.get().strip())
                inte = float(entry_interes.get().strip())
                mes = int(entry_meses.get().strip())
                
                database.actualizar_deuda_db(self.deuda_seleccionada_id, nuevo_n, tot, pag, inte, mes, deuda_actual["nombre"])
                self.deuda_seleccionada_id = None
                self.actualizar_tabla()
                ventana.destroy()
            except ValueError:
                messagebox.showerror("Error", "Valores numéricos incorrectos o duplicados.", parent=ventana)

        frame_btns = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btns.pack(fill="x", padx=40)
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray30", width=100, command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Guardar", fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], text_color="black", width=100, command=guardar_cambios).pack(side="right", padx=5)

    def confirmar_eliminacion(self):
        if self.deuda_seleccionada_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla para eliminar.")
            return

        deudas = database.obtener_deudas_con_pagos()
        deuda_actual = next((d for d in deudas if d["id"] == self.deuda_seleccionada_id), None)
        if not deuda_actual: return

        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar de forma permanente la deuda '{deuda_actual['nombre']}' y sus cuotas?"):
            database.eliminar_deuda_db(self.deuda_seleccionada_id, deuda_actual["nombre"])
            self.deuda_seleccionada_id = None
            self.actualizar_tabla()

    def abrir_ventana_registrar(self):
        todas = database.obtener_deudas_con_pagos()
        deudas_activas = [d for d in todas if d["meses_pagados"] < d["meses_a_pagar"]]
        
        if not deudas_activas:
            messagebox.showwarning("Atención", "No hay deudas activas/vigentes para asignarle un pago.")
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Registrar Pago de Deuda")
        ventana.geometry("400x350")
        ventana.grab_set()
        ventana.resizable(False, False)
        
        ctk.CTkLabel(ventana, text="Registrar Pago", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(ventana, text="Fecha del Pago (DD-MM-AAAA):", anchor="w").pack(fill="x", padx=40)
        entry_fecha = ctk.CTkEntry(ventana)
        entry_fecha.pack(fill="x", padx=40, pady=(0, 10))
        entry_fecha.insert(0, datetime.today().strftime('%d-%m-%Y'))
        
        ctk.CTkLabel(ventana, text="Tipo de Deuda:", anchor="w").pack(fill="x", padx=40)
        nombres_disponibles = [d["nombre"] for d in deudas_activas]
        
        ctk.CTkLabel(ventana, text="Pago Mensual ($):", anchor="w").pack(fill="x", padx=40)
        entry_importe = ctk.CTkEntry(ventana)
        
        def refrescar_monto_automatico(deuda_elegida):
            obj = next((d for d in deudas_activas if d["nombre"] == deuda_elegida), None)
            if obj:
                entry_importe.configure(state="normal")
                entry_importe.delete(0, tk.END)
                entry_importe.insert(0, f"{obj['pago_mensual']:.2f}")
                entry_importe.configure(state="disabled")

        combo_tipo = ctk.CTkOptionMenu(ventana, values=nombres_disponibles, fg_color="gray30", button_color="gray40", command=refrescar_monto_automatico)
        combo_tipo.pack(fill="x", padx=40, pady=(0, 10))
        combo_tipo.set(nombres_disponibles[0])
        
        entry_importe.pack(fill="x", padx=40, pady=(0, 20))
        refrescar_monto_automatico(nombres_disponibles[0])

        def registrar_pago():
            try:
                datetime.strptime(entry_fecha.get().strip(), "%d-%m-%Y")
                deuda_sel = combo_tipo.get()
                obj = next((d for d in deudas_activas if d["nombre"] == deuda_sel), None)
                
                if obj:
                    database.registrar_pago_deuda_db(entry_fecha.get().strip(), deuda_sel, obj["pago_mensual"])
                    
                self.actualizar_tabla()
                ventana.destroy()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido (DD-MM-AAAA).", parent=ventana)

        frame_btns = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btns.pack(fill="x", padx=40)
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray30", width=100, command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Registrar", fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], text_color="black", width=100, command=registrar_pago).pack(side="right", padx=5)