import tkinter as tk
import customtkinter as ctk
import database

# Importamos los componentes de Matplotlib para la gráfica
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ModuloGrafica(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.color_primario = "#FFCD39" # Color amarillo de tu paleta

        # Título Centrado
        self.lbl_titulo = ctk.CTkLabel(self, text="Gráfica de Ingresos", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(10, 5), anchor="center")
        
        self.lbl_desc = ctk.CTkLabel(
            self, 
            text="Visualización del total de ingresos acumulados mes a mes.",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_desc.pack(pady=(0, 15), anchor="center")

        # Contenedor para el gráfico
        self.frame_grafica_contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_grafica_contenedor.pack(fill="both", expand=True, padx=20, pady=10)

        # Renderizar la gráfica con los datos reales
        self.dibujar_grafica()

    def dibujar_grafica(self):
        # 1. Obtener los datos agrupados de la base de datos
        datos = database.obtener_totales_por_mes()
        
        meses_letras = {
            "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr", "05": "May", "06": "Jun",
            "07": "Jul", "08": "Ago", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dic"
        }

        meses_eje_x = []
        totales_eje_y = []

        if not datos:
            # Si no hay datos, mostramos un mensaje informativo en lugar de una gráfica vacía
            lbl_vacio = ctk.CTkLabel(
                self.frame_grafica_contenedor, 
                text="No hay registros de ingresos suficientes para generar la gráfica.",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            lbl_vacio.pack(expand=True)
            return

        for anio_mes, total in datos:
            # Separamos el año y el mes (ej: '2026-06' -> '2026', '06')
            anio, mes_num = anio_mes.split('-')
            etiqueta = f"{meses_letras.get(mes_num, mes_num)} {anio}"
            meses_eje_x.append(etiqueta)
            totales_eje_y.append(total)

        # 2. Configurar el estilo estético de Matplotlib (Modo Oscuro Adaptable)
        # Usamos un fondo oscuro para que combine perfectamente con CustomTkinter en modo Dark
        plt.rcParams.update({
            'text.color': 'white',
            'axes.labelcolor': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'figure.facecolor': '#242424', # Fondo del contenedor general
            'axes.facecolor': '#1a1a1a'     # Fondo interno del gráfico
        })

        # Crear la figura y los ejes del gráfico
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

        # Dibujar las barras horizontales o verticales (usamos verticales en este caso)
        barras = ax.bar(meses_eje_x, totales_eje_y, color=self.color_primario, edgecolor="white", width=0.5)

        # Configurar etiquetas y cuadrícula
        ax.set_ylabel("Importe Total ($)", fontsize=11, fontweight='bold', labelpad=10)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('gray')
        ax.spines['bottom'].set_color('gray')

        # Agregar el valor numérico arriba de cada barra para que sea fácil de leer
        for barra in barras:
            altura = barra.get_height()
            ax.annotate(f"${altura:.2f}",
                        xy=(barra.get_x() + barra.get_width() / 2, altura),
                        xytext=(0, 3),  # 3 puntos de desfase vertical
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, color='#FFCD39')

        # Ajustar el diseño para que no se corten los textos
        fig.tight_layout()

        # 3. Incrustar el gráfico de Matplotlib dentro del Frame de CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica_contenedor)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)