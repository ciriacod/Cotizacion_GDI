
import tkinter as tk
from tkinter import ttk


class DashboardView(ttk.Frame):

    def __init__(self, parent, colors, on_new_quote=None, service=None, password=""):

        super().__init__(
            parent,
            style="TFrame"
        )

        self.colors = colors
        self.on_new_quote = on_new_quote
        self.service = service
        self.password = password
        self.card_values = {}

        self.configure(
            padding=(25, 22)
        )

        self.build_view()

    def build_view(self):

        # Encabezado del Dashboard
        header = tk.Frame(
            self,
            bg=self.colors["background"]
        )

        header.pack(
            fill="x",
            pady=(0, 22)
        )

        title_container = tk.Frame(
            header,
            bg=self.colors["background"]
        )

        title_container.pack(side="left")

        tk.Label(
            title_container,
            text="Bienvenido al sistema",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_container,
            text="Resumen general de la gestión comercial.",
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        ttk.Button(
            header,
            text="+ Nueva cotización",
            style="JP.TButton",
            command=self.on_new_quote
        ).pack(
            side="right",
            anchor="center"
        )

        # Tarjetas de indicadores
        cards_container = tk.Frame(
            self,
            bg=self.colors["background"]
        )

        cards_container.pack(
            fill="x",
            pady=(0, 22)
        )

        cards = [
            ("Cotizaciones registradas", "—", "Total de registros"),
            ("Cotizaciones pendientes", "—", "En proceso de atención"),
            ("Cotizaciones aprobadas", "—", "Aceptadas por clientes"),
            ("Clientes registrados", "—", "Cartera de clientes")
        ]

        for column in range(4):
            cards_container.grid_columnconfigure(
                column,
                weight=1,
                uniform="cards"
            )

        for index, (title, value, description) in enumerate(cards):

            card = tk.Frame(
                cards_container,
                bg=self.colors["white"],
                highlightbackground=self.colors["border"],
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(0 if index == 0 else 7, 7 if index < 3 else 0)
            )

            tk.Frame(
                card,
                bg=self.colors["blue"],
                height=4
            ).pack(fill="x")

            body = tk.Frame(
                card,
                bg=self.colors["white"]
            )

            body.pack(
                fill="both",
                expand=True,
                padx=15,
                pady=15
            )

            tk.Label(
                body,
                text=title,
                bg=self.colors["white"],
                fg=self.colors["muted"],
                font=("Segoe UI", 9)
            ).pack(anchor="w")

            value_label = tk.Label(
                body,
                text=value,
                bg=self.colors["white"],
                fg=self.colors["navy"],
                font=("Segoe UI", 25, "bold")
            )
            value_label.pack(anchor="w", pady=(8, 2))
            self.card_values[title] = value_label

            tk.Label(
                body,
                text=description,
                bg=self.colors["white"],
                fg="#94A3B8",
                font=("Segoe UI", 8)
            ).pack(anchor="w")

        # Actividad reciente
        activity_container = tk.Frame(
            self,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )

        activity_container.pack(
            fill="both",
            expand=True
        )

        activity_header = tk.Frame(
            activity_container,
            bg=self.colors["white"]
        )

        activity_header.pack(
            fill="x",
            padx=20,
            pady=(17, 12)
        )

        tk.Label(
            activity_header,
            text="Cotizaciones recientes",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        tk.Label(
            activity_header,
            text="Últimos registros",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8)
        ).pack(side="right")

        # Tabla
        table_container = tk.Frame(
            activity_container,
            bg=self.colors["white"]
        )

        table_container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        columns = (
            "numero",
            "fecha",
            "cliente",
            "responsable",
            "estado"
        )

        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="JP.Treeview",
            height=8
        )

        headings = {
            "numero": "N° COTIZACIÓN",
            "fecha": "FECHA",
            "cliente": "CLIENTE",
            "responsable": "RESPONSABLE",
            "estado": "ESTADO"
        }

        widths = {
            "numero": 130,
            "fecha": 110,
            "cliente": 230,
            "responsable": 180,
            "estado": 130
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Mensaje temporal
        self.empty_message = tk.Label(
            activity_container,
            text="Los registros de cotizaciones aparecerán aquí al conectar la base de datos.",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        )

        self.empty_message.pack(
            pady=(0, 18)
        )
        self._load_data()

    def _load_data(self):
        """Carga indicadores y actividad reciente desde procedimientos almacenados."""
        if self.service is None:
            return
        try:
            summary = self.service.resumen_dashboard(self.password) or {}
            mapping = {
                "Cotizaciones registradas": "total_cotizaciones",
                "Cotizaciones pendientes": "pendientes",
                "Cotizaciones aprobadas": "aprobadas",
                "Clientes registrados": "clientes",
            }
            for title, key in mapping.items():
                self.card_values[title].configure(text=str(summary.get(key, 0) or 0))

            recent = self.service.recientes(self.password, 8) or []
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in recent:
                self.tree.insert("", "end", values=(
                    row.get("nmr_cotizacion", ""),
                    row.get("fecha_emision", ""),
                    row.get("razon_social", ""),
                    row.get("responsable", ""),
                    row.get("estado", ""),
                ))
            self.empty_message.configure(
                text="" if recent else "Todavía no hay cotizaciones registradas."
            )
        except Exception as exc:
            self.empty_message.configure(
                text=f"No se pudo cargar el resumen: {exc}"
            )
