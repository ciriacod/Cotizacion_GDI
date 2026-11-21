
import tkinter as tk
from tkinter import ttk, messagebox

from database.connection import DatabaseConnection

from services.cliente_service import ClienteService
from services.empleado_service import EmpleadoService
from services.catalogo_service import CatalogoService
from services.producto_servicio_service import ProductoServicioService
from services.parametro_service import ParametroService
from services.cotizacion_service import CotizacionService
from services.reporte_service import ReporteService

from views.clientes_view import ClientesView
from views.dashboard_view import DashboardView
from views.empleados_view import EmpleadosView
from views.catalogos_personal_view import CatalogosPersonalView
from views.catalogos_view import CatalogosView
from views.parametros_view import ParametrosView
from views.cotizaciones_view import CotizacionesView
from views.reportes_view import ReportesView
from views.connection_view import ConnectionView


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()

        self.root.title(
            "JP Cotiza | Gestión de Cotizaciones"
        )

        self.root.geometry("1280x800")
        self.root.minsize(1050, 650)

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

        self.database = DatabaseConnection()

        self.cliente_service = ClienteService(
            self.database
        )

        self.empleado_service = EmpleadoService(
            self.database
        )

        # Servicio de Cargos y Especialidades.
        self.catalogo_personal_service = CatalogoService(
            self.database
        )

        # Servicio de Productos y Servicios.
        self.producto_servicio_service = ProductoServicioService(
            self.database
        )

        # Servicio de los seis catálogos de parámetros.
        self.parametro_service = ParametroService(
            self.database
        )

        self.cotizacion_service = CotizacionService(self.database)
        self.reporte_service = ReporteService(self.database)
        self.database_password = None

        self.configure_styles()
        self.build_interface()
        self.show_connection_page()

    # =================================================
    # ESTILOS
    # =================================================

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
            font=("Segoe UI", 9),
            padding=(12, 10),
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
            font=("Segoe UI", 9, "bold"),
            padding=(12, 10),
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
            background=[
                ("selected", "#DCEBFA")
            ],
            foreground=[
                ("selected", self.colors["navy"])
            ]
        )

    # =================================================
    # ESTRUCTURA PRINCIPAL
    # =================================================

    def build_interface(self):
        self.root.configure(
            background=self.colors["background"]
        )

        self.main_container = tk.Frame(
            self.root,
            bg=self.colors["background"]
        )

        self.main_container.pack(
            fill="both",
            expand=True
        )

        self.sidebar = tk.Frame(
            self.main_container,
            bg=self.colors["navy"],
            width=245
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.build_sidebar()

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

        self.content = tk.Frame(
            self.workspace,
            bg=self.colors["background"]
        )

        self.content.pack(
            fill="both",
            expand=True
        )

    # =================================================
    # MENÚ LATERAL
    # =================================================

    def build_sidebar(self):
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
            text="COTIZACIONES COMERCIALES",
            bg=self.colors["navy"],
            fg="#AFC5DF",
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            padx=20
        )

        tk.Frame(
            self.sidebar,
            bg="#315276",
            height=1
        ).pack(
            fill="x",
            padx=15,
            pady=12
        )

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

        menu_items = [
            ("dashboard", "Dashboard"),
            ("clientes", "Clientes"),
            ("empleados", "Empleados"),
            ("catalogos_personal", "Cargos y Especialidades"),
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
                command=lambda page=page_id: self.show_page(page)
            )

            button.pack(
                fill="x",
                padx=9,
                pady=2
            )

            self.navigation_buttons[page_id] = button

        ttk.Button(
            self.sidebar, text="Conexión / Base de datos", style="JP.Nav.TButton",
            command=self.show_connection_page
        ).pack(fill="x", padx=9, pady=(12, 2))

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
            text="Versión 1.1.0",
            bg=self.colors["navy"],
            fg="#718DAA",
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

    # =================================================
    # BARRA SUPERIOR
    # =================================================

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

    # =================================================
    # CONEXIÓN E INICIALIZACIÓN DE BASE DE DATOS
    # =================================================

    def show_connection_page(self):
        if self.current_page is not None:
            self.current_page.destroy()
        self.page_title.configure(text="Conexión con MySQL")
        self.current_module = "connection"
        self.current_page = ConnectionView(
            self.content, self.database, self._on_database_ready, self.colors
        )
        self.current_page.pack(fill="both", expand=True)

    def _on_database_ready(self, password, result):
        self.database_password = password  # Solo en memoria durante esta ejecución.
        messagebox.showinfo(
            "JP Cotiza listo",
            f"La base de datos '{result['database']}' está preparada.\n"
            "Se verificaron las 21 tablas y se instalaron los procedimientos, triggers y catálogos.",
            parent=self.root,
        )
        self.show_page("dashboard")

    # =================================================
    # NAVEGACIÓN
    # =================================================

    def show_page(self, page_id):
        pages = {
            "dashboard": "Dashboard",
            "clientes": "Gestión de Clientes",
            "empleados": "Gestión de Empleados",
            "catalogos_personal": "Cargos y Especialidades",
            "catalogos": "Productos y Servicios",
            "parametros": "Parámetros del Sistema",
            "cotizaciones": "Gestión de Cotizaciones",
            "reportes": "Consultas y Reportes"
        }

        title = pages.get(
            page_id,
            "Sistema"
        )

        password = self.database_password
        if password is None:
            self.show_connection_page()
            return

        if self.current_page is not None:
            self.current_page.destroy()
            self.current_page = None

        for key, button in self.navigation_buttons.items():
            if key == page_id:
                button.configure(
                    style="JP.NavActive.TButton"
                )
            else:
                button.configure(
                    style="JP.Nav.TButton"
                )

        self.page_title.configure(text=title)
        self.current_module = page_id

        if page_id == "dashboard":
            self.current_page = DashboardView(
                self.content,
                self.colors,
                on_new_quote=lambda: self.show_page("cotizaciones"),
                on_refresh=self._obtener_datos_dashboard
            )
            if self.database_password is not None:
                self.current_page.refresh()

        elif page_id == "clientes":
            self.current_page = ClientesView(
                self.content,
                self.colors,
                self.cliente_service,
                password
            )

        elif page_id == "empleados":
            self.current_page = EmpleadosView(
                self.content,
                self.colors,
                self.empleado_service,
                password
            )

        elif page_id == "catalogos_personal":
            self.current_page = CatalogosPersonalView(
                self.content,
                self.colors,
                self.catalogo_personal_service,
                password
            )

        elif page_id == "catalogos":
            self.current_page = CatalogosView(
                self.content,
                self.colors,
                self.producto_servicio_service,
                password
            )

        elif page_id == "parametros":
            self.current_page = ParametrosView(
                self.content,
                self.colors,
                self.parametro_service,
                password
            )

        elif page_id == "cotizaciones":
            self.current_page = CotizacionesView(
                self.content, self.colors, self.cotizacion_service, password,
                on_saved=self._refrescar_dashboard_si_visible
            )

        elif page_id == "reportes":
            self.current_page = ReportesView(
                self.content, self.colors, self.reporte_service, password
            )

        else:
            messagebox.showwarning("Módulo", "El módulo solicitado no está disponible.", parent=self.root)
            return

        self.current_page.pack(
            fill="both",
            expand=True
        )

    def _obtener_datos_dashboard(self):
        password = self.database_password or self.solicitar_password()
        if password is None:
            raise ConnectionError("Se canceló la conexión con MySQL.")
        stats = self.cotizacion_service.resumen_dashboard(password)
        recent = self.cotizacion_service.recientes(password, 8)
        return stats, recent

    def _refrescar_dashboard_si_visible(self):
        if self.current_module == "dashboard" and self.current_page is not None:
            self.current_page.refresh()

    # =================================================
    # EJECUCIÓN
    # =================================================

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
