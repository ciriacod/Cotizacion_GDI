
import tkinter as tk
from tkinter import ttk

from views.dashboard_view import DashboardView
from views.placeholder_view import PlaceholderView


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()

        self.root.title(
            "Sistema de Gestión de Cotizaciones JP"
        )

        self.root.geometry("1280x800")
        self.root.minsize(1050, 650)

        # Paleta institucional
        self.colors = {
            "navy": "#16365C",
            "navy_light": "#244B75",
            "blue": "#2563A6",
            "blue_light": "#EAF2FB",
            "background": "#F3F6FA",
            "white": "#FFFFFF",
            "text": "#263445",
            "muted": "#718096",
            "border": "#E2E8F0",
            "success": "#16845B"
        }

        self.current_page = None
        self.current_module = None
        self.navigation_buttons = {}

        self.configure_styles()
        self.build_interface()

        self.show_page("dashboard")

    def configure_styles(self):

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "JP.TButton",
            font=("Segoe UI", 10),
            padding=(12, 10),
            background=self.colors["navy"],
            foreground=self.colors["white"],
            borderwidth=0
        )

        style.map(
            "JP.TButton",
            background=[
                ("active", self.colors["navy_light"])
            ]
        )

        style.configure(
            "JP.Nav.TButton",
            font=("Segoe UI", 10),
            padding=(14, 12),
            background=self.colors["navy"],
            foreground="#DCE6F1",
            anchor="w",
            borderwidth=0
        )

        style.map(
            "JP.Nav.TButton",
            background=[
                ("active", self.colors["navy_light"])
            ],
            foreground=[
                ("active", self.colors["white"])
            ]
        )

        style.configure(
            "JP.NavActive.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 12),
            background=self.colors["blue"],
            foreground=self.colors["white"],
            anchor="w",
            borderwidth=0
        )

        style.configure(
            "JP.Treeview",
            font=("Segoe UI", 9),
            rowheight=32,
            background=self.colors["white"],
            fieldbackground=self.colors["white"],
            foreground=self.colors["text"],
            borderwidth=0
        )

        style.configure(
            "JP.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background=self.colors["blue_light"],
            foreground=self.colors["navy"],
            padding=10,
            relief="flat"
        )

        style.map(
            "JP.Treeview",
            background=[("selected", "#DCEBFA")],
            foreground=[("selected", self.colors["navy"])]
        )

    def build_interface(self):

        self.root.configure(
            background=self.colors["background"]
        )

        # Contenedor general
        self.main_container = tk.Frame(
            self.root,
            bg=self.colors["background"]
        )

        self.main_container.pack(
            fill="both",
            expand=True
        )

        # Menú lateral
        self.sidebar = tk.Frame(
            self.main_container,
            bg=self.colors["navy"],
            width=240
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.build_sidebar()

        # Área principal
        self.workspace = tk.Frame(
            self.main_container,
            bg=self.colors["background"]
        )

        self.workspace.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.build_topbar()

        # Área dinámica de contenido
        self.content = tk.Frame(
            self.workspace,
            bg=self.colors["background"]
        )

        self.content.pack(
            fill="both",
            expand=True
        )

    def build_sidebar(self):

        # Identidad de la empresa
        brand = tk.Frame(
            self.sidebar,
            bg=self.colors["navy"],
            height=105
        )

        brand.pack(fill="x")
        brand.pack_propagate(False)

        tk.Label(
            brand,
            text="JP INGENIERÍA",
            bg=self.colors["navy"],
            fg=self.colors["white"],
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(22, 2)
        )

        tk.Label(
            brand,
            text="GESTIÓN DE COTIZACIONES",
            bg=self.colors["navy"],
            fg="#AFC5DF",
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            padx=20
        )

        # Separador
        tk.Frame(
            self.sidebar,
            bg="#315276",
            height=1
        ).pack(fill="x", padx=15, pady=12)

        tk.Label(
            self.sidebar,
            text="MENÚ PRINCIPAL",
            bg=self.colors["navy"],
            fg="#91A9C3",
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 10)
        )

        # Opciones de navegación
        menu_items = [
            ("dashboard", "Dashboard"),
            ("clientes", "Clientes"),
            ("empleados", "Empleados"),
            ("catalogos", "Productos y servicios"),
            ("parametros", "Parámetros"),
            ("cotizaciones", "Cotizaciones"),
            ("reportes", "Reportes")
        ]

        for page_id, label in menu_items:

            button = ttk.Button(
                self.sidebar,
                text=label,
                style="JP.Nav.TButton",
                command=lambda p=page_id: self.show_page(p)
            )

            button.pack(
                fill="x",
                padx=10,
                pady=2
            )

            self.navigation_buttons[page_id] = button

        # Información inferior
        footer = tk.Frame(
            self.sidebar,
            bg=self.colors["navy"]
        )

        footer.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20
        )

        tk.Label(
            footer,
            text="J.P. INGENIERÍA Y SERVICIOS S.R.L.",
            bg=self.colors["navy"],
            fg="#AFC5DF",
            font=("Segoe UI", 8),
            wraplength=195,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            footer,
            text="Versión 1.0.0",
            bg=self.colors["navy"],
            fg="#718DAA",
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(5, 0))

    def build_topbar(self):

        topbar = tk.Frame(
            self.workspace,
            bg=self.colors["white"],
            height=65,
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )

        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Título del módulo
        self.page_title = tk.Label(
            topbar,
            text="Dashboard",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 14, "bold")
        )

        self.page_title.pack(
            side="left",
            padx=25
        )

        # Usuario
        user_container = tk.Frame(
            topbar,
            bg=self.colors["white"]
        )

        user_container.pack(
            side="right",
            padx=25
        )

        tk.Label(
            user_container,
            text="ASISTENTE COMERCIAL",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="e")

        tk.Label(
            user_container,
            text="Usuario del sistema",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="e")

    def show_page(self, page_id):

        # Eliminar vista anterior
        if self.current_page is not None:
            self.current_page.destroy()

        # Actualizar navegación
        for key, button in self.navigation_buttons.items():

            if key == page_id:
                button.configure(style="JP.NavActive.TButton")
            else:
                button.configure(style="JP.Nav.TButton")

        pages = {
            "dashboard": "Dashboard",
            "clientes": "Gestión de Clientes",
            "empleados": "Gestión de Empleados",
            "catalogos": "Productos y Servicios",
            "parametros": "Parámetros del Sistema",
            "cotizaciones": "Gestión de Cotizaciones",
            "reportes": "Consultas y Reportes"
        }

        title = pages.get(page_id, "Sistema")

        self.page_title.configure(text=title)
        self.current_module = page_id

        if page_id == "dashboard":

            self.current_page = DashboardView(
                self.content,
                self.colors,
                on_new_quote=lambda: self.show_page("cotizaciones")
            )

        else:

            self.current_page = PlaceholderView(
                self.content,
                self.colors,
                title=title,
                module_id=page_id
            )

        self.current_page.pack(
            fill="both",
            expand=True
        )

    def run(self):
        self.root.mainloop()
