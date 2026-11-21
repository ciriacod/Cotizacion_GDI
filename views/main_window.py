"""Ventana principal de COTIZEP e integración de módulos."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from database.connection import DatabaseConnection
from views.connection_view import ConnectionView
from views.dashboard_view import DashboardView
from views.clientes_view import ClientesView
from views.empleados_view import EmpleadosView
from views.catalogos_view import CatalogosView
from views.catalogos_personal_view import CatalogosPersonalView
from views.parametros_view import ParametrosView
from views.cotizaciones_view import CotizacionesView
from views.reportes_view import ReportesView

from services.cliente_service import ClienteService
from services.empleado_service import EmpleadoService
from services.producto_servicio_service import ProductoServicioService
from services.catalogo_service import CatalogoService
from services.parametro_service import ParametroService
from services.cotizacion_service import CotizacionService
from services.reporte_service import ReporteService


class MainWindow:
    """Aplicación de escritorio: conexión inicial y navegación por módulos."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("COTIZEP | Sistema de Gestión de Cotizaciones")
        self.root.geometry("1360x850")
        self.root.minsize(1100, 700)
        self.database = DatabaseConnection()
        self.password = ""
        self.services = {}
        self.current_page = None
        self.current_module = None
        self.navigation_buttons = {}

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
            "success": "#16845B",
        }
        self.configure_styles()
        self.show_connection()

    def configure_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("JP.TButton", font=("Segoe UI", 10), padding=(12, 10),
                        background=self.colors["navy"], foreground=self.colors["white"], borderwidth=0)
        style.map("JP.TButton", background=[("active", self.colors["navy_light"])])
        style.configure("JP.Nav.TButton", font=("Segoe UI", 10), padding=(14, 12),
                        background=self.colors["navy"], foreground="#DCE6F1", anchor="w", borderwidth=0)
        style.map("JP.Nav.TButton", background=[("active", self.colors["navy_light"])],
                  foreground=[("active", self.colors["white"])])
        style.configure("JP.NavActive.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 12),
                        background=self.colors["blue"], foreground=self.colors["white"], anchor="w", borderwidth=0)
        style.configure("JP.Treeview", font=("Segoe UI", 9), rowheight=30,
                        background=self.colors["white"], fieldbackground=self.colors["white"],
                        foreground=self.colors["text"], borderwidth=0)
        style.configure("JP.Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background=self.colors["blue_light"], foreground=self.colors["navy"],
                        padding=9, relief="flat")

    def show_connection(self):
        for child in self.root.winfo_children():
            child.destroy()
        self.root.configure(background=self.colors["background"])
        self.connection_view = ConnectionView(
            self.root, self.database, self._on_connected, self.colors
        )
        self.connection_view.pack(fill="both", expand=True)

    def _on_connected(self, password, result):
        self.password = password or ""
        self.services = {
            "clientes": ClienteService(self.database),
            "empleados": EmpleadoService(self.database),
            "catalogos": ProductoServicioService(self.database),
            "catalogos_personal": CatalogoService(self.database),
            "parametros": ParametroService(self.database),
            "cotizaciones": CotizacionService(self.database),
            "reportes": ReporteService(self.database),
        }
        self._build_application()
        self.show_page("dashboard")

    def _build_application(self):
        for child in self.root.winfo_children():
            child.destroy()
        self.root.title("COTIZEP | Sistema de Gestión de Cotizaciones")
        self.main_container = tk.Frame(self.root, bg=self.colors["background"])
        self.main_container.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.main_container, bg=self.colors["navy"], width=245)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.workspace = tk.Frame(self.main_container, bg=self.colors["background"])
        self.workspace.pack(side="right", fill="both", expand=True)
        self._build_topbar()
        self.content = tk.Frame(self.workspace, bg=self.colors["background"])
        self.content.pack(fill="both", expand=True)

    def _build_sidebar(self):
        brand = tk.Frame(self.sidebar, bg=self.colors["navy"], height=112)
        brand.pack(fill="x")
        brand.pack_propagate(False)
        tk.Label(brand, text="COTIZEP", bg=self.colors["navy"], fg=self.colors["white"],
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=20, pady=(20, 0))
        tk.Label(brand, text="GESTIÓN DE COTIZACIONES", bg=self.colors["navy"],
                 fg="#AFC5DF", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=21, pady=(1, 0))
        tk.Frame(self.sidebar, bg="#315276", height=1).pack(fill="x", padx=15, pady=12)
        tk.Label(self.sidebar, text="MENÚ PRINCIPAL", bg=self.colors["navy"], fg="#91A9C3",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(4, 9))

        items = [
            ("dashboard", "⌂  Panel principal"),
            ("clientes", "♙  Clientes"),
            ("empleados", "♟  Empleados"),
            ("catalogos", "▦  Productos y servicios"),
            ("catalogos_personal", "▤  Cargos y especialidades"),
            ("parametros", "⚙  Parámetros"),
            ("cotizaciones", "▣  Cotizaciones"),
            ("reportes", "▥  Reportes"),
        ]
        for page_id, label in items:
            button = ttk.Button(self.sidebar, text=label, style="JP.Nav.TButton",
                                command=lambda p=page_id: self.show_page(p))
            button.pack(fill="x", padx=9, pady=2)
            self.navigation_buttons[page_id] = button

        footer = tk.Frame(self.sidebar, bg=self.colors["navy"])
        footer.pack(side="bottom", fill="x", padx=19, pady=18)
        tk.Label(footer, text="J.P. INGENIERÍA Y SERVICIOS S.R.L.", bg=self.colors["navy"],
                 fg="#AFC5DF", font=("Segoe UI", 8), wraplength=200, justify="left").pack(anchor="w")
        tk.Label(footer, text="COTIZEP · Versión 1.2.0", bg=self.colors["navy"],
                 fg="#718DAA", font=("Segoe UI", 8)).pack(anchor="w", pady=(5, 8))
        ttk.Button(footer, text="Cambiar conexión", style="JP.Nav.TButton",
                   command=self.show_connection).pack(fill="x", pady=(0, 2))

    def _build_topbar(self):
        topbar = tk.Frame(self.workspace, bg=self.colors["white"], height=66,
                          highlightbackground=self.colors["border"], highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self.page_title = tk.Label(topbar, text="Panel principal", bg=self.colors["white"],
                                   fg=self.colors["text"], font=("Segoe UI", 14, "bold"))
        self.page_title.pack(side="left", padx=25)
        right = tk.Frame(topbar, bg=self.colors["white"])
        right.pack(side="right", padx=22)
        tk.Label(right, text="COTIZEP", bg=self.colors["white"], fg=self.colors["text"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="e")
        tk.Label(right, text=f"MySQL · {self.database.database_name}", bg=self.colors["white"],
                 fg=self.colors["muted"], font=("Segoe UI", 8)).pack(anchor="e")

    def show_page(self, page_id):
        titles = {
            "dashboard": "Panel principal",
            "clientes": "Gestión de clientes",
            "empleados": "Gestión de empleados",
            "catalogos": "Productos y servicios",
            "catalogos_personal": "Cargos y especialidades",
            "parametros": "Parámetros del sistema",
            "cotizaciones": "Gestión de cotizaciones",
            "reportes": "Consultas y reportes",
        }
        if page_id not in titles:
            return
        if self.current_page is not None:
            self.current_page.destroy()
            self.current_page = None
        self.current_module = page_id
        self.page_title.configure(text=titles[page_id])
        for key, button in self.navigation_buttons.items():
            button.configure(style="JP.NavActive.TButton" if key == page_id else "JP.Nav.TButton")

        try:
            if page_id == "dashboard":
                view = DashboardView(self.content, self.colors,
                                     on_new_quote=lambda: self.show_page("cotizaciones"),
                                     service=self.services["cotizaciones"], password=self.password)
            elif page_id == "clientes":
                view = ClientesView(self.content, self.colors, self.services["clientes"], self.password)
            elif page_id == "empleados":
                view = EmpleadosView(self.content, self.colors, self.services["empleados"], self.password)
            elif page_id == "catalogos":
                view = CatalogosView(self.content, self.colors, self.services["catalogos"], self.password)
            elif page_id == "catalogos_personal":
                view = CatalogosPersonalView(self.content, self.colors,
                                             self.services["catalogos_personal"], self.password)
            elif page_id == "parametros":
                view = ParametrosView(self.content, self.colors, self.services["parametros"], self.password)
            elif page_id == "cotizaciones":
                view = CotizacionesView(self.content, self.colors, self.services["cotizaciones"],
                                        self.password, on_saved=lambda: self._refresh_dashboard())
            else:
                view = ReportesView(self.content, self.colors, self.services["reportes"], self.password)
            self.current_page = view
            view.pack(fill="both", expand=True)
        except Exception as exc:
            messagebox.showerror("No se pudo abrir el módulo", str(exc), parent=self.root)

    def _refresh_dashboard(self):
        if self.current_module == "dashboard":
            self.show_page("dashboard")

    def run(self):
        self.root.mainloop()
