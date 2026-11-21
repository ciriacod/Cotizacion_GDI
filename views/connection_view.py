"""Asistente inicial para conectar e inicializar la base MySQL."""
import tkinter as tk
from tkinter import ttk, messagebox
from database.installer import DatabaseInstaller


class ConnectionView(ttk.Frame):
    def __init__(self, parent, database, on_connected, colors):
        super().__init__(parent, padding=28)
        self.database = database
        self.on_connected = on_connected
        self.colors = colors
        self._build()

    def _build(self):
        card = ttk.LabelFrame(self, text="Configuración de conexión e instalación inicial", padding=22)
        card.pack(fill="both", expand=True, padx=50, pady=30)
        ttk.Label(card, text="Bienvenido a JP Cotiza", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        ttk.Label(card, text="Conecta con un servidor MySQL 8.0 o superior. Si la base no existe, el asistente la creará e instalará las tablas, triggers, procedimientos y catálogos.", wraplength=760).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        defaults = self.database.config
        self.fields = {}
        specs = [("host", "Servidor / Host", defaults["host"]), ("port", "Puerto", str(defaults["port"])),
                 ("database", "Nombre de la base de datos", defaults["database"]), ("user", "Usuario MySQL", defaults["user"])]
        for r, (key, label, value) in enumerate(specs, start=2):
            ttk.Label(card, text=label).grid(row=r, column=0, sticky="w", pady=7)
            entry = ttk.Entry(card, width=44)
            entry.insert(0, value)
            entry.grid(row=r, column=1, sticky="ew", padx=(18, 0), pady=7)
            self.fields[key] = entry
        ttk.Label(card, text="Contraseña MySQL (no se guarda en el equipo)").grid(row=6, column=0, sticky="w", pady=7)
        self.password = ttk.Entry(card, width=44, show="●")
        self.password.grid(row=6, column=1, sticky="ew", padx=(18, 0), pady=7)
        card.columnconfigure(1, weight=1)
        ttk.Separator(card).grid(row=7, column=0, columnspan=2, sticky="ew", pady=18)
        ttk.Label(card, text="Importante: MySQL Server debe estar instalado y activo. No se necesita Docker ni crear manualmente la base. El usuario MySQL debe tener permisos para crear bases de datos, tablas, triggers y procedimientos.", wraplength=760).grid(row=8, column=0, columnspan=2, sticky="w", pady=(0, 14))
        self.status = tk.StringVar(value="Listo para conectar.")
        ttk.Label(card, textvariable=self.status, foreground="#315B85", wraplength=760).grid(row=9, column=0, columnspan=2, sticky="w", pady=8)
        self.button = ttk.Button(card, text="Conectar e inicializar JP Cotiza", command=self._connect)
        self.button.grid(row=10, column=1, sticky="e", pady=(14, 0))

    def _connect(self):
        password = self.password.get()
        # Se permite contraseña vacía porque algunas instalaciones locales la configuran así.
        try:
            self.button.configure(state="disabled")
            self.status.set("Conectando con el servidor e instalando/verificando la base de datos...")
            self.update_idletasks()
            self.database.save_config(self.fields["host"].get(), self.fields["port"].get(),
                                      self.fields["database"].get(), self.fields["user"].get())
            result = DatabaseInstaller(self.database).initialize(password)
            self.status.set(f"Conexión correcta. Base: {result['database']} | Tablas: {result['tables']} | Procedimientos y triggers verificados.")
            self.button.configure(state="normal")
            self.on_connected(password, result)
        except Exception as exc:
            self.status.set("No se pudo completar la conexión o inicialización.")
            self.button.configure(state="normal")
            messagebox.showerror("No se pudo preparar la base de datos", str(exc), parent=self)
