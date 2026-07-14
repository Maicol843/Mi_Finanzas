import tkinter as tk
import customtkinter as ctk
import sys
from datetime import datetime

# --- SOLUCIÓN AL ERROR DE ACCESO DENEGADO / DPI ---
# Forzar a Matplotlib a usar el backend nativo de Tkinter evita que cargue Qt
import matplotlib
matplotlib.use('TkAgg') 

# Importar componentes de Matplotlib para la integración en Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ingresos import ModuloIngresos
from egresos import ModuloEgresos
from ahorros import ModuloAhorros
from deudas import ModuloDeudas 

# Importar el conector y las funciones necesarias de la base de datos
import database

# Configuración inicial de la interfaz (Tema y Color)
ctk.set_appearance_mode("System")  # Detecta automáticamente el modo del sistema (Claro/Oscuro)
ctk.set_default_color_theme("blue")  # Tema de color principal

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Sistema de Gestión Financiera")

        try:
            self.iconbitmap("logo.ico") 
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
        # ----------------------------

        self.geometry("1000 x 700")  
        self.resizable(True, True)

        # -------------------------------------------------------------
        # CONFIGURACIÓN DEL GRID (Diseño de la ventana)
        # -------------------------------------------------------------
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # MARCO DEL MENÚ LATERAL (IZQUIERDO)
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) 

        # Título del Menú
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Mi Finanzas", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 40))

        # Botones del menú lateral
        self.btn_inicio = ctk.CTkButton(self.sidebar_frame, text="Inicio", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_inicio)
        self.btn_inicio.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_ingresos = ctk.CTkButton(self.sidebar_frame, text="Ingresos", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_ingresos)
        self.btn_ingresos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_gastos = ctk.CTkButton(self.sidebar_frame, text="Gastos", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_egresos)
        self.btn_gastos.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_ahorros = ctk.CTkButton(self.sidebar_frame, text="Ahorros", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_ahorros)
        self.btn_ahorros.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_deudas = ctk.CTkButton(self.sidebar_frame, text="Deudas", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_deudas)
        self.btn_deudas.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # -------------------------------------------------------------
        # MARCO DE CONTENIDO PRINCIPAL (DERECHO)
        # -------------------------------------------------------------
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Contenido por defecto (Vista de Inicio)
        self.mostrar_vista_inicio()

    # -------------------------------------------------------------
    # FUNCIONES DE NAVEGACIÓN Y VISTAS
    # -------------------------------------------------------------
    def limpiar_pantalla_principal(self):
        """Elimina los elementos del contenedor principal para cargar una nueva vista."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def actualizar_estilo_botones(self, boton_activo):
        """Cambia visualmente el botón seleccionado para saber dónde estamos."""
        botones = [self.btn_inicio, self.btn_ingresos, self.btn_gastos, self.btn_ahorros, self.btn_deudas]
        for btn in botones:
            if btn == boton_activo:
                btn.configure(fg_color=["#FFCD39", "#ffc107"], text_color="black") 
            else:
                btn.configure(fg_color="transparent", text_color=["gray10", "white"])

    # -------------------------------------------------------------
    # MÉTODOS DE CÁLCULO FILTRADOS POR EL MES ACTUAL
    # -------------------------------------------------------------
    def obtener_total_ingresos(self):
        try:
            mes_actual = datetime.now().strftime("%m")
            anio_actual = datetime.now().strftime("%Y")
            conexion = database.conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT SUM(importe) FROM ingresos 
                WHERE substr(fecha, 4, 2) = ? AND substr(fecha, 7, 4) = ?
            """, (mes_actual, anio_actual))
            total = cursor.fetchone()[0]
            conexion.close()
            return total if total is not None else 0.0
        except Exception:
            return 0.0

    def obtener_total_egresos(self):
        try:
            mes_actual = datetime.now().strftime("%m")
            anio_actual = datetime.now().strftime("%Y")
            conexion = database.conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT SUM(importe) FROM egresos 
                WHERE fecha LIKE ?
            """, (f"%-{mes_actual}-{anio_actual}",))
            total = cursor.fetchone()[0]
            conexion.close()
            return total if total is not None else 0.0
        except Exception:
            return 0.0

    def obtener_total_ahorros(self):
        try:
            mes_actual = datetime.now().strftime("%m")
            anio_actual = datetime.now().strftime("%Y")
            conexion = database.conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT SUM(importe) FROM depositos_ahorro 
                WHERE substr(fecha, 4, 2) = ? AND substr(fecha, 7, 4) = ?
            """, (mes_actual, anio_actual))
            total = cursor.fetchone()[0]
            conexion.close()
            return total if total is not None else 0.0
        except Exception:
            return 0.0

    def obtener_total_deudas(self):
        try:
            mes_actual = datetime.now().strftime("%m")
            anio_actual = datetime.now().strftime("%Y")
            conexion = database.conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT SUM(importe) FROM pagos_deudas 
                WHERE substr(fecha, 4, 2) = ? AND substr(fecha, 7, 4) = ?
            """, (mes_actual, anio_actual))
            total = cursor.fetchone()[0]
            conexion.close()
            return total if total is not None else 0.0
        except Exception:
            return 0.0

    def obtener_gastos_por_tipo(self):
        """Devuelve un diccionario con los totales correspondientes a gastos fijos y variables."""
        gastos_tipo = {"Fijo": 0.0, "Variable": 0.0}
        try:
            mes_actual = datetime.now().strftime("%m")
            anio_actual = datetime.now().strftime("%Y")
            conexion = database.conectar()
            cursor = conexion.cursor()
            
            # SOLUCIÓN: Cambiado 'tipo' por 'categoria'
            cursor.execute("""
                SELECT categoria, SUM(importe) FROM egresos 
                WHERE fecha LIKE ? 
                GROUP BY categoria
            """, (f"%-{mes_actual}-{anio_actual}",))
            
            rows = cursor.fetchall()
            for row in rows:
                # Aseguramos capitalizar para que coincida exactamente con "Fijo" o "Variable"
                cat_nombre = str(row[0]).capitalize()
                if cat_nombre in gastos_tipo:
                    gastos_tipo[cat_nombre] = row[1] if row[1] is not None else 0.0
                    
            conexion.close()
        except Exception as e:
            print(f"Error en obtener_gastos_por_tipo: {e}") # Opcional: para ver errores en consola
        return gastos_tipo

    def mostrar_vista_inicio(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_inicio)
        
        # -------------------------------------------------------------
        # BARRA DE DESPLAZAMIENTO (CTkScrollableFrame)
        # -------------------------------------------------------------
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Título centrado
        lbl_bienvenida = ctk.CTkLabel(
            scroll_frame, 
            text="¡Bienvenido al Sistema Financiero!", 
            font=ctk.CTkFont(size=26, weight="bold")
        )
        lbl_bienvenida.pack(pady=(20, 5), anchor="center")
        
        # --- TRADUCCIÓN DEL MES A ESPAÑOL ---
        meses_espanol = {
            "January": "Enero", "February": "Febrero", "March": "Marzo", 
            "April": "Abril", "May": "Mayo", "June": "Junio", 
            "July": "Julio", "August": "Agosto", "September": "Septiembre", 
            "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
        }
        mes_ingles = datetime.now().strftime("%B")
        nombre_mes = meses_espanol.get(mes_ingles, mes_ingles)
        # -------------------------------------

        lbl_descripcion = ctk.CTkLabel(
            scroll_frame, 
            text=f"Resumen de transacciones correspondientes al mes de {nombre_mes}.", 
            font=ctk.CTkFont(size=15)
        )
        lbl_descripcion.pack(pady=(0, 15), anchor="center")

        # Obtener valores reales actualizados de la BD
        ingresos = self.obtener_total_ingresos()
        gastos = self.obtener_total_egresos()
        ahorros = self.obtener_total_ahorros()
        deudas = self.obtener_total_deudas()
        dict_gastos = self.obtener_gastos_por_tipo()

        # Contenedor para las 4 Cards alineadas horizontalmente
        cards_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        cards_frame.pack(pady=10, padx=10, fill="x")
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cards")

        data_cards = [
            {"titulo": "Ingresos", "valor": ingresos, "color": "#198754", "col": 0},
            {"titulo": "Gastos", "valor": gastos, "color": "#dc3545", "col": 1},
            {"titulo": "Ahorros", "valor": ahorros, "color": "#20c997", "col": 2},
            {"titulo": "Deudas (Pagos)", "valor": deudas, "color": "#fd7e14", "col": 3}
        ]

        for card in data_cards:
            card_item = ctk.CTkFrame(
                cards_frame, 
                corner_radius=12, 
                border_width=2, 
                border_color=card["color"],
                fg_color=["#F0F0F0", "#2B2B2B"]
            )
            card_item.grid(row=0, column=card["col"], padx=8, pady=5, sticky="nsew")
            card_item.grid_columnconfigure(0, weight=1)

            lbl_title = ctk.CTkLabel(card_item, text=card["titulo"], font=ctk.CTkFont(size=14, weight="bold"))
            lbl_title.grid(row=0, column=0, pady=(15, 5), sticky="ew")

            lbl_value = ctk.CTkLabel(card_item, text=f"$ {card['valor']:.2f}", font=ctk.CTkFont(size=20, weight="bold"), text_color=card["color"])
            lbl_value.grid(row=1, column=0, pady=(5, 15), sticky="ew")

        # Configuración de estilos para los gráficos (Claro/Oscuro)
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color_chart = "#2B2B2B" if is_dark else "#F0F0F0"
        text_color_chart = "white" if is_dark else "black"

        # -------------------------------------------------------------
        # PRIMER BLOQUE DE GRÁFICOS: TORTAS (Lado a Lado)
        # -------------------------------------------------------------
        pie_charts_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        pie_charts_frame.pack(pady=10, padx=10, fill="both", expand=True)
        pie_charts_frame.grid_columnconfigure((0, 1), weight=1, uniform="charts")

        # --- PIE 1: IZQUIERDO (Distribución Total) ---
        fig_p1, ax_p1 = plt.subplots(figsize=(4, 4), facecolor=bg_color_chart)
        ax_p1.set_facecolor(bg_color_chart)
        
        valores_p1 = [ingresos, gastos, ahorros, deudas]
        labels_p1 = ["Ingresos", "Gastos", "Ahorros", "Deudas"]
        colors_p1 = ["#198754", "#dc3545", "#20c997", "#fd7e14"]

        if sum(valores_p1) > 0:
            wedges, texts, autotexts = ax_p1.pie(valores_p1, labels=labels_p1, autopct="%1.1f%%", startangle=140, colors=colors_p1, textprops=dict(color=text_color_chart))
            for autotext in autotexts:
                autotext.set_color('white' if is_dark else 'black')
                autotext.set_weight('bold')
        else:
            ax_p1.text(0.5, 0.5, "Sin datos en el mes", ha='center', va='center', color=text_color_chart, fontsize=12)
            ax_p1.axis('off')
        
        ax_p1.set_title("Distribución Financiera del Mes", color=text_color_chart, weight="bold", fontsize=13)
        canvas_p1 = FigureCanvasTkAgg(fig_p1, master=pie_charts_frame)
        canvas_p1.get_tk_widget().grid(row=0, column=0, padx=15, pady=5, sticky="nsew")
        canvas_p1.draw()

        # --- PIE 2: DERECHO (Sobrante vs Gastado vs Ahorrado) ---
        fig_p2, ax_p2 = plt.subplots(figsize=(4, 4), facecolor=bg_color_chart)
        ax_p2.set_facecolor(bg_color_chart)

        resta_sobrante = ingresos - (gastos + ahorros + deudas)
        dinero_sobrante = resta_sobrante if resta_sobrante > 0 else 0.0
        dinero_gastado = gastos + deudas
        dinero_ahorrado = ahorros

        valores_p2 = [dinero_sobrante, dinero_gastado, dinero_ahorrado]
        labels_p2 = ["Sobrante", "Gastado", "Ahorrado"]
        colors_p2 = ["#0d6efd", "#bb2d3b", "#157347"]

        if sum(valores_p2) > 0:
            wedges2, texts2, autotexts2 = ax_p2.pie(valores_p2, labels=labels_p2, autopct="%1.1f%%", startangle=140, colors=colors_p2, textprops=dict(color=text_color_chart))
            for autotext in autotexts2:
                autotext.set_color('white' if is_dark else 'black')
                autotext.set_weight('bold')
        else:
            ax_p2.text(0.5, 0.5, "Sin datos en el mes", ha='center', va='center', color=text_color_chart, fontsize=12)
            ax_p2.axis('off')

        ax_p2.set_title("Estado de los Ingresos", color=text_color_chart, weight="bold", fontsize=13)
        canvas_p2 = FigureCanvasTkAgg(fig_p2, master=pie_charts_frame)
        canvas_p2.get_tk_widget().grid(row=0, column=1, padx=15, pady=5, sticky="nsew")
        canvas_p2.draw()

        # -------------------------------------------------------------
        # SEGUNDO BLOQUE DE GRÁFICOS: BARRAS (Abajo del todo)
        # -------------------------------------------------------------
        bar_charts_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        bar_charts_frame.pack(pady=20, padx=10, fill="both", expand=True)
        bar_charts_frame.grid_columnconfigure((0, 1), weight=1, uniform="charts")

        # --- BARRAS 1: IZQUIERDO (Barras Verticales - Ingresos vs Egresos) ---
        fig_b1, ax_b1 = plt.subplots(figsize=(4, 3.5), facecolor=bg_color_chart)
        ax_b1.set_facecolor(bg_color_chart)
        
        categorias_b1 = ["Ingresos", "Egresos"]
        valores_b1 = [ingresos, gastos]
        colores_b1 = ["#198754", "#dc3545"]

        ax_b1.set_title("Ingresos vs Egresos", color=text_color_chart, weight="bold", fontsize=13)

        # VALIDACIÓN: Verificar si hay registros
        if sum(valores_b1) > 0:
            bars1 = ax_b1.bar(categorias_b1, valores_b1, color=colores_b1, width=0.5)
            ax_b1.tick_params(colors=text_color_chart)
            
            for spine in ["top", "right", "left", "bottom"]:
                ax_b1.spines[spine].set_color(text_color_chart if spine in ["left", "bottom"] else "none")

            for bar in bars1:
                height = bar.get_height()
                ax_b1.text(bar.get_x() + bar.get_width()/2., height, f"${height:,.2f}", 
                         ha="center", va="bottom", color=text_color_chart, fontsize=9, weight="bold")
        else:
            ax_b1.text(0.5, 0.5, "Sin datos en el mes", ha='center', va='center', color=text_color_chart, fontsize=12)
            ax_b1.axis('off')

        canvas_b1 = FigureCanvasTkAgg(fig_b1, master=bar_charts_frame)
        canvas_b1.get_tk_widget().grid(row=0, column=0, padx=15, pady=5, sticky="nsew")
        canvas_b1.draw()

        # --- BARRAS 2: DERECHO (Barras Horizontales - Gastos Fijos vs Variables) ---
        fig_b2, ax_b2 = plt.subplots(figsize=(4, 3.5), facecolor=bg_color_chart)
        ax_b2.set_facecolor(bg_color_chart)

        categorias_b2 = ["Fijo", "Variable"]
        valores_b2 = [dict_gastos["Fijo"], dict_gastos["Variable"]]
        colores_b2 = ["#B02A37", "#dc3545"]

        ax_b2.set_title("Gastos", color=text_color_chart, weight="bold", fontsize=13)

        # VALIDACIÓN: Verificar si hay registros
        if sum(valores_b2) > 0:
            bars2 = ax_b2.barh(categorias_b2, valores_b2, color=colores_b2, height=0.5)
            ax_b2.tick_params(colors=text_color_chart)

            for spine in ["top", "right", "left", "bottom"]:
                ax_b2.spines[spine].set_color(text_color_chart if spine in ["left", "bottom"] else "none")

            for bar in bars2:
                width = bar.get_width()
                ax_b2.text(width, bar.get_y() + bar.get_height()/2., f" ${width:,.2f}", 
                         ha="left", va="center", color=text_color_chart, fontsize=9, weight="bold")
        else:
            ax_b2.text(0.5, 0.5, "Sin datos en el mes", ha='center', va='center', color=text_color_chart, fontsize=12)
            ax_b2.axis('off')

        canvas_b2 = FigureCanvasTkAgg(fig_b2, master=bar_charts_frame)
        canvas_b2.get_tk_widget().grid(row=0, column=1, padx=15, pady=5, sticky="nsew")
        canvas_b2.draw()

    def ir_a_inicio(self):
        self.mostrar_vista_inicio()

    def ir_a_ingresos(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_ingresos)
        self.modulo_ingresos = ModuloIngresos(self.main_frame)
        self.modulo_ingresos.pack(fill="both", expand=True)

    def ir_a_egresos(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_gastos)
        self.modulo_egresos = ModuloEgresos(self.main_frame)
        self.modulo_egresos.pack(fill="both", expand=True)

    def ir_a_ahorros(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_ahorros)
        self.modulo_ahorros = ModuloAhorros(self.main_frame)
        self.modulo_ahorros.pack(fill="both", expand=True)

    def ir_a_deudas(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_deudas)
        
        self.modulo_deudas = ModuloDeudas(self.main_frame)
        self.modulo_deudas.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()