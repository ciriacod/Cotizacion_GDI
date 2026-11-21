"""Consulta, visualizacion y exportacion de los diez reportes de negocio."""

import csv
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox, filedialog


class ReportesView(ttk.Frame):
    def __init__(self, parent, colors, service, password):
        super().__init__(parent, padding=16)
        self.colors = colors
        self.service = service
        self.password = password
        self.rows = []
        self._construir()

    def _construir(self):
        ttk.Label(self, text="Consultas y reportes", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(self, text="Diez consultas de negocio definidas para el proceso comercial.", foreground="#64748B").pack(anchor="w", pady=(3, 12))
        filters = ttk.Frame(self)
        filters.pack(fill="x", pady=(0, 10))
        ttk.Label(filters, text="Reporte:").pack(side="left")
        self.reports = dict(self.service.listar_reportes())
        self.report_var = tk.StringVar()
        self.combo = ttk.Combobox(filters, textvariable=self.report_var, state="readonly", width=48, values=[f"{title} [{key}]" for key, title in self.reports.items()])
        self.combo.pack(side="left", padx=7)
        self.combo.bind("<<ComboboxSelected>>", self._report_selected)
        ttk.Label(filters, text="Desde (AAAA-MM-DD):").pack(side="left", padx=(10, 4))
        self.start = ttk.Entry(filters, width=12)
        self.start.pack(side="left")
        ttk.Label(filters, text="Hasta:").pack(side="left", padx=(8, 4))
        self.end = ttk.Entry(filters, width=12)
        self.end.pack(side="left")
        ttk.Button(filters, text="Ejecutar", command=self._run).pack(side="left", padx=8)
        ttk.Button(filters, text="Exportar CSV", command=self._export).pack(side="right")
        today = date.today()
        self.start.insert(0, today.replace(day=1).isoformat())
        self.end.insert(0, today.isoformat())
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill="both", expand=True)
        self.tree = None
        if self.combo["values"]:
            self.combo.current(0)
        self._report_selected()

    def _selected_code(self):
        value = self.report_var.get()
        if "[" in value and value.endswith("]"):
            return value.rsplit("[", 1)[1][:-1].strip()
        return "periodo"

    def _report_selected(self, _event=None):
        code = self._selected_code()
        state = "normal" if code == "periodo" else "disabled"
        self.start.configure(state=state)
        self.end.configure(state=state)

    def _run(self):
        try:
            code = self._selected_code()
            start = self.start.get().strip() if code == "periodo" else None
            end = self.end.get().strip() if code == "periodo" else None
            self.rows = self.service.ejecutar(self.password, code, start, end)
            self._render_table()
        except Exception as error:
            messagebox.showerror("Reporte", str(error), parent=self)

    def _render_table(self):
        for child in self.table_frame.winfo_children():
            child.destroy()
        if not self.rows:
            ttk.Label(self.table_frame, text="La consulta no devolvió registros.", foreground="#64748B").pack(anchor="w", pady=20)
            return
        columns = list(self.rows[0].keys())
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(110, min(240, len(str(col)) * 10 + 35)), anchor="w")
        ybar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        self.table_frame.rowconfigure(0, weight=1)
        self.table_frame.columnconfigure(0, weight=1)
        for index, row in enumerate(self.rows):
            values = [str(value) if value is not None else "" for value in row.values()]
            self.tree.insert("", "end", iid=str(index), values=values)

    def _export(self):
        if not self.rows:
            messagebox.showwarning("Exportar", "Ejecuta un reporte que contenga registros antes de exportar.", parent=self)
            return
        path = filedialog.asksaveasfilename(parent=self, title="Exportar reporte", defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="reporte_cotizaciones.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=list(self.rows[0].keys()))
                writer.writeheader()
                writer.writerows(self.rows)
            messagebox.showinfo("Exportación", f"Reporte exportado en:\n{path}", parent=self)
        except OSError as error:
            messagebox.showerror("Exportación", str(error), parent=self)
