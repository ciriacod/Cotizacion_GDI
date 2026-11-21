
import tkinter as tk
from tkinter import ttk, messagebox


class ClientesView(ttk.Frame):

    def __init__(self, parent, colors, service, password):
        super().__init__(parent)

        self.colors = colors
        self.service = service
        self.password = password

        self.clientes = []
        self.distritos = []
        self.cliente_seleccionado = None

        self.configure(padding=(25, 22))

        self.build_view()
        self.cargar_distritos()
        self.cargar_clientes()

    # =====================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # =====================================================

    def build_view(self):
        header = tk.Frame(self, bg=self.colors["background"])
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header,
            text="Gestión de Clientes",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Registra, consulta y administra la información de tus clientes.",
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self, bg=self.colors["background"])
        content.pack(fill="both", expand=True)

        form_panel = tk.Frame(
            content,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=340
        )
        form_panel.pack(side="left", fill="y", padx=(0, 15))
        form_panel.pack_propagate(False)
        self.build_form(form_panel)

        list_panel = tk.Frame(
            content,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        list_panel.pack(side="right", fill="both", expand=True)
        self.build_list(list_panel)

    # =====================================================
    # FORMULARIO DE CLIENTES
    # =====================================================

    def build_form(self, parent):
        tk.Label(
            parent,
            text="Datos del cliente",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 18))

        self.entries = {}

        fields = [
            ("ruc", "RUC"),
            ("razon_social", "Razón social"),
            ("direccion_via", "Dirección")
        ]

        for key, label in fields:
            tk.Label(
                parent,
                text=label,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=20, pady=(5, 5))

            entry = ttk.Entry(parent, font=("Segoe UI", 10))
            entry.pack(fill="x", padx=20, ipady=5)
            self.entries[key] = entry

        tk.Label(
            parent,
            text="Distrito",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=20, pady=(12, 5))

        self.distrito_combo = ttk.Combobox(
            parent,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.distrito_combo.pack(fill="x", padx=20, ipady=4)

        buttons = tk.Frame(parent, bg=self.colors["white"])
        buttons.pack(fill="x", padx=20, pady=(18, 5))

        ttk.Button(
            buttons,
            text="Registrar cliente",
            style="JP.TButton",
            command=self.registrar_cliente
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Guardar cambios",
            command=self.modificar_cliente
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Gestionar contactos",
            command=self.abrir_contactos
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Desactivar cliente",
            command=self.eliminar_cliente
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Limpiar formulario",
            command=self.limpiar_formulario
        ).pack(fill="x", pady=3)

        tk.Label(
            parent,
            text=(
                "Selecciona un cliente de la tabla para editar sus datos "
                "o administrar sus contactos."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 8),
            wraplength=280,
            justify="left",
            padx=12,
            pady=10
        ).pack(fill="x", padx=20, pady=(15, 15))

    # =====================================================
    # TABLA DE CLIENTES
    # =====================================================

    def build_list(self, parent):
        header = tk.Frame(parent, bg=self.colors["white"])
        header.pack(fill="x", padx=18, pady=(18, 12))

        tk.Label(
            header,
            text="Clientes registrados",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Actualizar",
            command=self.cargar_clientes
        ).pack(side="right")

        search_frame = tk.Frame(parent, bg=self.colors["white"])
        search_frame.pack(fill="x", padx=18, pady=(0, 8))

        tk.Label(
            search_frame,
            text="Buscar:",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9)
        ).pack(side="left", padx=(0, 8))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 9)
        )
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind(
            "<KeyRelease>",
            lambda event: self.filtrar_clientes()
        )

        self.total_label = tk.Label(
            parent,
            text="Total de clientes: 0",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        )
        self.total_label.pack(anchor="w", padx=18, pady=(0, 8))

        columns = (
            "codigo",
            "ruc",
            "razon_social",
            "direccion",
            "distrito",
            "provincia",
            "departamento"
        )

        table_frame = tk.Frame(parent, bg=self.colors["white"])
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="JP.Treeview"
        )

        headings = {
            "codigo": "CÓDIGO",
            "ruc": "RUC",
            "razon_social": "RAZÓN SOCIAL",
            "direccion": "DIRECCIÓN",
            "distrito": "DISTRITO",
            "provincia": "PROVINCIA",
            "departamento": "DEPARTAMENTO"
        }

        widths = {
            "codigo": 85,
            "ruc": 105,
            "razon_social": 220,
            "direccion": 180,
            "distrito": 140,
            "provincia": 140,
            "departamento": 145
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                minwidth=75,
                anchor="w"
            )

        vertical_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        horizontal_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.seleccionar_cliente
        )

    # =====================================================
    # DISTRITOS
    # =====================================================

    def cargar_distritos(self):
        try:
            self.distritos = self.service.listar_distritos(
                self.password
            )

            self.distrito_combo["values"] = [
                self.texto_distrito(distrito)
                for distrito in self.distritos
            ]

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los distritos.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    @staticmethod
    def texto_distrito(distrito):
        nombre = distrito.get("nombre_distrito", "")
        provincia = distrito.get("nombre_provincia", "")
        departamento = distrito.get("nombre_departamento", "")
        return f"{nombre} - {provincia} - {departamento}"

    def obtener_codigo_distrito(self):
        indice = self.distrito_combo.current()

        if indice < 0 or indice >= len(self.distritos):
            return None

        return self.distritos[indice].get("cod_distrito")

    # =====================================================
    # CONSULTA Y BÚSQUEDA DE CLIENTES
    # =====================================================

    def cargar_clientes(self):
        try:
            self.clientes = self.service.listar_clientes(
                self.password
            )
            self.filtrar_clientes()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los clientes.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    def filtrar_clientes(self):
        texto = self.search_var.get().strip().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        total_visibles = 0

        for cliente in self.clientes:
            valores_busqueda = [
                str(cliente.get("cod_interno", "")),
                str(cliente.get("ruc", "")),
                str(cliente.get("razon_social", "")),
                str(cliente.get("direccion_via", "")),
                str(cliente.get("nombre_distrito", "")),
                str(cliente.get("nombre_provincia", "")),
                str(cliente.get("nombre_departamento", ""))
            ]

            if texto and not any(
                texto in valor.lower()
                for valor in valores_busqueda
            ):
                continue

            codigo = str(cliente.get("cod_interno", ""))
            if not codigo:
                continue

            self.tree.insert(
                "",
                "end",
                iid=codigo,
                values=(
                    codigo,
                    cliente.get("ruc", ""),
                    cliente.get("razon_social", ""),
                    cliente.get("direccion_via", ""),
                    cliente.get("nombre_distrito", ""),
                    cliente.get("nombre_provincia", ""),
                    cliente.get("nombre_departamento", "")
                )
            )
            total_visibles += 1

        self.total_label.config(
            text=(
                f"Clientes visibles: {total_visibles} "
                f"de {len(self.clientes)}"
            )
        )

    def seleccionar_cliente(self, event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        codigo = seleccion[0]

        try:
            cliente = self.service.buscar_cliente(
                self.password,
                codigo
            )

            if not cliente:
                self.cliente_seleccionado = None
                return

            self.cliente_seleccionado = codigo

            self.entries["ruc"].delete(0, tk.END)
            self.entries["ruc"].insert(0, cliente.get("ruc", ""))

            self.entries["razon_social"].delete(0, tk.END)
            self.entries["razon_social"].insert(
                0,
                cliente.get("razon_social", "")
            )

            self.entries["direccion_via"].delete(0, tk.END)
            self.entries["direccion_via"].insert(
                0,
                cliente.get("direccion_via", "")
            )

            codigo_distrito = str(cliente.get("cod_distrito", ""))
            self.distrito_combo.set("")

            for indice, distrito in enumerate(self.distritos):
                if str(distrito.get("cod_distrito", "")) == codigo_distrito:
                    self.distrito_combo.current(indice)
                    break

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"No se pudo consultar el cliente.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    def obtener_datos_formulario(self):
        return {
            "ruc": self.entries["ruc"].get().strip(),
            "razon_social": self.entries["razon_social"].get().strip(),
            "direccion_via": self.entries["direccion_via"].get().strip(),
            "cod_distrito": self.obtener_codigo_distrito()
        }

    # =====================================================
    # REGISTRAR CLIENTE
    # =====================================================

    def registrar_cliente(self):
        datos = self.obtener_datos_formulario()

        try:
            codigo = self.service.registrar_cliente(
                self.password,
                datos["ruc"],
                datos["razon_social"],
                datos["direccion_via"],
                datos["cod_distrito"]
            )

            messagebox.showinfo(
                "Cliente registrado",
                f"El cliente se registró correctamente.\nCódigo: {codigo}",
                parent=self.winfo_toplevel()
            )

            self.limpiar_formulario()
            self.cargar_clientes()

        except Exception as error:
            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # MODIFICAR CLIENTE
    # =====================================================

    def modificar_cliente(self):
        if not self.cliente_seleccionado:
            messagebox.showwarning(
                "Selecciona un cliente",
                "Selecciona un cliente de la tabla antes de modificarlo.",
                parent=self.winfo_toplevel()
            )
            return

        datos = self.obtener_datos_formulario()

        confirmar = messagebox.askyesno(
            "Confirmar modificación",
            "¿Deseas guardar los cambios de este cliente?",
            parent=self.winfo_toplevel()
        )
        if not confirmar:
            return

        try:
            self.service.modificar_cliente(
                self.password,
                self.cliente_seleccionado,
                datos["ruc"],
                datos["razon_social"],
                datos["direccion_via"],
                datos["cod_distrito"]
            )

            messagebox.showinfo(
                "Actualización correcta",
                "Los datos del cliente fueron actualizados.",
                parent=self.winfo_toplevel()
            )

            self.limpiar_formulario()
            self.cargar_clientes()

        except Exception as error:
            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # DESACTIVAR CLIENTE
    # =====================================================

    def eliminar_cliente(self):
        if not self.cliente_seleccionado:
            messagebox.showwarning(
                "Selecciona un cliente",
                "Selecciona un cliente de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar desactivación",
            (
                f"¿Deseas desactivar al cliente {self.cliente_seleccionado}?\n\n"
                "El cliente y sus contactos dejarán de aparecer en los listados, "
                "pero sus registros se conservarán en la base de datos."
            ),
            parent=self.winfo_toplevel()
        )
        if not confirmar:
            return

        try:
            self.service.eliminar_cliente(
                self.password,
                self.cliente_seleccionado
            )

            messagebox.showinfo(
                "Cliente desactivado",
                "El cliente fue desactivado correctamente.",
                parent=self.winfo_toplevel()
            )

            self.limpiar_formulario()
            self.cargar_clientes()

        except Exception as error:
            messagebox.showerror(
                "No se pudo desactivar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # ABRIR MÓDULO DE CONTACTOS
    # =====================================================

    def abrir_contactos(self):
        if not self.cliente_seleccionado:
            messagebox.showwarning(
                "Selecciona un cliente",
                "Primero selecciona un cliente de la tabla para gestionar sus contactos.",
                parent=self.winfo_toplevel()
            )
            return

        try:
            from views.contactos_view import ContactosView

            cliente = self.service.buscar_cliente(
                self.password,
                self.cliente_seleccionado
            )

            if not cliente:
                messagebox.showwarning(
                    "Cliente no disponible",
                    "No se encontró el cliente seleccionado. Actualiza el listado.",
                    parent=self.winfo_toplevel()
                )
                self.cargar_clientes()
                return

            ContactosView(
                self,
                self.colors,
                self.service,
                self.password,
                self.cliente_seleccionado,
                cliente.get("razon_social", "")
            )

        except Exception as error:
            messagebox.showerror(
                "No se pudo abrir Contactos",
                f"Ocurrió un error al abrir la gestión de contactos.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # LIMPIAR FORMULARIO
    # =====================================================

    def limpiar_formulario(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

        self.distrito_combo.set("")
        self.cliente_seleccionado = None

        seleccion = self.tree.selection()
        if seleccion:
            self.tree.selection_remove(seleccion)
