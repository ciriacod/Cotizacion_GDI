"""Panel de indicadores y actividad comercial reciente."""

import tkinter as tk
from tkinter import ttk, messagebox


class DashboardView(ttk.Frame):
    def __init__(self, parent, colors, on_new_quote=None, on_refresh=None):
        super().__init__(parent, padding=(25, 22))
        self.colors = colors
        self.on_new_quote = on_new_quote
        self.on_refresh = on_refresh
        self.values = {}
        self.build_view()

    def build_view(self):
        header = tk.Frame(self, bg=self.colors["background"])
        header.pack(fill="x", pady=(0, 20))
        title = tk.Frame(header, bg=self.colors["background"])
        title.pack(side="left")
        tk.Label(title, text="Bienvenido al sistema", bg=self.colors["background"], fg=self.colors["text"], font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(title, text="Resumen general de la gestión comercial.", bg=self.colors["background"], fg=self.colors["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
        ttk.Button(header, text="Actualizar indicadores", command=self.refresh).pack(side="right", padx=5)
        ttk.Button(header, text="+ Nueva cotización", style="JP.TButton", command=self.on_new_quote).pack(side="right", padx=5)

        cards_frame = tk.Frame(self, bg=self.colors["background"])
        cards_frame.pack(fill="x", pady=(0, 18))
        cards = [
            ("total_cotizaciones", "Cotizaciones registradas", "0", "Total de registros"),
            ("pendientes", "Cotizaciones pendientes", "0", "En revisión, enviadas o negociación"),
            ("aprobadas", "Cotizaciones aprobadas", "0", "Aceptadas por clientes"),
            ("clientes", "Clientes activos", "0", "Cartera comercial"),
        ]
        for i, (key, title_text, value, hint) in enumerate(cards):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="dashboard")
            card = tk.Frame(cards_frame, bg=self.colors["white"], highlightbackground=self.colors["border"], highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 6 if i < 3 else 0))
            tk.Frame(card, bg=self.colors["blue"], height=4).pack(fill="x")
            body = tk.Frame(card, bg=self.colors["white"])
            body.pack(fill="both", expand=True, padx=14, pady=13)
            tk.Label(body, text=title_text, bg=self.colors["white"], fg=self.colors["muted"], font=("Segoe UI", 9)).pack(anchor="w")
            label = tk.Label(body, text=value, bg=self.colors["white"], fg=self.colors["navy"], font=("Segoe UI", 24, "bold"))
            label.pack(anchor="w", pady=(7, 1))
            self.values[key] = label
            tk.Label(body, text=hint, bg=self.colors["white"], fg="#94A3B8", font=("Segoe UI", 8), wraplength=180, justify="left").pack(anchor="w")

        activity = tk.Frame(self, bg=self.colors["white"], highlightbackground=self.colors["border"], highlightthickness=1)
        activity.pack(fill="both", expand=True)
        top = tk.Frame(activity, bg=self.colors["white"])
        top.pack(fill="x", padx=18, pady=14)
        tk.Label(top, text="Cotizaciones recientes", bg=self.colors["white"], fg=self.colors["text"], font=("Segoe UI", 12, "bold")).pack(side="left")
        self.status = tk.Label(top, text="Conecta con MySQL para consultar los datos.", bg=self.colors["white"], fg=self.colors["muted"], font=("Segoe UI", 8))
        self.status.pack(side="right")
        table_frame = tk.Frame(activity, bg=self.colors["white"])
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        columns = ("numero", "fecha", "cliente", "responsable", "estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="JP.Treeview", height=8)
        headings = {"numero":"N° COTIZACIÓN", "fecha":"FECHA", "cliente":"CLIENTE", "responsable":"RESPONSABLE", "estado":"ESTADO"}
        widths = {"numero":135, "fecha":105, "cliente":260, "responsable":200, "estado":135}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w" if col in ("cliente", "responsable") else "center")
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        if not self.on_refresh:
            return
        try:
            stats, recent = self.on_refresh()
            for key, label in self.values.items():
                label.configure(text=str(stats.get(key, 0)))
            for row in self.tree.get_children():
                self.tree.delete(row)
            for index, quote in enumerate(recent):
                self.tree.insert("", "end", iid=str(index), values=(quote["nmr_cotizacion"], quote["fecha_emision"], quote["razon_social"], quote["responsable"], quote["estado"]))
            self.status.configure(text=f"{len(recent)} registros recientes cargados")
        except Exception as error:
            self.status.configure(text="No se pudo actualizar")
            messagebox.showerror("Dashboard", str(error), parent=self)
