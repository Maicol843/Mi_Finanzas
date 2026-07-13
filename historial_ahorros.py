import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import database

class ModuloHistorialAhorros(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent
        self.color_ahorros = ["#FFCD39", "#ffc107"] # Verde principal y verde hover
        self.registro_seleccionado_id = None  # ID para controlar la selección de la fila
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        
        # Diccionario para convertir nombres de meses a números de dos dígitos
        self.meses_dict = {
            "Todos": "Todos", "Enero": "01", "Febrero": "02", "Marzo": "03", 
            "Abril": "04", "Mayo": "05", "Junio": "06", "Julio": "07", 
            "Agosto": "08", "Septiembre": "09", "Octubre": "10", 
            "Noviembre": "11", "Diciembre": "12"
        }

        # Inicializamos las variables en "Todos"
        self.filtro_tipo = tk.StringVar(value="Todos")
        self.filtro_mes = tk.StringVar(value="Todos")

        # Título Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Historial de Ahorros", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(15, 20), anchor="center")

        # CONTENEDOR DE FILTROS Y ACCIONES
        self.frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_filtros.pack(fill="x", padx=20, pady=5)
        
        # --- BOTONES DE ACCIÓN (LADO IZQUIERDO) ---
        self.btn_editar = ctk.CTkButton(self.frame_filtros, text="Editar", fg_color="gray30", hover_color="gray40", width=90, command=self.abrir_ventana_editar)
        self.btn_editar.pack(side="left", padx=3)
        
        self.btn_eliminar = ctk.CTkButton(self.frame_filtros, text="Eliminar", fg_color="gray30", hover_color="gray40", text_color="white", width=90, command=self.confirmar_eliminacion)
        self.btn_eliminar.pack(side="left", padx=3)
        
        # --- FILTROS DE BÚSQUEDA (LADO DERECHO) ---
        self.btn_buscar = ctk.CTkButton(self.frame_filtros, text="Buscar", fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], text_color="black", width=90, command=self.ejecutar_busqueda)
        self.btn_buscar.pack(side="right", padx=(5, 0))

        opciones_meses = list(self.meses_dict.keys())
        self.combo_mes = ctk.CTkOptionMenu(
            self.frame_filtros, 
            values=opciones_meses, 
            variable=self.filtro_mes, 
            width=120,
            fg_color=self.color_ahorros[0],
            text_color="black",
            button_color=self.color_ahorros[0],
            button_hover_color=self.color_ahorros[1]
        )
        self.combo_mes.pack(side="right", padx=5)
        self.combo_mes.set("Todos") 
        
        self.lbl_mes = ctk.CTkLabel(self.frame_filtros, text="Mes:")
        self.lbl_mes.pack(side="right", padx=(10, 2))

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
            fg_color=self.color_ahorros[0],
            text_color="black",
            button_color=self.color_ahorros[0],
            button_hover_color=self.color_ahorros[1]
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
        self.pagina_actual = 1
        self.registro_seleccionado_id = None
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
            if tipo_sel != "Todos" and d["tipo_ahorro"] != tipo_sel:
                continue
            
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
        
        suma_total_importe = sum(float(item["importe"]) for item in datos_filtrados)
        
        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas
            
        inicio_idx = (self.pagina_actual - 1) * self.registros_por_pagina
        datos_pagina = datos_filtrados[inicio_idx:inicio_idx + self.registros_por_pagina]

        # Cabeceras
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

        # Filas de datos
        for item in datos_pagina:
            # Resaltar la fila seleccionada
            bg_match = self.color_ahorros if self.registro_seleccionado_id == item["id"] else "transparent"
            txt_color = "white" if self.registro_seleccionado_id == item["id"] else ["gray10", "white"]
            imp_color = "white" if self.registro_seleccionado_id == item["id"] else self.color_ahorros[0]

            fila = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color=bg_match, height=40, corner_radius=4)
            fila.pack(fill="x", pady=2, padx=2)
            fila.pack_propagate(False)
            
            lbl_f = ctk.CTkLabel(fila, text=item["fecha"], text_color=txt_color, anchor="w")
            lbl_f.place(relx=0.10, rely=0.5, anchor="w")
            
            lbl_t = ctk.CTkLabel(fila, text=item["tipo_ahorro"], text_color=txt_color, anchor="w")
            lbl_t.place(relx=0.45, rely=0.5, anchor="w")
            
            lbl_i = ctk.CTkLabel(fila, text=f"$ {item['importe']:.2f}", text_color=imp_color, font=ctk.CTkFont(weight="bold"), anchor="e")
            lbl_i.place(relx=0.85, rely=0.5, anchor="e")

            # Eventos de clic para seleccionar fila
            id_actual = item["id"]
            fila.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))
            lbl_f.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))
            lbl_t.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))
            lbl_i.bind("<Button-1>", lambda e, idx=id_actual: self.seleccionar_fila(idx))

        # Fila de Suma Total
        frame_total = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="gray25", height=35, corner_radius=4)
        frame_total.pack(fill="x", pady=(5, 2), padx=2)
        frame_total.pack_propagate(False)

        lbl_total_texto = ctk.CTkLabel(frame_total, text="TOTAL ACUMULADO:", font=ctk.CTkFont(weight="bold", size=13), anchor="w")
        lbl_total_texto.place(relx=0.45, rely=0.5, anchor="w")

        lbl_total_valor = ctk.CTkLabel(frame_total, text=f"$ {suma_total_importe:.2f}", text_color=self.color_ahorros[0], font=ctk.CTkFont(weight="bold", size=14), anchor="e")
        lbl_total_valor.place(relx=0.85, rely=0.5, anchor="e")

        # Paginación Inferior
        frame_paginacion = ctk.CTkFrame(self.frame_tabla_contenedor, fg_color="transparent", height=40)
        frame_paginacion.pack(fill="x", side="bottom")
        
        btn_ant = ctk.CTkButton(frame_paginacion, text="◀ Anterior", width=80, fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], state="normal" if self.pagina_actual > 1 else "disabled", command=self.pagina_anterior)
        btn_ant.place(relx=0.4, rely=0.5, anchor="e")
        
        lbl_paginas = ctk.CTkLabel(frame_paginacion, text=f"Página {self.pagina_actual} de {total_paginas}")
        lbl_paginas.place(relx=0.5, rely=0.5, anchor="center")
        
        btn_sig = ctk.CTkButton(frame_paginacion, text="Siguiente ▶", width=80, fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], state="normal" if self.pagina_actual < total_paginas else "disabled", command=self.pagina_siguiente)
        btn_sig.place(relx=0.6, rely=0.5, anchor="w")

    def seleccionar_fila(self, id_registro):
        self.registro_seleccionado_id = None if self.registro_seleccionado_id == id_registro else id_registro
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

    # --- VENTANA FORMULARIO EDITAR ---
    def abrir_ventana_editar(self):
        if self.registro_seleccionado_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona un registro del historial para editar.")
            return

        datos_completos = self.obtener_datos_filtrados()
        registro_actual = next((d for d in datos_completos if d["id"] == self.registro_seleccionado_id), None)
        
        if not registro_actual:
            return

        try:
            metas = database.obtener_metas_ahorro()
            nombres_ahorros = [m["nombre"] for m in metas]
        except Exception:
            nombres_ahorros = [registro_actual["tipo_ahorro"]]

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar Registro de Historial")
        ventana.geometry("400x380")
        ventana.grab_set()
        ventana.resizable(False, False)
        
        ctk.CTkLabel(ventana, text="Editar Ahorro", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        # Entrada de Fecha
        ctk.CTkLabel(ventana, text="Fecha (DD-MM-AAAA):", anchor="w").pack(fill="x", padx=40)
        entry_fecha = ctk.CTkEntry(ventana)
        entry_fecha.pack(fill="x", padx=40, pady=(0, 10))
        entry_fecha.insert(0, registro_actual["fecha"])
        
        # Select / OptionMenu Tipo de Ahorro
        ctk.CTkLabel(ventana, text="Tipo de Ahorro:", anchor="w").pack(fill="x", padx=40)
        combo_tipo = ctk.CTkOptionMenu(ventana, values=nombres_ahorros, fg_color="gray30", button_color="gray40")
        combo_tipo.pack(fill="x", padx=40, pady=(0, 10))
        combo_tipo.set(registro_actual["tipo_ahorro"])
        
        # Entrada de Importe
        ctk.CTkLabel(ventana, text="Importe ($):", anchor="w").pack(fill="x", padx=40)
        entry_importe = ctk.CTkEntry(ventana)
        entry_importe.pack(fill="x", padx=40, pady=(0, 20))
        entry_importe.insert(0, str(registro_actual["importe"]))

        def guardar_cambios():
            fecha = entry_fecha.get().strip()
            tipo = combo_tipo.get()
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
                database.actualizar_deposito_ahorro(self.registro_seleccionado_id, fecha, tipo, importe)
                self.registro_seleccionado_id = None
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}", parent=ventana)
                return
                
            self.actualizar_tabla()
            ventana.destroy()

        frame_btns = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btns.pack(fill="x", padx=40)
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray30", width=100, command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Guardar", fg_color=self.color_ahorros[0], hover_color=self.color_ahorros[1], text_color="black", width=100, command=guardar_cambios).pack(side="right", padx=5)

    # --- ACCIÓN ELIMINAR REGISTRO ---
    def confirmar_eliminacion(self):
        if self.registro_seleccionado_id is None:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila del historial para eliminar.")
            return

        respuesta = messagebox.askyesno(
            "Confirmar eliminación", 
            "¿Estás seguro de eliminar este registro del historial?\nEsta acción no se puede deshacer."
        )
        
        if respuesta:
            try:
                # La función ahora devuelve un booleano (True si borró, False si era el inicial)
                fue_eliminado = database.eliminar_deposito_ahorro_db(self.registro_seleccionado_id)
                
                if not fue_eliminado:
                    messagebox.showerror(
                        "Error", 
                        "No se puede eliminar este importe ya que es el importe de inicial del tipo de ahorro seleccionado."
                    )
                    return

                self.registro_seleccionado_id = None
                self.actualizar_tabla()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el registro: {e}")