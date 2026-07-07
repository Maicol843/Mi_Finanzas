import tkinter as tk
import customtkinter as ctk
import sys

from ingresos import ModuloIngresos
from egresos import ModuloEgresos
from ahorros import ModuloAhorros

# Configuración inicial de la interfaz (Tema y Color)
ctk.set_appearance_mode("System")  # Detecta automáticamente el modo del sistema (Claro/Oscuro)
ctk.set_default_color_theme("blue")  # Tema de color principal

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Sistema de Gestión Financiera - Ingresos y Egresos")
        self.geometry("1000 x 600")
        self.resizable(True, True)

        # -------------------------------------------------------------
        # CONFIGURACIÓN DEL GRID (Diseño de la ventana)
        # -------------------------------------------------------------
        # El menú ocupará la columna 0 y el contenido la columna 1
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # MARCO DEL MENÚ LATERAL (IZQUIERDO)
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) # Espaciador para empujar botones inferiores

        # Título del Menú
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Mi Finanzas", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 40))

        # Botón: Inicio
        self.btn_inicio = ctk.CTkButton(self.sidebar_frame, text="Inicio", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_inicio)
        self.btn_inicio.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Botón: Ingresos
        self.btn_ingresos = ctk.CTkButton(self.sidebar_frame, text="Ingresos", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_ingresos)
        self.btn_ingresos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Botón: Gastos (Egresos)
        self.btn_gastos = ctk.CTkButton(self.sidebar_frame, text="Gastos", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_egresos)
        self.btn_gastos.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Botón: Ahorros
        self.btn_ahorros = ctk.CTkButton(self.sidebar_frame, text="Ahorros", fg_color="transparent", hover_color=["#FFCD39", "#ffc107"], command=self.ir_a_ahorros)
        self.btn_ahorros.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Botón: Deudas
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
                # Aplicamos tus colores de la imagen image_f666e4.png y forzamos el texto a negro ("black")
                btn.configure(fg_color=["#FFCD39", "#ffc107"], text_color="black") 
            else:
                # Volvemos el fondo transparente y el texto a blanco (o el color por defecto de tu tema)
                btn.configure(fg_color="transparent", text_color=["gray10", "white"])

    def mostrar_vista_inicio(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_inicio)
        
        # Componentes de la vista de Inicio
        lbl_bienvenida = ctk.CTkLabel(self.main_frame, text="¡Bienvenido al Sistema Financiero!", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_bienvenida.pack(pady=(20, 10), anchor="w")
        
        lbl_descripcion = ctk.CTkLabel(self.main_frame, text="Selecciona una opción en el menú izquierdo para comenzar a gestionar tu dinero.", font=ctk.CTkFont(size=14))
        lbl_descripcion.pack(pady=10, anchor="w")

    # Métodos asignados a los botones del menú
    def ir_a_inicio(self):
        self.mostrar_vista_inicio()

    def ir_a_ingresos(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_ingresos)
        
        # Instanciamos y empaquetamos el módulo de ingresos directamente en el panel principal
        self.modulo_ingresos = ModuloIngresos(self.main_frame)
        self.modulo_ingresos.pack(fill="both", expand=True)

    def ir_a_egresos(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_gastos)
        
        # Instanciamos y renderizamos el nuevo módulo de gastos de forma interactiva
        self.modulo_egresos = ModuloEgresos(self.main_frame)
        self.modulo_egresos.pack(fill="both", expand=True)

    def ir_a_ahorros(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_ahorros)
        
        # SOLUCIÓN: Instanciamos y empaquetamos el módulo de ahorros real de forma interactiva
        self.modulo_ahorros = ModuloAhorros(self.main_frame)
        self.modulo_ahorros.pack(fill="both", expand=True)

    def ir_a_deudas(self):
        self.limpiar_pantalla_principal()
        self.actualizar_estilo_botones(self.btn_deudas)
        
        lbl = ctk.CTkLabel(self.main_frame, text="Módulo de Deudas", font=ctk.CTkFont(size=24, weight="bold"))
        lbl.pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()