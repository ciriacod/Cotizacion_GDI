
import tkinter as tk
from tkinter import ttk, messagebox


class EmpleadosView(ttk.Frame):

    def __init__(self, parent, colors, service, password):
        super().__init__(parent)

        self.colors = colors
        self.service = service
        self.password = password

        self.empleados = []
        self.cargos = []
        self.especialidades = []
        self.empleado_seleccionado = None

        self.configure(padding=(25, 22))

        self.construir_interfaz()
        self.cargar_catalogos()
        self.cargar_empleados()

    # =====================================================
    # INTERFAZ
    # =====================================================

    def construir_interfaz(self):
        header = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header,
            text="Gestión de Empleados",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text=(
                "Administra al personal, sus cargos, "
                "especialidades y credenciales."
            ),
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        content = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        content.pack(fill="both", expand=True)

        form_panel = tk.Frame(
            content,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=340
        )
        form_panel.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )
        form_panel.pack_propagate(False)

        self.construir_formulario(form_panel)

        table_panel = tk.Frame(
            content,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        table_panel.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.construir_tabla(table_panel)

    # =====================================================
    # FORMULARIO
    # =====================================================

    def construir_formulario(self, parent):
        tk.Label(
            parent,
            text="Datos del empleado",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.entries = {}

        fields = [
            ("dni", "DNI", False),
            ("nombre_completo", "Nombre completo", False),
            ("email", "Correo electrónico", False),
            ("telefono", "Teléfono", False)
        ]

        for key, label, secret in fields:
            tk.Label(
                parent,
                text=label,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Segoe UI", 9, "bold")
            ).pack(
                anchor="w",
                padx=20,
                pady=(5, 4)
            )

            entry = ttk.Entry(
                parent,
                font=("Segoe UI", 9),
                show="*" if secret else ""
            )
            entry.pack(
                fill="x",
                padx=20,
                ipady=4
            )

            self.entries[key] = entry

        tk.Label(
            parent,
            text="Cargo",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(9, 4)
        )

        self.cargo_combo = ttk.Combobox(
            parent,
            state="readonly"
        )
        self.cargo_combo.pack(
            fill="x",
            padx=20,
            ipady=3
        )

        tk.Label(
            parent,
            text="Especialidad",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(9, 4)
        )

        self.especialidad_combo = ttk.Combobox(
            parent,
            state="readonly"
        )
        self.especialidad_combo.pack(
            fill="x",
            padx=20,
            ipady=3
        )

        buttons = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        buttons.pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        ttk.Button(
            buttons,
            text="Registrar empleado",
            style="JP.TButton",
            command=self.registrar_empleado
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Guardar cambios",
            command=self.modificar_empleado
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Desactivar empleado",
            command=self.eliminar_empleado
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Limpiar formulario",
            command=self.limpiar_formulario
        ).pack(fill="x", pady=3)

        tk.Label(
            parent,
            text=(
                "El esquema MySQL exige un hash tecnico en EMPLEADO, "
                "pero el aplicativo no utiliza cuentas de acceso."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 8),
            wraplength=280,
            justify="left",
            padx=10,
            pady=9
        ).pack(
            fill="x",
            padx=20,
            pady=(10, 12)
        )

    # =====================================================
    # TABLA
    # =====================================================

    def construir_tabla(self, parent):
        header = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        header.pack(
            fill="x",
            padx=18,
            pady=(18, 12)
        )

        tk.Label(
            header,
            text="Personal registrado",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Actualizar",
            command=self.cargar_empleados
        ).pack(side="right")

        search_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        search_frame.pack(
            fill="x",
            padx=18,
            pady=(0, 8)
        )

        tk.Label(
            search_frame,
            text="Buscar:",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9)
        ).pack(side="left", padx=(0, 8))

        self.search_var = tk.StringVar()

        search = ttk.Entry(
            search_frame,
            textvariable=self.search_var
        )
        search.pack(
            side="left",
            fill="x",
            expand=True
        )

        search.bind(
            "<KeyRelease>",
            lambda event: self.filtrar_empleados()
        )

        self.total_label = tk.Label(
            parent,
            text="Empleados visibles: 0",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        )
        self.total_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 8)
        )

        frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        columns = (
            "id",
            "dni",
            "nombre",
            "email",
            "telefono",
            "cargo",
            "especialidad"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            style="JP.Treeview"
        )

        headings = {
            "id": "ID",
            "dni": "DNI",
            "nombre": "NOMBRE COMPLETO",
            "email": "CORREO",
            "telefono": "TELÉFONO",
            "cargo": "CARGO",
            "especialidad": "ESPECIALIDAD"
        }

        widths = {
            "id": 55,
            "dni": 90,
            "nombre": 190,
            "email": 190,
            "telefono": 100,
            "cargo": 150,
            "especialidad": 160
        }

        for column, label in headings.items():
            self.tree.heading(column, text=label)
            self.tree.column(
                column,
                width=widths[column],
                minwidth=65,
                anchor="w"
            )

        vertical = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )
        horizontal = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )
        horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.seleccionar_empleado
        )

    # =====================================================
    # CARGAR CATÁLOGOS
    # =====================================================

    def cargar_catalogos(self):
        try:
            self.cargos = self.service.listar_cargos(
                self.password
            )

            self.especialidades = (
                self.service.listar_especialidades(
                    self.password
                )
            )

            self.cargo_combo["values"] = [
                item["nombre_cargo"]
                for item in self.cargos
            ]

            self.especialidad_combo["values"] = [
                item["nombre_especialidad"]
                for item in self.especialidades
            ]

        except Exception as error:
            messagebox.showerror(
                "Error de catálogos",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # CARGAR EMPLEADOS
    # =====================================================

    def cargar_empleados(self):
        try:
            self.empleados = self.service.listar_empleados(
                self.password
            )

            self.filtrar_empleados()

        except Exception as error:
            messagebox.showerror(
                "Error",
                (
                    "No se pudieron cargar los empleados.\n\n"
                    f"{error}"
                ),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # BÚSQUEDA
    # =====================================================

    def filtrar_empleados(self):
        texto = self.search_var.get().strip().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        total = 0

        for empleado in self.empleados:
            valores = [
                empleado.get("id_empleado", ""),
                empleado.get("DNI", ""),
                empleado.get("nombre_completo", ""),
                empleado.get("email", ""),
                empleado.get("telefono", ""),
                empleado.get("nombre_cargo", ""),
                empleado.get("nombre_especialidad", "")
            ]

            if texto and not any(
                texto in str(value).lower()
                for value in valores
            ):
                continue

            self.tree.insert(
                "",
                "end",
                iid=str(empleado["id_empleado"]),
                values=tuple(
                    value or ""
                    for value in valores
                )
            )

            total += 1

        self.total_label.config(
            text=(
                f"Empleados visibles: {total} "
                f"de {len(self.empleados)}"
            )
        )

    # =====================================================
    # OBTENER DATOS DEL FORMULARIO
    # =====================================================

    def _id_catalogo_seleccionado(
        self,
        combo,
        catalogo,
        campo_id
    ):
        indice = combo.current()

        if indice < 0 or indice >= len(catalogo):
            return None

        return catalogo[indice].get(campo_id)

    def _obtener_datos(self):
        return {
            "dni": self.entries["dni"].get().strip(),
            "nombre": self.entries["nombre_completo"].get().strip(),
            "email": self.entries["email"].get().strip(),
            "telefono": self.entries["telefono"].get().strip(),

            "id_cargo": self._id_catalogo_seleccionado(
                self.cargo_combo,
                self.cargos,
                "id_cargo"
            ),

            "id_especialidad": self._id_catalogo_seleccionado(
                self.especialidad_combo,
                self.especialidades,
                "id_especialidad"
            )
        }

    # =====================================================
    # SELECCIONAR EMPLEADO
    # =====================================================

    def seleccionar_empleado(self, event=None):
        seleccion = self.tree.selection()

        if not seleccion:
            return

        try:
            empleado = self.service.buscar_empleado(
                self.password,
                seleccion[0]
            )

            if not empleado:
                return

            self.empleado_seleccionado = int(
                empleado["id_empleado"]
            )

            campos = [
                ("dni", empleado.get("DNI", "")),
                (
                    "nombre_completo",
                    empleado.get("nombre_completo", "")
                ),
                ("email", empleado.get("email", "")),
                ("telefono", empleado.get("telefono") or "")
            ]

            for key, value in campos:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, value)

            for index, cargo in enumerate(self.cargos):
                if cargo["id_cargo"] == empleado["id_cargo"]:
                    self.cargo_combo.current(index)
                    break

            for index, especialidad in enumerate(self.especialidades):
                if (
                    especialidad["id_especialidad"]
                    == empleado["id_especialidad"]
                ):
                    self.especialidad_combo.current(index)
                    break

        except Exception as error:
            messagebox.showerror(
                "Error",
                (
                    "No se pudo consultar el empleado.\n\n"
                    f"{error}"
                ),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # REGISTRAR
    # =====================================================

    def registrar_empleado(self):
        datos = self._obtener_datos()

        try:
            nuevo_id = self.service.registrar_empleado(
                self.password,
                datos["dni"],
                datos["nombre"],
                datos["email"],
                datos["telefono"],
                datos["id_cargo"],
                datos["id_especialidad"]
            )

            messagebox.showinfo(
                "Registro correcto",
                f"Empleado registrado. ID: {nuevo_id}",
                parent=self.winfo_toplevel()
            )

            self.limpiar_formulario()
            self.cargar_empleados()

        except Exception as error:
            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # MODIFICAR
    # =====================================================

    def modificar_empleado(self):
        if self.empleado_seleccionado is None:
            messagebox.showwarning(
                "Selecciona un empleado",
                "Selecciona un registro de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        datos = self._obtener_datos()

        confirmar = messagebox.askyesno(
            "Confirmar cambios",
            "¿Deseas guardar los cambios del empleado?",
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        try:
            self.service.modificar_empleado(
                self.password,
                self.empleado_seleccionado,
                datos["dni"],
                datos["nombre"],
                datos["email"],
                datos["telefono"],
                datos["id_cargo"],
                datos["id_especialidad"]
            )

            messagebox.showinfo(
                "Actualización correcta",
                "Los datos del empleado fueron actualizados.",
                parent=self.winfo_toplevel()
            )

            self.limpiar_formulario()
            self.cargar_empleados()

        except Exception as error:
            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # DESACTIVAR
    # =====================================================

    def eliminar_empleado(self):
        if self.empleado_seleccionado is None:
            messagebox.showwarning(
                "Selecciona un empleado",
                "Selecciona un registro de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar desactivación",
            (
                "¿Deseas desactivar este empleado?\n\n"
                "El registro se conservará en MySQL."
            ),
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        try:
            self.service.eliminar_empleado(
                self.password,
                self.empleado_seleccionado
            )

            messagebox.showinfo(
                "Empleado desactivado",
                "El empleado fue desactivado correctamente.",
                parent=self.winfo_toplevel()
            )

            self.limpiar_formulario()
            self.cargar_empleados()

        except Exception as error:
            messagebox.showerror(
                "No se pudo desactivar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # LIMPIAR FORMULARIO
    # =====================================================

    def limpiar_formulario(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

        self.cargo_combo.set("")
        self.especialidad_combo.set("")

        self.empleado_seleccionado = None

        seleccion = self.tree.selection()

        if seleccion:
            self.tree.selection_remove(seleccion)
