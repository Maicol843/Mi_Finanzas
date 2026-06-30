import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import database 
from historial import ModuloHistorial
from grafica import ModuloGrafica

class ModuloIngresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent  # Guardamos la referencia para la navegación
        self.color_primario = ["#FFCD39", "#ffc107"]
        self.ingreso_seleccionado_id = None
        
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.texto_busqueda = tk.StringVar()

        # Encabezado
        self.lbl_titulo = ctk.CTkLabel(self, text="Mis Ingresos", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(10, 5), anchor="center")
        
        self.lbl_desc = ctk.CTkLabel(
            self, 
            text="Aquí se registran tus ingresos del mes actual. Los registros anteriores se guardan en el Historial.",
            font=ctk.CTkFont(size=13),
            wraplength=600
        )
        self.lbl_desc.pack(pady=(0, 20), anchor="center")

        # Barra de Acciones
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=20, pady=10)
        
        self.btn_registrar = ctk.CTkButton(self.frame_acciones, text="Registrar", fg_color=self.color_primario, text_color="black", hover_color=self.color_primario, width=90, command=self.abrir_ventana_registro)
        self.btn_registrar.pack(side="left", padx=3)
        
        self.btn_editar = ctk.CTkButton(self.frame_acciones, text="Editar", fg_color="#3D8BFD", hover_color="#0d6efd", width=90, command=self.abrir_ventana_editar)
        self.btn_editar.pack(side="left", padx=3)
        
        self.btn_eliminar = ctk.CTkButton(self.frame_acciones, text="Eliminar", fg_color="#d9534f", hover_color="#c9302c", width=90, command=self.eliminar_ingreso)
        self.btn_eliminar.pack(side="left", padx=3)

        # Botón Historial
        self.btn_historial = ctk.CTkButton(self.frame_acciones, text="Historial", fg_color="gray30", width=90, command=self.ir_a_historial)
        self.btn_historial.pack(side="left", padx=3)

        # Botón Gráfica
        self.btn_grafica = ctk.CTkButton(
            self.frame_acciones, 
            text="Gráfica", 
            fg_color="gray30", 
            width=90, 
            command=self.ir_a_grafica
        )
        self.btn_grafica.pack(side="left", padx=3)
        
        self.entry_buscar = ctk.CTkEntry(self.frame_acciones, placeholder_text="Buscar por descripcion", width=200)
        self.entry_buscar.pack(side="right", padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.detectar_busqueda())

        self.frame_tabla_contenedor = ctk.CTkFrame(self)
        self.frame_tabla_contenedor.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.actualizar_tabla()

    def ir_a_historial(self):
        """Destruye la vista actual y carga el módulo de historial dentro del panel de inicio"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        historial_vista = ModuloHistorial(self.parent)
        historial_vista.pack(fill="both", expand=True)
    
    def ir_a_grafica(self):
        """Destruye la vista de ingresos actual y carga el panel dinámico de estadísticas"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        grafica_vista = ModuloGrafica(self.parent)
        grafica_vista.pack(fill="both", expand=True)

    def detectar_busqueda(self):
        self.texto_busqueda.set(self.entry_buscar.get())
        self.pagina_actual = 1
        self.actualizar_tabla()

    def obtener_datos_filtrados(self):
        # Capturamos de forma dinámica el mes y año actuales del sistema reloj
        mes_actual = datetime.today().strftime('%m')
        anio_actual = datetime.today().strftime('%Y')
        
        # Filtramos estrictamente por los dos parámetros para evitar arrastrar el año pasado
        todos_los_ingresos = database.obtener_ingresos_por_mes_anio(mes_actual, anio_actual)
        
        busqueda = self.texto_busqueda.get().lower().strip()
        if not busqueda:
            return todos_los_ingresos
        return [i for i in todos_los_ingresos if busqueda in i["descripcion"].lower()]

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

        # Filas
        for item in datos_pagina:
            bg_match = self.color_primario if self.ingreso_seleccionado_id == item["id"] else "transparent"
            txt_color = "black" if self.ingreso_seleccionado_id == item["id"] else ["gray10", "white"]
            
            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color=bg_match, height=35, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)
            
            lbl_f = ctk.CTkLabel(fila, text=item["fecha"], text_color=txt_color, anchor="w")
            lbl_f.place(relx=0.05, rely=0.5, anchor="w")
            
            lbl_d = ctk.CTkLabel(fila, text=item["descripcion"], text_color=txt_color, anchor="w")
            lbl_d.place(relx=0.35, rely=0.5, anchor="w")
            
            lbl_i = ctk.CTkLabel(fila, text=f"$ {item['importe']:.2f}", text_color=txt_color, anchor="e")
            lbl_i.place(relx=0.95, rely=0.5, anchor="e")
            
            id_actual = item["id"]
            fila.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))
            lbl_f.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))
            lbl_d.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))
            lbl_i.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))

        # Fila del Total
        suma_total = sum(item["importe"] for item in datos_filtrados)
        frame_total = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_total.pack(fill="x", side="top", pady=(10, 0))
        
        lbl_total_txt = ctk.CTkLabel(frame_total, text="TOTAL MES ACTUAL:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_total_txt.place(relx=0.35, rely=0.5, anchor="w")
        
        lbl_total_num = ctk.CTkLabel(frame_total, text=f"$ {suma_total:.2f}", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.color_primario[0])
        lbl_total_num.place(relx=0.95, rely=0.5, anchor="e")

        # Paginación
        frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_paginacion.pack(fill="x", side="bottom")
        
        btn_ant = ctk.CTkButton(frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_primario, text_color="black", hover_color=self.color_primario, state="normal" if self.pagina_actual > 1 else "disabled", command=self.pagina_anterior)
        btn_ant.place(relx=0.4, rely=0.5, anchor="e")
        
        lbl_paginas = ctk.CTkLabel(frame_paginacion, text=f"Página {self.pagina_actual} de {total_paginas}")
        lbl_paginas.place(relx=0.5, rely=0.5, anchor="center")
        
        btn_sig = ctk.CTkButton(frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_primario, text_color="black", hover_color=self.color_primario, state="normal" if self.pagina_actual < total_paginas else "disabled", command=self.pagina_siguiente)
        btn_sig.place(relx=0.6, rely=0.5, anchor="w")

    def seleccionar_fila(self, id_ingreso):
        self.ingreso_seleccionado_id = None if self.ingreso_seleccionado_id == id_ingreso else id_ingreso
        self.actualizar_tabla()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        if self.pagina_actual < len(self.obtener_datos_filtrados()) // self.registros_por_pagina + 1:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def abrir_ventana_registro(self):
        self.ventana_formulario("Registrar Ingreso")

    def abrir_ventana_editar(self):
        if self.ingreso_seleccionado_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla para editar.")
            return
        todos = database.obtener_ingresos()
        ingreso = next(i for i in todos if i["id"] == self.ingreso_seleccionado_id)
        self.ventana_formulario("Editar Ingreso", ingreso)

    def ventana_formulario(self, titulo, datos_edicion=None):
        ventana = ctk.CTkToplevel(self)
        ventana.title(titulo)
        ventana.geometry("400x350")
        ventana.grab_set()
        ventana.resizable(False, False)
        
        ctk.CTkLabel(ventana, text=titulo, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(ventana, text="Fecha (DD-MM-AAAA):", anchor="w").pack(fill="x", padx=40)
        entry_fecha = ctk.CTkEntry(ventana)
        entry_fecha.pack(fill="x", padx=40, pady=(0, 10))
        fecha_hoy = datetime.today().strftime('%d-%m-%Y')
        entry_fecha.insert(0, fecha_hoy if not datos_edicion else datos_edicion["fecha"])
        
        ctk.CTkLabel(ventana, text="Descripción:", anchor="w").pack(fill="x", padx=40)
        entry_desc = ctk.CTkEntry(ventana)
        entry_desc.pack(fill="x", padx=40, pady=(0, 10))
        if datos_edicion: entry_desc.insert(0, datos_edicion["descripcion"])
        
        ctk.CTkLabel(ventana, text="Importe ($):", anchor="w").pack(fill="x", padx=40)
        entry_importe = ctk.CTkEntry(ventana)
        entry_importe.pack(fill="x", padx=40, pady=(0, 20))
        if datos_edicion: entry_importe.insert(0, str(datos_edicion["importe"]))

        def guardar():
            fecha = entry_fecha.get().strip()
            descripcion = entry_desc.get().strip()
            importe_str = entry_importe.get().strip()
            
            if not fecha or not descripcion or not importe_str:
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
                
            if datos_edicion:
                database.actualizar_ingreso(datos_edicion["id"], fecha, descripcion, importe)
            else:
                database.insertar_ingreso(fecha, descripcion, importe)
                
            self.actualizar_tabla()
            ventana.destroy()

        frame_btns = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btns.pack(fill="x", padx=40)
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray30", width=100, command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Guardar", fg_color=self.color_primario, text_color="black", hover_color=self.color_primario, width=100, command=guardar).pack(side="right", padx=5)

    def eliminar_ingreso(self):
        if self.ingreso_seleccionado_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este registro?"):
            database.eliminar_ingreso_db(self.ingreso_seleccionado_id)
            self.ingreso_seleccionado_id = None
            self.actualizar_tabla()