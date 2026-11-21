
import tkinter as tk
from tkinter import ttk, messagebox


class CatalogosPersonalView(ttk.Frame):
    """Administración de los catálogos CARGO y ESPECIALIDAD."""

    def __init__(self, parent, colors, service, password):
        super().__init__(parent)

        self.colors = colors
        self.service = service
        self.password = password

        self.tipo = "Cargo"
        self.registros = []
        self.registro_seleccionado = None

        self.configure(padding=(25, 22))

        self.construir_interfaz()
        self.cargar_registros()

    # =================================================
    # INTERFAZ PRINCIPAL
    # =================================================

    def construir_interfaz(self):
        header = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header,
            text="Cargos y Especialidades",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Administra los catálogos asignables al personal.",
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        selector = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        selector.pack(fill="x", pady=(0, 12))

        tk.Label(
            selector,
            text="Catálogo:",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 10))

        self.tipo_combo = ttk.Combobox(
            selector,
            values=("Cargo", "Especialidad"),
            state="readonly",
            width=24
        )
        self.tipo_combo.set("Cargo")
        self.tipo_combo.pack(side="left")

        self.tipo_combo.bind(
            "<<ComboboxSelected>>",
            self.cambiar_catalogo
        )

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

    # =================================================
    # FORMULARIO
    # =================================================

    def construir_formulario(self, parent):
        tk.Label(
            parent,
            text="Datos del catálogo",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 16)
        )

        tk.Label(
            parent,
            text="Nombre",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(4, 5)
        )

        self.nombre_entry = ttk.Entry(
            parent,
            font=("Segoe UI", 10)
        )
        self.nombre_entry.pack(
            fill="x",
            padx=20,
            ipady=5
        )

        tk.Label(
            parent,
            text="Descripción",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 5)
        )

        desc_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        desc_frame.pack(fill="x", padx=20)

        self.descripcion_text = tk.Text(
            desc_frame,
            height=4,
            wrap="word",
            font=("Segoe UI", 9),
            relief="solid",
            borderwidth=1
        )
        self.descripcion_text.pack(fill="x")

        # Campos exclusivos de ESPECIALIDAD.
        self.special_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )

        tk.Label(
            self.special_frame,
            text="Área de conocimiento",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(10, 5))

        self.area_entry = ttk.Entry(
            self.special_frame
        )
        self.area_entry.pack(fill="x", ipady=4)

        tk.Label(
            self.special_frame,
            text="Certificación requerida (opcional)",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(10, 5))

        self.certificacion_entry = ttk.Entry(
            self.special_frame
        )
        self.certificacion_entry.pack(fill="x", ipady=4)

        self.buttons_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        self.buttons_frame.pack(
            fill="x",
            padx=20,
            pady=(18, 5)
        )

        ttk.Button(
            self.buttons_frame,
            text="Registrar",
            style="JP.TButton",
            command=self.registrar
        ).pack(fill="x", pady=3)

        ttk.Button(
            self.buttons_frame,
            text="Guardar cambios",
            command=self.modificar
        ).pack(fill="x", pady=3)

        ttk.Button(
            self.buttons_frame,
            text="Desactivar",
            command=self.desactivar
        ).pack(fill="x", pady=3)

        ttk.Button(
            self.buttons_frame,
            text="Limpiar formulario",
            command=self.limpiar
        ).pack(fill="x", pady=3)

        tk.Label(
            parent,
            text=(
                "Los registros se desactivan en lugar de borrarse. "
                "Esto conserva las relaciones con empleados."
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
            pady=(12, 15)
        )

    # =================================================
    # TABLA
    # =================================================

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
            text="Registros activos",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Actualizar",
            command=self.cargar_registros
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
            lambda event: self.filtrar()
        )

        self.total_label = tk.Label(
            parent,
            text="Registros visibles: 0",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        )
        self.total_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 8)
        )

        self.table_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        self.crear_treeview()

    def crear_treeview(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if self.tipo == "Cargo":
            self.columns = (
                "id",
                "nombre",
                "descripcion"
            )

            self.headings = {
                "id": "ID",
                "nombre": "CARGO",
                "descripcion": "DESCRIPCIÓN"
            }

            self.widths = {
                "id": 55,
                "nombre": 190,
                "descripcion": 300
            }

        else:
            self.columns = (
                "id",
                "nombre",
                "descripcion",
                "area",
                "certificacion"
            )

            self.headings = {
                "id": "ID",
                "nombre": "ESPECIALIDAD",
                "descripcion": "DESCRIPCIÓN",
                "area": "ÁREA",
                "certificacion": "CERTIFICACIÓN"
            }

            self.widths = {
                "id": 55,
                "nombre": 190,
                "descripcion": 240,
                "area": 150,
                "certificacion": 150
            }

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=self.columns,
            show="headings",
            style="JP.Treeview"
        )

        for column in self.columns:
            self.tree.heading(
                column,
                text=self.headings[column]
            )

            self.tree.column(
                column,
                width=self.widths[column],
                minwidth=65,
                anchor="w"
            )

        vertical = ttk.Scrollbar(
            self.table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        horizontal = ttk.Scrollbar(
            self.table_frame,
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

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.seleccionar
        )

    # =================================================
    # CAMBIAR ENTRE CATÁLOGOS
    # =================================================

    def cambiar_catalogo(self, event=None):
        self.tipo = self.tipo_combo.get()
        self.registro_seleccionado = None

        self.limpiar()

        if self.tipo == "Especialidad":
            self.special_frame.pack(
                fill="x",
                padx=20,
                before=self.buttons_frame
            )
        else:
            self.special_frame.pack_forget()

        self.crear_treeview()
        self.cargar_registros()

    # =================================================
    # CARGAR REGISTROS
    # =================================================

    def cargar_registros(self):
        try:
            if self.tipo == "Cargo":
                self.registros = self.service.listar_cargos(
                    self.password
                )
            else:
                self.registros = self.service.listar_especialidades(
                    self.password
                )

            self.filtrar()

        except Exception as error:
            messagebox.showerror(
                "Error",
                (
                    "No se pudieron cargar los registros.\n\n"
                    f"{error}"
                ),
                parent=self.winfo_toplevel()
            )

    # =================================================
    # BÚSQUEDA Y TABLA
    # =================================================

    def filtrar(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        texto = self.search_var.get().strip().lower()
        total = 0

        for registro in self.registros:

            if self.tipo == "Cargo":
                identificador = registro["id_cargo"]

                valores = (
                    identificador,
                    registro.get("nombre_cargo", ""),
                    registro.get("descripcion") or ""
                )

            else:
                identificador = registro["id_especialidad"]

                valores = (
                    identificador,
                    registro.get("nombre_especialidad", ""),
                    registro.get("descripcion") or "",
                    registro.get("area_conocimiento", ""),
                    registro.get("certificacion_requerida") or ""
                )

            if texto and not any(
                texto in str(valor).lower()
                for valor in valores
            ):
                continue

            self.tree.insert(
                "",
                "end",
                iid=str(identificador),
                values=valores
            )

            total += 1

        self.total_label.config(
            text=(
                f"Registros visibles: {total} "
                f"de {len(self.registros)}"
            )
        )

    # =================================================
    # SELECCIONAR REGISTRO
    # =================================================

    def seleccionar(self, event=None):
        seleccion = self.tree.selection()

        if not seleccion:
            return

        identificador = int(seleccion[0])

        if self.tipo == "Cargo":
            registro = next(
                (
                    item
                    for item in self.registros
                    if item["id_cargo"] == identificador
                ),
                None
            )
        else:
            registro = next(
                (
                    item
                    for item in self.registros
                    if item["id_especialidad"] == identificador
                ),
                None
            )

        if registro is None:
            return

        self.registro_seleccionado = identificador

        if self.tipo == "Cargo":
            nombre = registro.get("nombre_cargo", "")
        else:
            nombre = registro.get("nombre_especialidad", "")

        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, nombre)

        self.descripcion_text.delete("1.0", tk.END)
        self.descripcion_text.insert(
            "1.0",
            registro.get("descripcion") or ""
        )

        if self.tipo == "Especialidad":
            self.area_entry.delete(0, tk.END)
            self.area_entry.insert(
                0,
                registro.get("area_conocimiento", "")
            )

            self.certificacion_entry.delete(0, tk.END)
            self.certificacion_entry.insert(
                0,
                registro.get("certificacion_requerida") or ""
            )

    # =================================================
    # OBTENER DATOS
    # =================================================

    def obtener_datos(self):
        nombre = self.nombre_entry.get().strip()

        descripcion = self.descripcion_text.get(
            "1.0",
            "end-1c"
        ).strip()

        if self.tipo == "Cargo":
            return nombre, descripcion

        area = self.area_entry.get().strip()
        certificacion = self.certificacion_entry.get().strip()

        return (
            nombre,
            descripcion,
            area,
            certificacion
        )

    # =================================================
    # REGISTRAR
    # =================================================

    def registrar(self):
        try:
            datos = self.obtener_datos()

            if self.tipo == "Cargo":
                nuevo_id = self.service.registrar_cargo(
                    self.password,
                    *datos
                )
            else:
                nuevo_id = self.service.registrar_especialidad(
                    self.password,
                    *datos
                )

            messagebox.showinfo(
                "Registro correcto",
                f"Registro creado correctamente. ID: {nuevo_id}",
                parent=self.winfo_toplevel()
            )

            self.limpiar()
            self.cargar_registros()

        except Exception as error:
            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =================================================
    # MODIFICAR
    # =================================================

    def modificar(self):
        if self.registro_seleccionado is None:
            messagebox.showwarning(
                "Selecciona un registro",
                "Selecciona un registro de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar cambios",
            "¿Deseas guardar los cambios?",
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        try:
            datos = self.obtener_datos()

            if self.tipo == "Cargo":
                self.service.modificar_cargo(
                    self.password,
                    self.registro_seleccionado,
                    *datos
                )
            else:
                self.service.modificar_especialidad(
                    self.password,
                    self.registro_seleccionado,
                    *datos
                )

            messagebox.showinfo(
                "Actualización correcta",
                "Los datos fueron actualizados.",
                parent=self.winfo_toplevel()
            )

            self.limpiar()
            self.cargar_registros()

        except Exception as error:
            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =================================================
    # DESACTIVAR
    # =================================================

    def desactivar(self):
        if self.registro_seleccionado is None:
            messagebox.showwarning(
                "Selecciona un registro",
                "Selecciona un registro de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar desactivación",
            (
                "¿Deseas desactivar este registro?\n\n"
                "Se conservará en la base de datos."
            ),
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        try:
            if self.tipo == "Cargo":
                self.service.desactivar_cargo(
                    self.password,
                    self.registro_seleccionado
                )
            else:
                self.service.desactivar_especialidad(
                    self.password,
                    self.registro_seleccionado
                )

            messagebox.showinfo(
                "Registro desactivado",
                "El registro fue desactivado correctamente.",
                parent=self.winfo_toplevel()
            )

            self.limpiar()
            self.cargar_registros()

        except Exception as error:
            messagebox.showerror(
                "No se pudo desactivar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =================================================
    # LIMPIAR
    # =================================================

    def limpiar(self):
        self.nombre_entry.delete(0, tk.END)
        self.descripcion_text.delete("1.0", tk.END)
        self.area_entry.delete(0, tk.END)
        self.certificacion_entry.delete(0, tk.END)

        self.registro_seleccionado = None

        if hasattr(self, "tree"):
            seleccion = self.tree.selection()

            if seleccion:
                self.tree.selection_remove(seleccion)
