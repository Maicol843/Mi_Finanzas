import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import database

# Bibliotecas necesarias para embeber Matplotlib en CustomTkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ModuloGraficaDeudas(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent
        self.color_naranja = "#FD9843"

        # Título Centrado
        self.lbl_titulo = ctk.CTkLabel(
            self, 
            text="Gráfica de Deudas", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.lbl_titulo.pack(pady=(5, 2), anchor="center")

        # Descripción Centrada
        self.lbl_desc = ctk.CTkLabel(
            self, 
            text="Visualización de tus deudas pagadas mes por mes",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.lbl_desc.pack(pady=(0, 20), anchor="center")

        # Contenedor para incrustar el gráfico de barras
        self.frame_grafico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_grafico.pack(fill="both", expand=True, padx=20, pady=10)

        self.generar_grafica_barras()

    def generar_grafica_barras(self):
        # 1. Obtener datos reales desde el historial de pagos de la BD
        try:
            pagos = database.obtener_historial_pagos()
        except Exception:
            pagos = []
        
        # Mapeo estático de los 12 meses en orden cronológico
        meses_nombre = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # VALIDACIÓN TEMPRANA: Si el historial de pagos está vacío
        if not pagos:
            lbl_sin_registros = ctk.CTkLabel(
                self.frame_grafico,
                text="No hay registros de deudas suficientes para generar la grafica",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            lbl_sin_registros.place(relx=0.5, rely=0.5, anchor="center")
            return

        # Obtener el año corriente para filtrar/mostrar de forma íntegra
        anio_actual = datetime.today().year

        # Inicializar el diccionario de totales con todos los meses del año actual en 0.0
        datos_agrupados = {mes: 0.0 for mes in meses_nombre}

        # Sumar los importes de los pagos correspondientes al año en curso
        for p in pagos:
            try:
                fecha_dt = datetime.strptime(p["fecha"], "%d-%m-%Y")
                # Validamos que el pago pertenezca al año actual
                if fecha_dt.year == anio_actual:
                    nombre_mes = meses_nombre[fecha_dt.month - 1]
                    datos_agrupados[nombre_mes] += p["importe"]
            except ValueError:
                continue

        # Separar listas ordenadas para los ejes
        meses_eje_x = meses_nombre
        totales_eje_y = [datos_agrupados[mes] for mes in meses_nombre]

        # VALIDACIÓN SECUNDARIA: Si todos los meses acumulados suman 0
        if sum(totales_eje_y) == 0:
            lbl_sin_registros = ctk.CTkLabel(
                self.frame_grafico,
                text="No hay registros de deudas suficientes para generar la grafica.",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            lbl_sin_registros.place(relx=0.5, rely=0.5, anchor="center")
            return

        # 2. Configuración estética estricta para Modo Oscuro (Previene el fondo blanco)
        plt.rcParams.update({
            'text.color': 'white', 
            'axes.labelcolor': 'white', 
            'xtick.color': 'white', 
            'ytick.color': 'white',
            'figure.facecolor': '#242424', 
            'axes.facecolor': '#2b2b2b'
        })
        
        fig, ax = plt.subplots(figsize=(10, 5))

        # Dibujar gráfico de barras centrado color anaranjado
        barras = ax.bar(meses_eje_x, totales_eje_y, color=self.color_naranja, width=0.6, edgecolor="white", linewidth=0.7)

        # Configurar títulos de ejes y rejilla
        ax.set_ylabel("Total de Importes ($)", fontdict={'weight': 'bold', 'size': 11}, labelpad=10)
        ax.grid(axis='y', linestyle='--', alpha=0.2)
        
        # Ocultar marcos innecesarios
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('gray')
        ax.spines['bottom'].set_color('gray')

        # Rotar ligeramente las etiquetas si fuera necesario por espacio
        plt.xticks(rotation=15)

        # Añadir etiquetas dinámicas únicamente sobre las barras que tienen saldo acumulado > 0
        for barra in barras:
            alto = barra.get_height()
            if alto > 0:
                ax.annotate(
                    f"${alto:.2f}",
                    xy=(barra.get_x() + barra.get_width() / 2, alto),
                    xytext=(0, 4),  
                    textcoords="offset points",
                    ha='center', 
                    va='bottom', 
                    size=9,
                    weight='bold'
                )

        # Ajuste interno de márgenes
        plt.tight_layout()

        # 3. Incrustar el lienzo generado sin fugas de color blanco
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        
        # Ajustamos el widget interno de TK para heredar el fondo oscuro
        widget_tk = canvas.get_tk_widget()
        widget_tk.configure(bg='#242424', highlightthickness=0)
        widget_tk.pack(fill="both", expand=True)