
import tkinter as tk
from tkinter import ttk


class PlaceholderView(ttk.Frame):

    MODULES = {

        "clientes": {
            "description": (
                "Administra la información comercial "
                "de los clientes de la empresa."
            ),
            "features": [
                "Registrar nuevos clientes.",
                "Consultar y buscar clientes.",
                "Modificar información comercial.",
                "Gestionar contactos asociados."
            ]
        },

        "empleados": {
            "description": (
                "Administra la información del personal "
                "responsable de las cotizaciones."
            ),
            "features": [
                "Registrar empleados.",
                "Consultar información del personal.",
                "Asignar cargos y especialidades.",
                "Modificar registros existentes."
            ]
        },

        "catalogos": {
            "description": (
                "Administra los productos y servicios "
                "disponibles para cotización."
            ),
            "features": [
                "Registrar productos.",
                "Registrar servicios.",
                "Gestionar tipos de productos.",
                "Gestionar unidades de medida.",
                "Consultar precios referenciales."
            ]
        },

        "parametros": {
            "description": (
                "Configura los parámetros utilizados "
                "durante la elaboración de cotizaciones."
            ),
            "features": [
                "Tipos de cotización.",
                "Orígenes de solicitud.",
                "Monedas.",
                "Formas de pago.",
                "Estados de cotización.",
                "Garantías."
            ]
        },

        "cotizaciones": {
            "description": (
                "Gestiona la elaboración, consulta y "
                "seguimiento de propuestas comerciales."
            ),
            "features": [
                "Registrar nuevas cotizaciones.",
                "Agregar productos y servicios.",
                "Calcular importes.",
                "Modificar cotizaciones.",
                "Actualizar estados.",
                "Consultar documentos comerciales."
            ]
        },

        "reportes": {
            "description": (
                "Consulta información estadística "
                "sobre la actividad comercial."
            ),
            "features": [
                "Cotizaciones por periodo.",
                "Cotizaciones por estado.",
                "Clientes con mayor actividad.",
                "Productos y servicios más cotizados.",
                "Cotizaciones próximas a vencer.",
                "Montos cotizados por moneda."
            ]
        }
    }

    def __init__(
        self,
        parent,
        colors,
        title,
        module_id
    ):

        super().__init__(parent)

        self.colors = colors
        self.title = title
        self.module_id = module_id

        self.configure(
            padding=(30, 28)
        )

        self.build_view()

    def build_view(self):

        module = self.MODULES.get(
            self.module_id,
            {}
        )

        description = module.get(
            "description",
            "Módulo del sistema."
        )

        features = module.get(
            "features",
            []
        )

        # Encabezado
        tk.Label(
            self,
            text=self.title,
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        tk.Label(
            self,
            text=description,
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10),
            wraplength=800,
            justify="left"
        ).pack(
            anchor="w",
            pady=(7, 25)
        )

        # Panel principal
        panel = tk.Frame(
            self,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )

        panel.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            panel,
            text="Funcionalidades del módulo",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 15)
        )

        for feature in features:

            row = tk.Frame(
                panel,
                bg=self.colors["white"]
            )

            row.pack(
                fill="x",
                padx=28,
                pady=7
            )

            tk.Label(
                row,
                text="•",
                bg=self.colors["white"],
                fg=self.colors["blue"],
                font=("Segoe UI", 14, "bold")
            ).pack(side="left")

            tk.Label(
                row,
                text=feature,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Segoe UI", 10)
            ).pack(
                side="left",
                padx=10
            )

        # Aviso
        tk.Label(
            panel,
            text=(
                "Este módulo está preparado para su "
                "implementación en las siguientes etapas."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 9),
            padx=15,
            pady=12,
            wraplength=700,
            justify="left"
        ).pack(
            anchor="w",
            padx=25,
            pady=(30, 25)
        )
