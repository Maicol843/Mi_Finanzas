import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from datetime import datetime
import database

class VistaGraficaEgresos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent

        # Encabezado Centrado Obligatorio
        self.lbl_titulo = ctk.CTkLabel(self, text="Gráfica de Gastos", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10), anchor="center")

        self.lbl_desc = ctk.CTkLabel(
            self, 
            text="Visualización del total de tus gastos acumulados mes a mes.",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_desc.pack(pady=(0, 15), anchor="center")

        # Contenedor para incrustar el lienzo de la gráfica o el mensaje de error
        self.frame_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_canvas.pack(fill="both", expand=True, padx=20, pady=20)

        self.generar_grafica()

    def obtener_totales_historicos(self):
        """
        Extrae y agrupa los egresos pertenecientes ÚNICAMENTE al año actual.
        """
        todos_los_registros = []
        anio_actual = datetime.today().strftime('%Y') # Detecta automáticamente el año en curso
        
        try:
            # Intentamos traer todos los egresos si la función existe
            if hasattr(database, 'obtener_todos_los_egresos'):
                todos_los_registros = database.obtener_todos_los_egresos()
            elif hasattr(database, 'obtener_egresos'):
                todos_los_registros = database.obtener_egresos()
            else:
                # Si no hay función global, iteramos los 12 meses pero clavados al año actual
                for m in range(1, 13):
                    mes_str = f"{m:02d}"
                    registros_mes = database.obtener_egresos_mes_actual(mes_str, anio_actual)
                    if registros_mes:
                        todos_los_registros.extend(registros_mes)
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            
        acumulado_meses = defaultdict(float)
        
        for reg in todos_los_registros:
            try:
                fecha_obj = datetime.strptime(reg["fecha"], "%d-%m-%Y")
                # FILTRO CRUCIAL: Solo tomamos en cuenta los registros que coincidan con el año actual
                if fecha_obj.strftime("%Y") == anio_actual:
                    clave_mes = fecha_obj.strftime("%m-%Y")
                    acumulado_meses[clave_mes] += float(reg["importe"])
            except Exception:
                continue

        # Si no hay datos, retornamos listas vacías para que el generador sepa que no hay registros
        if not acumulado_meses:
            return [], []

        meses_ordenados = sorted(acumulado_meses.keys(), key=lambda x: datetime.strptime(x, "%m-%Y"))
        totales_ordenados = [acumulado_meses[mes] for mes in meses_ordenados]

        return meses_ordenados, totales_ordenados

    def generar_grafica(self):
        # 1. Obtener los datos reales de la base de datos
        meses, totales = self.obtener_totales_historicos()

        # 2. VALIDACIÓN: Si no hay registros válidos, muestra el mensaje de error centrado en lugar de la gráfica
        if not meses or sum(totales) == 0:
            lbl_sin_registros = ctk.CTkLabel(
                self.frame_canvas,
                text="No hay registros de gastos suficientes para generar la gráfica.",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            lbl_sin_registros.place(relx=0.5, rely=0.5, anchor="center")
            return

        # 3. Configurar la estética oscura/clara de Matplotlib acorde a CustomTkinter
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') # Fondo adaptado a modo oscuro por defecto
        ax.set_facecolor('#333333')

        # 4. Dibujar las barras de gastos (Tonalidad Roja de Gastos)
        barras = ax.bar(meses, totales, color="#F44336", width=0.5, edgecolor="white", linewidth=0.7)

        # 5. Configurar etiquetas y diseño de ejes
        ax.set_ylabel("Total Gastado ($)", color="white", fontsize=11, fontweight="bold")
        ax.set_xlabel("Meses Registrados", color="white", fontsize=11, fontweight="bold")
        ax.tick_params(colors="white", labelsize=10)
        ax.grid(True, color="#444444", linestyle="--", linewidth=0.5)

        # Añadir etiquetas de valor sobre cada barra para mejor lectura
        for barra in barras:
            altura = barra.get_height()
            # Ajustar la escala visual de manera limpia si los valores son superiores a cero
            ax.annotate(f"${altura:,.2f}",
                        xy=(barra.get_x() + barra.get_width() / 2, altura),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', color='white', fontsize=9, fontweight="bold")

        plt.tight_layout()

        # 6. Dibujar e incrustar el objeto gráfico dentro del frame de Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)