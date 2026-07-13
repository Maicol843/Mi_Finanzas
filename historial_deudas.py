import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import database

class ModuloHistorialDeudas(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent
        self.color_deudas = ["#FD9843", "#fd7e14"] # Tonalidad naranja corporativa
        self.registro_seleccionado_id = None
        
        # Variables de Control de Paginación y Filtros
        self.pagina_actual = 1
        self.items_por_pagina = 10
        self.filtro_tipo = "Todos"
        self.filtro_mes = "Todos"
        self.pagos_filtrados = []

        # Encabezado Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Historial de Deudas", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(5, 20), anchor="center")

        # Barra Superior de Controles (Acciones a la izquierda, Combos de búsqueda a la derecha)
        self.frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controles.pack(fill="x", padx=20, pady=5)
        
        # Subcontenedor Izquierdo: Acciones de Edición y Eliminación
        self.frame_btns = ctk.CTkFrame(self.frame_controles, fg_color="transparent")
        self.frame_btns.pack(side="left", fill="y")
        
        self.btn_editar = ctk.CTkButton(self.frame_btns, text="Editar", fg_color="gray30", hover_color="gray40", width=90, command=self.abrir_ventana_editar)
        self.btn_editar.pack(side="left", padx=3)
        
        self.btn_eliminar = ctk.CTkButton(self.frame_btns, text="Eliminar", fg_color="gray30", hover_color="gray40", text_color="white", width=90, command=self.confirmar_eliminacion)
        self.btn_eliminar.pack(side="left", padx=3)

        # Subcontenedor Derecho: Filtros Selectores y Buscar
        self.frame_filtros = ctk.CTkFrame(self.frame_controles, fg_color="transparent")
        self.frame_filtros.pack(side="right", fill="y")

        # Obtener nombres únicos de deudas de la BD para el selector
        deudas_todas = database.obtener_deudas_con_pagos()
        nombres_deudas = ["Todos"] + list(set([d["nombre"] for d in deudas_todas]))

        # Selector Tipo/Nombre (Modificado a color Anaranjado)
        self.combo_tipo = ctk.CTkOptionMenu(
            self.frame_filtros, 
            values=nombres_deudas, 
            width=140,
            fg_color=self.color_deudas[0],
            button_color=self.color_deudas[1],
            button_hover_color=self.color_deudas[0]
        )
        self.combo_tipo.pack(side="left", padx=3)
        self.combo_tipo.set("Todos")

        # Selector Meses (Modificado a color Anaranjado)
        meses = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.combo_mes = ctk.CTkOptionMenu(
            self.frame_filtros, 
            values=meses, 
            width=120,
            fg_color=self.color_deudas[0],
            button_color=self.color_deudas[1],
            button_hover_color=self.color_deudas[0]
        )
        self.combo_mes.pack(side="left", padx=3)
        self.combo_mes.set("Todos")

        self.btn_buscar = ctk.CTkButton(self.frame_filtros, text="Buscar", fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], width=80, command=self.ejecutar_busqueda)
        self.btn_buscar.pack(side="left", padx=3)

        # Contenedor para la Estructura de la Tabla
        self.frame_tabla_contenedor = ctk.CTkFrame(self)
        self.frame_tabla_contenedor.pack(fill="both", expand=True, padx=20, pady=(10, 5))
        
        # Barra de Paginación Centrada (Abajo del contenedor)
        self.frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        self.frame_paginacion.pack(fill="x", side="bottom")
        
        self.btn_anterior = ctk.CTkButton(self.frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], text_color="white", command=self.pagina_anterior)
        self.btn_anterior.place(relx=0.4, rely=0.5, anchor="e")
        
        self.lbl_info_pag = ctk.CTkLabel(self.frame_paginacion, text="Página 1 de 1", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_info_pag.place(relx=0.5, rely=0.5, anchor="center")
        
        self.btn_siguiente = ctk.CTkButton(self.frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_deudas[0], hover_color=self.color_deudas[1], text_color="white", command=self.pagina_siguiente)
        self.btn_siguiente.place(relx=0.6, rely=0.5, anchor="w")

        # Cargar los datos iniciales al arrancar
        self.ejecutar_busqueda()

    def seleccionar_fila(self, id_registro):
        self.registro_seleccionado_id = None if self.registro_seleccionado_id == id_registro else id_registro
        self.actualizar_tabla()

    def ejecutar_busqueda(self):
        self.filtro_tipo = self.combo_tipo.get()
        self.filtro_mes = self.combo_mes.get()
        self.pagina_actual = 1
        
        # Consulta directa a los registros reales de la base de datos de deudas
        todos_los_pagos = database.obtener_historial_pagos()
        
        # Mapeo de meses en español para la evaluación de filtros
        meses_map = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6, 
                     "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}

        self.pagos_filtrados = []
        for pago in todos_los_pagos:
            cumple_tipo = (self.filtro_tipo == "Todos" or pago["tipo_deuda"].lower() == self.filtro_tipo.lower())
            
            cumple_mes = True
            if self.filtro_mes != "Todos":
                try:
                    fecha_dt = datetime.strptime(pago["fecha"], "%d-%m-%Y")
                    cumple_mes = (fecha_dt.month == meses_map[self.filtro_mes])
                except ValueError:
                    cumple_mes = False
            
            if cumple_tipo and cumple_mes:
                self.pagos_filtrados.append(pago)
                
        self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        total_paginas = max(1, (len(self.pagos_filtrados) + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def actualizar_tabla(self):
        # Limpiar filas previas exceptuando la paginación
        for widget in self.frame_tabla_contenedor.winfo_children():
            if widget != self.frame_paginacion:
                widget.destroy()

        # Cabeceras
        headers = ["Fecha del Pago", "Tipo de Deuda / Nombre", "Importe Registrado ($)"]
        frame_headers = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray20", height=35)
        frame_headers.pack(fill="x", side="top")
        frame_headers.pack_propagate(False)
        
        posiciones_x = [0.05, 0.40, 0.85]
        anchos_rel = [0.30, 0.40, 0.15]

        for i, h in enumerate(headers):
            anchor_lbl = "w" if i < 2 else "e"
            lbl = ctk.CTkLabel(frame_headers, text=h, font=ctk.CTkFont(weight="bold"), anchor=anchor_lbl)
            lbl.place(relx=posiciones_x[i], rely=0.5, anchor="w" if i < 2 else "e", relwidth=anchos_rel[i])

        # Lógica de Paginación
        total_items = len(self.pagos_filtrados)
        total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        
        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas

        indice_inicio = (self.pagina_actual - 1) * self.items_por_pagina
        indice_fin = indice_inicio + self.items_por_pagina
        pagos_pagina = self.pagos_filtrados[indice_inicio:indice_fin]

        self.lbl_info_pag.configure(text=f"Página {self.pagina_actual} de {total_paginas}")
        
        self.btn_anterior.configure(state="disabled" if self.pagina_actual == 1 else "normal")
        self.btn_siguiente.configure(state="disabled" if self.pagina_actual == total_paginas else "normal")

        # Renderizar registros de la página actual
        for item in pagos_pagina:
            bg_match = self.color_deudas if self.registro_seleccionado_id == item["id"] else "transparent"
            txt_color = "white" if self.registro_seleccionado_id == item["id"] else ["gray10", "white"]
            
            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color=bg_match, height=40, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)

            lbl_f = ctk.CTkLabel(fila, text=item["fecha"], text_color=txt_color, anchor="w")
            lbl_f.place(relx=posiciones_x[0], rely=0.5, anchor="w", relwidth=anchos_rel[0])
            
            lbl_t = ctk.CTkLabel(fila, text=item["tipo_deuda"], text_color=txt_color, anchor="w")
            lbl_t.place(relx=posiciones_x[1], rely=0.5, anchor="w", relwidth=anchos_rel[1])
            
            lbl_i = ctk.CTkLabel(fila, text=f"$ {item['importe']:.2f}", text_color=txt_color, anchor="e", font=ctk.CTkFont(weight="bold"))
            lbl_i.place(relx=posiciones_x[2], rely=0.5, anchor="e", relwidth=anchos_rel[2])
            
            id_actual = item["id"]
            for componente in [fila, lbl_f, lbl_t, lbl_i]:
                componente.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))

        # Sección del TOTAL (Suma de todos los importes filtrados acumulados)
        suma_total = sum(pago["importe"] for pago in self.pagos_filtrados)
        
        frame_total = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray25", height=40)
        frame_total.pack(fill="x", side="bottom", pady=(5, 0))
        frame_total.pack_propagate(False)
        
        lbl_txt_total = ctk.CTkLabel(frame_total, text="TOTAL:", font=ctk.CTkFont(size=13, weight="bold"), anchor="e")
        lbl_txt_total.place(relx=0.60, rely=0.5, anchor="e", relwidth=0.20)
        
        lbl_valor_total = ctk.CTkLabel(frame_total, text=f"$ {suma_total:.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.color_deudas[0], anchor="e")
        lbl_valor_total.place(relx=posiciones_x[2], rely=0.5, anchor="e", relwidth=anchos_rel[2])

    def abrir_ventana_editar(self):
        if self.registro_seleccionado_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona una cuota del historial para editar.")
            return
            
        # Buscar el registro seleccionado en la lista interna
        pago_seleccionado = next((p for p in self.pagos_filtrados if p["id"] == self.registro_seleccionado_id), None)
        if not pago_seleccionado:
            return

        # Ventana Flotante Modal (Toplevel)
        ventana_edit = ctk.CTkToplevel(self)
        ventana_edit.title("Editar Fecha de Pago")
        ventana_edit.geometry("360x310")
        ventana_edit.resizable(False, False)
        
        # Forzar a estar por delante y bloquear ventana de fondo
        ventana_edit.transient(self)
        ventana_edit.grab_set()
        
        # Centrar la ventana respecto a la app
        ventana_edit.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - (360 // 2)
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - (310 // 2)
        ventana_edit.geometry(f"+{x}+{y}")

        # Titulo
        lbl_v_titulo = ctk.CTkLabel(ventana_edit, text="Modificar Registro", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_v_titulo.pack(pady=(15, 15))

        # Campo Tipo Deuda (Deshabilitado)
        ctk.CTkLabel(ventana_edit, text="Tipo de Deuda:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30)
        entry_tipo = ctk.CTkEntry(ventana_edit, width=300)
        entry_tipo.insert(0, pago_seleccionado["tipo_deuda"])
        entry_tipo.configure(state="disabled")
        entry_tipo.pack(pady=(2, 10), padx=30)

        # Campo Importe (Deshabilitado)
        ctk.CTkLabel(ventana_edit, text="Importe ($):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30)
        entry_importe = ctk.CTkEntry(ventana_edit, width=300)
        entry_importe.insert(0, f"{pago_seleccionado['importe']:.2f}")
        entry_importe.configure(state="disabled")
        entry_importe.pack(pady=(2, 10), padx=30)

        # Campo Fecha (Habilitado para edición)
        ctk.CTkLabel(ventana_edit, text="Fecha del Pago (DD-MM-AAAA):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30)
        entry_fecha = ctk.CTkEntry(ventana_edit, width=300)
        entry_fecha.insert(0, pago_seleccionado["fecha"])
        entry_fecha.pack(pady=(2, 15), padx=30)
        entry_fecha.focus()

        # Acción de Guardar Cambios
        def guardar_cambios():
            nueva_fecha = entry_fecha.get().strip()
            
            # Validación simple de formato de fecha
            try:
                datetime.strptime(nueva_fecha, "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Error", "El formato de fecha no es válido. Utilice DD-MM-AAAA (ej: 12-07-2026).", parent=ventana_edit)
                return

            # Guardar en la Base de Datos
            try:
                database.actualizar_fecha_pago_db(self.registro_seleccionado_id, nueva_fecha)
                messagebox.showinfo("Éxito", "Fecha de pago actualizada correctamente.")
                ventana_edit.destroy() # Cerrar ventana flotante
                self.ejecutar_busqueda() # Recargar la tabla principal
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar en la base de datos: {e}", parent=ventana_edit)

        # Botón Guardar 
        btn_guardar = ctk.CTkButton(
            ventana_edit, 
            text="Guardar", 
            width=200,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.color_deudas[0], 
            hover_color=self.color_deudas[1], 
            command=guardar_cambios
        )
        btn_guardar.pack(pady=(5, 10))

    def confirmar_eliminacion(self):
        if self.registro_seleccionado_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona una cuota del historial para eliminar.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Deseas eliminar permanentemente este registro de pago del historial?"):
            try:
                # 1. Elimina físicamente el registro de la tabla 'pagos_deudas'
                database.eliminar_pago_deuda_db(self.registro_seleccionado_id)
                
                # 2. Deselecciona la fila eliminada para evitar inconsistencias
                self.registro_seleccionado_id = None
                messagebox.showinfo("Éxito", "El registro ha sido eliminado con éxito.")
                
                # 3. Refresca la tabla y el cálculo del acumulado TOTAL de forma automática
                self.ejecutar_busqueda()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el registro de la base de datos: {e}")