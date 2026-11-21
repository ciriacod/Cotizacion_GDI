
import tkinter as tk
from tkinter import ttk, messagebox


class CatalogosView(ttk.Frame):
    """Gestión de productos, servicios, unidades y tipos."""

    def __init__(self, parent, colors, service, password):
        super().__init__(parent)

        self.colors = colors
        self.service = service
        self.password = password

        self.items = []
        self.unidades = []
        self.tipos = []

        self.item_seleccionado = None
        self.unidad_seleccionada = None
        self.tipo_seleccionado = None

        self.configure(padding=(22, 18))

        self._cargar_catalogos_iniciales()
        self._construir_interfaz()

        self._cargar_items()
        self._cargar_unidades()
        self._cargar_tipos()

    # =====================================================
    # INTERFAZ PRINCIPAL
    # =====================================================

    def _cargar_catalogos_iniciales(self):
        try:
            self.unidades = self.service.listar_unidades(
                self.password
            )

            self.tipos = self.service.listar_tipos(
                self.password
            )

        except Exception as error:
            messagebox.showerror(
                "Error de catálogos",
                (
                    "No se pudieron cargar unidades y tipos.\n\n"
                    f"{error}"
                ),
                parent=self.winfo_toplevel()
            )

    def _construir_interfaz(self):
        header = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text="Productos y Servicios",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text=(
                "Administra el catálogo comercial, sus precios referenciales "
                "y las unidades de medida."
            ),
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_items = tk.Frame(
            self.notebook,
            bg=self.colors["background"]
        )

        self.tab_unidades = tk.Frame(
            self.notebook,
            bg=self.colors["background"]
        )

        self.tab_tipos = tk.Frame(
            self.notebook,
            bg=self.colors["background"]
        )

        self.notebook.add(
            self.tab_items,
            text="Productos y servicios"
        )

        self.notebook.add(
            self.tab_unidades,
            text="Unidades de medida"
        )

        self.notebook.add(
            self.tab_tipos,
            text="Tipos de producto"
        )

        self._construir_tab_items()
        self._construir_tab_unidades()
        self._construir_tab_tipos()

    # =====================================================
    # COMPONENTES REUTILIZABLES
    # =====================================================

    def _panel(self, parent, width=None):
        panel = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=width if width else 0
        )

        if width:
            panel.pack_propagate(False)

        return panel

    def _label(self, parent, text, pady=(8, 4)):
        tk.Label(
            parent,
            text=text,
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=pady)

    def _crear_entry(self, parent, key, label, show=None):
        self._label(parent, label)

        entry = ttk.Entry(
            parent,
            font=("Segoe UI", 9),
            show=show or ""
        )

        entry.pack(fill="x", ipady=4)
        self.item_entries[key] = entry

        return entry

    # =====================================================
    # PESTAÑA PRODUCTOS Y SERVICIOS
    # =====================================================

    def _construir_tab_items(self):
        body = tk.Frame(
            self.tab_items,
            bg=self.colors["background"]
        )
        body.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=8
        )

        form_panel = self._panel(body, width=355)
        form_panel.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )

        self._construir_form_item(form_panel)

        list_panel = self._panel(body)
        list_panel.pack(
            side="right",
            fill="both",
            expand=True
        )

        self._construir_tabla_items(list_panel)

    def _construir_form_item(self, parent):
        tk.Label(
            parent,
            text="Datos del producto / servicio",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=17,
            pady=(15, 8)
        )

        inner = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        inner.pack(
            fill="both",
            expand=True,
            padx=17,
            pady=(0, 8)
        )

        self.item_entries = {}

        self._crear_entry(
            inner,
            "descripcion",
            "Descripción"
        )

        self._label(inner, "Tipo de elemento")

        self.tipo_item_combo = ttk.Combobox(
            inner,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.tipo_item_combo.pack(fill="x", ipady=3)

        self.tipo_item_combo.bind(
            "<<ComboboxSelected>>",
            self._cambio_tipo_item
        )

        self._label(inner, "Unidad de medida")

        self.unidad_item_combo = ttk.Combobox(
            inner,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.unidad_item_combo.pack(fill="x", ipady=3)

        self._crear_entry(
            inner,
            "precio",
            "Precio referencial"
        )

        self.detalle_producto_frame = tk.Frame(
            inner,
            bg=self.colors["white"]
        )
        self.detalle_producto_frame.pack(fill="x")

        self.product_entries = {}

        self._label(
            self.detalle_producto_frame,
            "Marca",
            pady=(8, 4)
        )

        self.product_entries["marca"] = ttk.Entry(
            self.detalle_producto_frame,
            font=("Segoe UI", 9)
        )
        self.product_entries["marca"].pack(fill="x", ipady=4)

        self._label(
            self.detalle_producto_frame,
            "Modelo",
            pady=(8, 4)
        )

        self.product_entries["modelo"] = ttk.Entry(
            self.detalle_producto_frame,
            font=("Segoe UI", 9)
        )
        self.product_entries["modelo"].pack(fill="x", ipady=4)

        self._label(
            self.detalle_producto_frame,
            "Año (opcional)",
            pady=(8, 4)
        )

        self.product_entries["anio"] = ttk.Entry(
            self.detalle_producto_frame,
            font=("Segoe UI", 9)
        )
        self.product_entries["anio"].pack(fill="x", ipady=4)

        self._label(
            self.detalle_producto_frame,
            "Número de parte",
            pady=(8, 4)
        )

        self.product_entries["nmr_parte"] = ttk.Entry(
            self.detalle_producto_frame,
            font=("Segoe UI", 9)
        )
        self.product_entries["nmr_parte"].pack(fill="x", ipady=4)

        buttons = tk.Frame(
            inner,
            bg=self.colors["white"]
        )
        self.item_buttons_frame = buttons
        buttons.pack(fill="x", pady=(13, 5))

        ttk.Button(
            buttons,
            text="Registrar producto / servicio",
            style="JP.TButton",
            command=self.registrar_item
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Guardar cambios",
            command=self.modificar_item
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Desactivar registro",
            command=self.desactivar_item
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Limpiar formulario",
            command=self.limpiar_item
        ).pack(fill="x", pady=3)

        tk.Label(
            inner,
            text=(
                "El código se genera automáticamente desde MySQL. "
                "Los datos técnicos de marca/modelo solo aplican a equipos "
                "y materiales."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 8),
            wraplength=300,
            justify="left",
            padx=9,
            pady=8
        ).pack(fill="x", pady=(8, 5))

        self._actualizar_combos_item()

    # =====================================================
    # TABLA DE PRODUCTOS Y SERVICIOS
    # =====================================================

    def _construir_tabla_items(self, parent):
        header = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        header.pack(
            fill="x",
            padx=15,
            pady=(15, 10)
        )

        tk.Label(
            header,
            text="Catálogo activo",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Actualizar",
            command=self._cargar_items
        ).pack(side="right")

        search_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        search_frame.pack(
            fill="x",
            padx=15,
            pady=(0, 7)
        )

        tk.Label(
            search_frame,
            text="Buscar:",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9)
        ).pack(side="left", padx=(0, 8))

        self.item_search = tk.StringVar()

        search = ttk.Entry(
            search_frame,
            textvariable=self.item_search
        )
        search.pack(
            side="left",
            fill="x",
            expand=True
        )

        search.bind(
            "<KeyRelease>",
            lambda event: self._filtrar_items()
        )

        self.item_total_label = tk.Label(
            parent,
            text="Registros: 0",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        )
        self.item_total_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 7)
        )

        table_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        columns = (
            "codigo",
            "descripcion",
            "tipo",
            "unidad",
            "precio",
            "marca",
            "modelo",
            "nmr_parte"
        )

        self.item_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="JP.Treeview"
        )

        headings = {
            "codigo": "CÓDIGO",
            "descripcion": "DESCRIPCIÓN",
            "tipo": "TIPO",
            "unidad": "UNIDAD",
            "precio": "PRECIO",
            "marca": "MARCA",
            "modelo": "MODELO",
            "nmr_parte": "N.º PARTE"
        }

        widths = {
            "codigo": 95,
            "descripcion": 260,
            "tipo": 95,
            "unidad": 90,
            "precio": 95,
            "marca": 120,
            "modelo": 120,
            "nmr_parte": 120
        }

        for col in columns:
            self.item_tree.heading(
                col,
                text=headings[col]
            )

            self.item_tree.column(
                col,
                width=widths[col],
                minwidth=70,
                anchor="w"
            )

        vertical = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.item_tree.yview
        )

        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.item_tree.xview
        )

        self.item_tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        self.item_tree.grid(
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

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.item_tree.bind(
            "<<TreeviewSelect>>",
            self._seleccionar_item
        )

    # =====================================================
    # COMBOS DE PRODUCTOS Y SERVICIOS
    # =====================================================

    def _actualizar_combos_item(self):
        self.tipo_item_combo["values"] = [
            f'{tipo["nombre_tipo"]} ({tipo["id_tipo"]})'
            for tipo in self.tipos
            if tipo["nombre_tipo"].strip().casefold() in {"equipo", "material", "servicio"}
        ]

        self.unidad_item_combo["values"] = [
            f'{unidad["abreviatura"]} - {unidad["nombre_unidad"]}'
            for unidad in self.unidades
        ]

        if (
            self.tipo_item_combo["values"]
            and self.tipo_item_combo.current() < 0
        ):
            self.tipo_item_combo.current(0)

        if (
            self.unidad_item_combo["values"]
            and self.unidad_item_combo.current() < 0
        ):
            self.unidad_item_combo.current(0)

        self._cambio_tipo_item()

    def _tipo_item_id(self):
        index = self.tipo_item_combo.current()

        disponibles = [
            item for item in self.tipos
            if item.get("nombre_tipo", "").strip().casefold() in {"equipo", "material", "servicio"}
        ]

        if index < 0 or index >= len(disponibles):
            return None

        return int(disponibles[index]["id_tipo"])

    def _unidad_item_id(self):
        index = self.unidad_item_combo.current()

        if index < 0 or index >= len(self.unidades):
            return None

        return int(self.unidades[index]["id_unidad"])

    def _cambio_tipo_item(self, event=None):
        tipo_id = self._tipo_item_id()

        tipo_nombre = next((t["nombre_tipo"].strip().casefold() for t in self.tipos if int(t["id_tipo"]) == tipo_id), "")
        if tipo_nombre in {"equipo", "material"}:
            if not self.detalle_producto_frame.winfo_manager():
                self.detalle_producto_frame.pack(
                    fill="x",
                    before=self.item_buttons_frame
                )
        else:
            self.detalle_producto_frame.pack_forget()

    # =====================================================
    # CARGAR Y FILTRAR PRODUCTOS
    # =====================================================

    def _cargar_items(self):
        try:
            self.items = self.service.listar_catalogo(
                self.password
            )

            self._filtrar_items()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el catálogo.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    def _filtrar_items(self):
        for iid in self.item_tree.get_children():
            self.item_tree.delete(iid)

        texto = self.item_search.get().strip().lower()
        total = 0

        for item in self.items:
            valores = (
                item.get("cod_pro_ser", ""),
                item.get("descripcion", ""),
                item.get("nombre_tipo", ""),
                item.get("abreviatura", ""),
                item.get("precio_referencial", ""),
                item.get("marca") or "",
                item.get("modelo") or "",
                item.get("nmr_parte") or ""
            )

            if texto and not any(
                texto in str(value).lower()
                for value in valores
            ):
                continue

            self.item_tree.insert(
                "",
                "end",
                iid=item["cod_pro_ser"],
                values=valores
            )

            total += 1

        self.item_total_label.config(
            text=f"Registros visibles: {total} de {len(self.items)}"
        )

    # =====================================================
    # SELECCIONAR PRODUCTO O SERVICIO
    # =====================================================

    def _seleccionar_item(self, event=None):
        seleccion = self.item_tree.selection()

        if not seleccion:
            return

        codigo = seleccion[0]

        item = next(
            (
                registro for registro in self.items
                if registro["cod_pro_ser"] == codigo
            ),
            None
        )

        if item is None:
            return

        self.item_seleccionado = codigo

        self.item_entries["descripcion"].delete(0, tk.END)
        self.item_entries["descripcion"].insert(
            0,
            item.get("descripcion", "")
        )

        self.item_entries["precio"].delete(0, tk.END)
        self.item_entries["precio"].insert(
            0,
            str(item.get("precio_referencial", ""))
        )

        disponibles = [
            t for t in self.tipos
            if t["nombre_tipo"].strip().casefold() in {"equipo", "material", "servicio"}
        ]

        for index, tipo in enumerate(disponibles):
            if int(tipo["id_tipo"]) == int(item["id_tipo"]):
                self.tipo_item_combo.current(index)
                break

        # Se conserva la clasificación original del registro.
        self.tipo_item_combo.configure(state="disabled")

        for index, unidad in enumerate(self.unidades):
            if int(unidad["id_unidad"]) == int(item["id_unidad"]):
                self.unidad_item_combo.current(index)
                break

        self._cambio_tipo_item()

        for key in ("marca", "modelo", "anio", "nmr_parte"):
            self.product_entries[key].delete(0, tk.END)

            value = item.get(key)

            if value is not None:
                self.product_entries[key].insert(
                    0,
                    str(value)
                )

    # =====================================================
    # OBTENER DATOS DEL FORMULARIO
    # =====================================================

    def _datos_item_formulario(self):
        return {
            "descripcion": self.item_entries["descripcion"].get().strip(),
            "id_unidad": self._unidad_item_id(),
            "id_tipo": self._tipo_item_id(),
            "precio": self.item_entries["precio"].get().strip(),
            "marca": self.product_entries["marca"].get().strip(),
            "modelo": self.product_entries["modelo"].get().strip(),
            "anio": self.product_entries["anio"].get().strip(),
            "nmr_parte": self.product_entries["nmr_parte"].get().strip()
        }

    # =====================================================
    # REGISTRAR PRODUCTO / SERVICIO
    # =====================================================

    def registrar_item(self):
        datos = self._datos_item_formulario()

        try:
            codigo = self.service.registrar_item(
                self.password,
                datos["descripcion"],
                datos["id_unidad"],
                datos["id_tipo"],
                datos["precio"],
                datos["marca"],
                datos["modelo"],
                datos["anio"],
                datos["nmr_parte"]
            )

            messagebox.showinfo(
                "Registro correcto",
                (
                    "Registro creado correctamente.\n"
                    f"Código generado: {codigo}"
                ),
                parent=self.winfo_toplevel()
            )

            self.limpiar_item()
            self._cargar_items()

        except Exception as error:
            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # MODIFICAR PRODUCTO / SERVICIO
    # =====================================================

    def modificar_item(self):
        if not self.item_seleccionado:
            messagebox.showwarning(
                "Selecciona un registro",
                "Selecciona un producto o servicio de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar modificación",
            "¿Deseas guardar los cambios de este registro?",
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        datos = self._datos_item_formulario()

        try:
            self.service.modificar_item(
                self.password,
                self.item_seleccionado,
                datos["descripcion"],
                datos["id_unidad"],
                datos["id_tipo"],
                datos["precio"],
                datos["marca"],
                datos["modelo"],
                datos["anio"],
                datos["nmr_parte"]
            )

            messagebox.showinfo(
                "Actualización correcta",
                "El registro fue actualizado correctamente.",
                parent=self.winfo_toplevel()
            )

            self.limpiar_item()
            self._cargar_items()

        except Exception as error:
            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # DESACTIVAR PRODUCTO / SERVICIO
    # =====================================================

    def desactivar_item(self):
        if not self.item_seleccionado:
            messagebox.showwarning(
                "Selecciona un registro",
                "Selecciona un producto o servicio de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar desactivación",
            (
                "¿Deseas desactivar este registro?\n\n"
                "Si ya fue usado en una cotización, el registro histórico "
                "se conservará y dejará de estar disponible en el catálogo."
            ),
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        try:
            self.service.desactivar_item(
                self.password,
                self.item_seleccionado
            )

            messagebox.showinfo(
                "Registro desactivado",
                "El producto o servicio fue desactivado.",
                parent=self.winfo_toplevel()
            )

            self.limpiar_item()
            self._cargar_items()

        except Exception as error:
            messagebox.showerror(
                "No se pudo desactivar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # LIMPIAR FORMULARIO DE PRODUCTOS
    # =====================================================

    def limpiar_item(self):
        for entry in self.item_entries.values():
            entry.delete(0, tk.END)

        for entry in self.product_entries.values():
            entry.delete(0, tk.END)

        self.item_seleccionado = None

        self.tipo_item_combo.configure(state="readonly")

        if self.tipo_item_combo["values"]:
            self.tipo_item_combo.current(0)

        if self.unidad_item_combo["values"]:
            self.unidad_item_combo.current(0)

        selection = self.item_tree.selection()

        if selection:
            self.item_tree.selection_remove(selection)

        self._cambio_tipo_item()

    # =====================================================
    # PESTAÑA UNIDADES DE MEDIDA
    # =====================================================

    def _construir_tab_unidades(self):
        body = tk.Frame(
            self.tab_unidades,
            bg=self.colors["background"]
        )
        body.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=8
        )

        form = self._panel(body, width=310)
        form.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )

        tk.Label(
            form,
            text="Unidad de medida",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=17,
            pady=(18, 14)
        )

        inner = tk.Frame(
            form,
            bg=self.colors["white"]
        )
        inner.pack(
            fill="x",
            padx=17
        )

        self.unidad_nombre_entry = self._entry_unidad(
            inner,
            "Nombre de unidad"
        )

        self.unidad_abrev_entry = self._entry_unidad(
            inner,
            "Abreviatura"
        )

        buttons = tk.Frame(
            inner,
            bg=self.colors["white"]
        )
        buttons.pack(fill="x", pady=(18, 5))

        ttk.Button(
            buttons,
            text="Registrar unidad",
            style="JP.TButton",
            command=self._registrar_unidad
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Guardar cambios",
            command=self._modificar_unidad
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Desactivar unidad",
            command=self._desactivar_unidad
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Limpiar",
            command=self._limpiar_unidad
        ).pack(fill="x", pady=3)

        tk.Label(
            inner,
            text=(
                "Las abreviaturas son únicas y admiten hasta 5 caracteres. "
                "No desactives una unidad que deba seguir disponible para "
                "nuevos registros."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 8),
            wraplength=260,
            justify="left",
            padx=9,
            pady=8
        ).pack(fill="x", pady=(15, 5))

        listing = self._panel(body)
        listing.pack(
            side="right",
            fill="both",
            expand=True
        )

        self._construir_tabla_unidades(listing)

    def _entry_unidad(self, parent, label):
        self._label(parent, label)

        entry = ttk.Entry(
            parent,
            font=("Segoe UI", 9)
        )
        entry.pack(fill="x", ipady=4)

        return entry

    def _construir_tabla_unidades(self, parent):
        header = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        header.pack(
            fill="x",
            padx=15,
            pady=(15, 10)
        )

        tk.Label(
            header,
            text="Unidades activas",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Actualizar",
            command=self._cargar_unidades
        ).pack(side="right")

        self.unidad_tree = ttk.Treeview(
            parent,
            columns=("id", "nombre", "abreviatura"),
            show="headings",
            style="JP.Treeview"
        )

        for col, label, width in (
            ("id", "ID", 60),
            ("nombre", "UNIDAD DE MEDIDA", 220),
            ("abreviatura", "ABREVIATURA", 120)
        ):
            self.unidad_tree.heading(
                col,
                text=label
            )

            self.unidad_tree.column(
                col,
                width=width,
                minwidth=60,
                anchor="w"
            )

        self.unidad_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.unidad_tree.bind(
            "<<TreeviewSelect>>",
            self._seleccionar_unidad
        )

    def _cargar_unidades(self):
        try:
            self.unidades = self.service.listar_unidades(
                self.password
            )

            if hasattr(self, "unidad_tree"):
                for iid in self.unidad_tree.get_children():
                    self.unidad_tree.delete(iid)

                for unidad in self.unidades:
                    self.unidad_tree.insert(
                        "",
                        "end",
                        iid=str(unidad["id_unidad"]),
                        values=(
                            unidad["id_unidad"],
                            unidad["nombre_unidad"],
                            unidad["abreviatura"]
                        )
                    )

            if hasattr(self, "unidad_item_combo"):
                self._actualizar_combos_item()

        except Exception as error:
            messagebox.showerror(
                "Error de unidades",
                str(error),
                parent=self.winfo_toplevel()
            )

    def _seleccionar_unidad(self, event=None):
        selection = self.unidad_tree.selection()

        if not selection:
            return

        selected_id = int(selection[0])

        unidad = next(
            (
                u for u in self.unidades
                if int(u["id_unidad"]) == selected_id
            ),
            None
        )

        if unidad is None:
            return

        self.unidad_seleccionada = selected_id

        self.unidad_nombre_entry.delete(0, tk.END)
        self.unidad_nombre_entry.insert(
            0,
            unidad["nombre_unidad"]
        )

        self.unidad_abrev_entry.delete(0, tk.END)
        self.unidad_abrev_entry.insert(
            0,
            unidad["abreviatura"]
        )

    def _registrar_unidad(self):
        try:
            nuevo_id = self.service.registrar_unidad(
                self.password,
                self.unidad_nombre_entry.get(),
                self.unidad_abrev_entry.get()
            )

            messagebox.showinfo(
                "Registro correcto",
                f"Unidad registrada. ID: {nuevo_id}",
                parent=self.winfo_toplevel()
            )

            self._limpiar_unidad()
            self._cargar_unidades()

        except Exception as error:
            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=self.winfo_toplevel()
            )

    def _modificar_unidad(self):
        if self.unidad_seleccionada is None:
            messagebox.showwarning(
                "Selecciona una unidad",
                "Selecciona una unidad de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        try:
            self.service.modificar_unidad(
                self.password,
                self.unidad_seleccionada,
                self.unidad_nombre_entry.get(),
                self.unidad_abrev_entry.get()
            )

            messagebox.showinfo(
                "Actualización correcta",
                "Unidad actualizada.",
                parent=self.winfo_toplevel()
            )

            self._limpiar_unidad()
            self._cargar_unidades()

        except Exception as error:
            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self.winfo_toplevel()
            )

    def _desactivar_unidad(self):
        if self.unidad_seleccionada is None:
            messagebox.showwarning(
                "Selecciona una unidad",
                "Selecciona una unidad de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        if not messagebox.askyesno(
            "Confirmar desactivación",
            "¿Deseas desactivar esta unidad de medida?",
            parent=self.winfo_toplevel()
        ):
            return

        try:
            self.service.desactivar_unidad(
                self.password,
                self.unidad_seleccionada
            )

            messagebox.showinfo(
                "Unidad desactivada",
                "La unidad fue desactivada.",
                parent=self.winfo_toplevel()
            )

            self._limpiar_unidad()
            self._cargar_unidades()

        except Exception as error:
            messagebox.showerror(
                "No se pudo desactivar",
                str(error),
                parent=self.winfo_toplevel()
            )

    def _limpiar_unidad(self):
        self.unidad_nombre_entry.delete(0, tk.END)
        self.unidad_abrev_entry.delete(0, tk.END)

        self.unidad_seleccionada = None

        selection = self.unidad_tree.selection()

        if selection:
            self.unidad_tree.selection_remove(selection)

    # =====================================================
    # PESTAÑA TIPOS DE PRODUCTO
    # =====================================================

    def _construir_tab_tipos(self):
        body = tk.Frame(
            self.tab_tipos,
            bg=self.colors["background"]
        )
        body.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=8
        )

        form = self._panel(body, width=340)
        form.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )

        tk.Label(
            form,
            text="Tipo de producto",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=17,
            pady=(18, 14)
        )

        inner = tk.Frame(
            form,
            bg=self.colors["white"]
        )
        inner.pack(fill="x", padx=17)

        self.tipo_nombre_entry = self._entry_tipo(
            inner,
            "Nombre del tipo"
        )

        self._label(inner, "Descripción")

        self.tipo_descripcion_text = tk.Text(
            inner,
            height=5,
            wrap="word",
            font=("Segoe UI", 9),
            relief="solid",
            borderwidth=1
        )
        self.tipo_descripcion_text.pack(fill="x")

        ttk.Button(
            inner,
            text="Guardar cambios",
            style="JP.TButton",
            command=self._modificar_tipo
        ).pack(fill="x", pady=(16, 4))

        ttk.Button(
            inner,
            text="Limpiar selección",
            command=self._limpiar_tipo
        ).pack(fill="x", pady=4)

        tk.Label(
            inner,
            text=(
                "Los tres tipos existentes tienen IDs reservados por el "
                "trigger que genera los códigos EQU, MAT y SER. En esta "
                "versión se pueden editar sus nombres y descripciones, "
                "pero no crear ni eliminar tipos nuevos."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 8),
            wraplength=285,
            justify="left",
            padx=9,
            pady=8
        ).pack(fill="x", pady=(14, 5))

        listing = self._panel(body)
        listing.pack(
            side="right",
            fill="both",
            expand=True
        )

        header = tk.Frame(
            listing,
            bg=self.colors["white"]
        )
        header.pack(
            fill="x",
            padx=15,
            pady=(15, 10)
        )

        tk.Label(
            header,
            text="Tipos activos",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Actualizar",
            command=self._cargar_tipos
        ).pack(side="right")

        self.tipo_tree = ttk.Treeview(
            listing,
            columns=("id", "nombre", "descripcion"),
            show="headings",
            style="JP.Treeview"
        )

        for col, label, width in (
            ("id", "ID", 60),
            ("nombre", "TIPO", 170),
            ("descripcion", "DESCRIPCIÓN", 360)
        ):
            self.tipo_tree.heading(
                col,
                text=label
            )

            self.tipo_tree.column(
                col,
                width=width,
                minwidth=70,
                anchor="w"
            )

        self.tipo_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.tipo_tree.bind(
            "<<TreeviewSelect>>",
            self._seleccionar_tipo
        )

    def _entry_tipo(self, parent, label):
        self._label(parent, label)

        entry = ttk.Entry(
            parent,
            font=("Segoe UI", 9)
        )
        entry.pack(fill="x", ipady=4)

        return entry

    def _cargar_tipos(self):
        try:
            self.tipos = self.service.listar_tipos(
                self.password
            )

            if hasattr(self, "tipo_tree"):
                for iid in self.tipo_tree.get_children():
                    self.tipo_tree.delete(iid)

                for tipo in self.tipos:
                    self.tipo_tree.insert(
                        "",
                        "end",
                        iid=str(tipo["id_tipo"]),
                        values=(
                            tipo["id_tipo"],
                            tipo["nombre_tipo"],
                            tipo.get("descripcion") or ""
                        )
                    )

            if hasattr(self, "tipo_item_combo"):
                self._actualizar_combos_item()

        except Exception as error:
            messagebox.showerror(
                "Error de tipos",
                str(error),
                parent=self.winfo_toplevel()
            )

    def _seleccionar_tipo(self, event=None):
        selection = self.tipo_tree.selection()

        if not selection:
            return

        selected_id = int(selection[0])

        tipo = next(
            (
                t for t in self.tipos
                if int(t["id_tipo"]) == selected_id
            ),
            None
        )

        if tipo is None:
            return

        self.tipo_seleccionado = selected_id

        self.tipo_nombre_entry.delete(0, tk.END)
        self.tipo_nombre_entry.insert(
            0,
            tipo["nombre_tipo"]
        )

        self.tipo_descripcion_text.delete("1.0", tk.END)
        self.tipo_descripcion_text.insert(
            "1.0",
            tipo.get("descripcion") or ""
        )

    def _modificar_tipo(self):
        if self.tipo_seleccionado is None:
            messagebox.showwarning(
                "Selecciona un tipo",
                "Selecciona un tipo de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        try:
            descripcion = self.tipo_descripcion_text.get(
                "1.0",
                "end-1c"
            )

            self.service.modificar_tipo(
                self.password,
                self.tipo_seleccionado,
                self.tipo_nombre_entry.get(),
                descripcion
            )

            messagebox.showinfo(
                "Actualización correcta",
                "Tipo actualizado.",
                parent=self.winfo_toplevel()
            )

            self._limpiar_tipo()
            self._cargar_tipos()

        except Exception as error:
            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self.winfo_toplevel()
            )

    def _limpiar_tipo(self):
        self.tipo_nombre_entry.delete(0, tk.END)
        self.tipo_descripcion_text.delete("1.0", tk.END)

        self.tipo_seleccionado = None

        selection = self.tipo_tree.selection()

        if selection:
            self.tipo_tree.selection_remove(selection)
