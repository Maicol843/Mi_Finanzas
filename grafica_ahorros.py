import tkinter as tk
import customtkinter as ctk
import database
from datetime import datetime

# Importaciones para incrustar Matplotlib en CustomTkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ModuloGraficaAhorros(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.parent = parent
        self.color_ahorros = ["#4CAF50", "#45a049"] # Color verde consistente
        
        # Diccionario para ordenar y mostrar las etiquetas de los meses correctamente
        self.meses_nombres = {
            "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr", 
            "05": "May", "06": "Jun", "07": "Jul", "08": "Ago", 
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dic"
        }

        # 1. Contenedor Superior (Botón Volver alineado a la izquierda)
        self.frame_superior = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.frame_superior.pack(fill="x", padx=20, pady=(10, 0))
        self.frame_superior.pack_propagate(False)

        # 2. Título Centrado
        self.lbl_titulo = ctk.CTkLabel(
            self, 
            text="Gráfica de Ahorros", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.lbl_titulo.pack(pady=(10, 5), anchor="center")

        # 3. Descripción Centrada
        self.lbl_descripcion = ctk.CTkLabel(
            self, 
            text="Visualización de tus ahorros acumulados mes por mes", 
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.lbl_descripcion.pack(pady=(0, 20), anchor="center")

        # 4. Contenedor para el gráfico
        self.frame_grafico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_grafico.pack(fill="both", expand=True, padx=20, pady=10)

        # Generar e incrustar la gráfica
        self.crear_grafica()

    def obtener_totales_por_mes(self):
        """Obtiene el historial de depósitos y suma los importes agrupados por mes"""
        try:
            depositos = database.obtener_historial_depositos()
        except Exception:
            depositos = []

        # Inicializamos un diccionario con todos los meses del año en 0.0
        totales_meses = {str(i).zfill(2): 0.0 for i in range(1, 13)}

        for d in depositos:
            try:
                # Extraemos el mes de la fecha (DD-MM-AAAA)
                partes_fecha = d["fecha"].split("-")
                mes = partes_fecha[1].zfill(2)
                if mes in totales_meses:
                    totales_meses[mes] += float(d["importe"])
            except (IndexError, ValueError):
                continue

        # Convertimos a listas ordenadas para Matplotlib
        meses_claves = sorted(totales_meses.keys())
        etiquetas_meses = [self.meses_nombres[m] for m in meses_claves]
        valores_totales = [totales_meses[m] for m in meses_claves]

        return etiquetas_meses, valores_totales

    def crear_grafica(self):
        # Obtener los datos procesados de la base de datos
        meses, totales = self.obtener_totales_por_mes()

        # Configurar el estilo oscuro de la gráfica para que combine con CustomTkinter
        plt.style.use('dark_background')
        
        # Crear la figura y los ejes
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#1a1a1a') # Fondo oscuro de la ventana del gráfico
        ax.set_facecolor('#1a1a1a') # Fondo interno del gráfico

        # Dibujar las barras usando el color verde consistente
        bars = ax.bar(meses, totales, color=self.color_ahorros[0], edgecolor='none', width=0.6)

        # Configurar títulos de los ejes y cuadrícula
        ax.set_ylabel("Monto Total ($)", fontsize=11, color="white", labelpad=10)
        ax.tick_params(axis='both', colors='white', labelsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
        
        # Eliminar los bordes innecesarios de la gráfica para un diseño limpio
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Añadir el valor numérico arriba de cada barra (solo si es mayor a 0)
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'${height:.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # Desplazamiento de 3 puntos hacia arriba
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, color='white', weight='bold')

        # Ajustar los márgenes de la figura automáticamente
        fig.tight_layout()

        # Incrustar la figura en el contenedor de CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)