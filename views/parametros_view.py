
import tkinter as tk
from tkinter import ttk, messagebox


class ParametrosView(ttk.Frame):
    """Administración de los catálogos de parámetros del sistema."""

    CONFIGURACION = {
        "tipo_cotizacion": {
            "titulo": "Tipos de cotización",
            "descripcion": "Clasificaciones disponibles para las cotizaciones.",
            "campos": [
                ("descripcion", "Descripción")
            ],
            "columnas": {
                "id_tipo_cotizacion": ("ID", 70),
                "descripcion": ("DESCRIPCIÓN", 420),
            },
        },
        "origen_solicitud": {
            "titulo": "Orígenes de solicitud",
            "descripcion": "Canales por los que los clientes solicitan una cotización.",
            "campos": [
                ("descripcion", "Descripción")
            ],
            "columnas": {
                "id_origen": ("ID", 70),
                "descripcion": ("DESCRIPCIÓN", 420),
            },
        },
        "moneda": {
            "titulo": "Monedas",
            "descripcion": "Monedas utilizadas para expresar los importes de las cotizaciones.",
            "campos": [
                ("nombre", "Nombre de la moneda"),
                ("simbolo", "Símbolo"),
                ("codigo_iso", "Código ISO (3 caracteres)"),
            ],
            "columnas": {
                "id_moneda": ("ID", 60),
                "nombre": ("NOMBRE", 230),
                "simbolo": ("SÍMBOLO", 110),
                "codigo_iso": ("CÓDIGO ISO", 120),
            },
        },
        "forma_pago": {
            "titulo": "Formas de pago",
            "descripcion": "Condiciones de pago y días de crédito ofrecidos.",
            "campos": [
                ("descripcion", "Descripción"),
                ("dias_credito", "Días de crédito"),
            ],
            "columnas": {
                "id_forma_pago": ("ID", 60),
                "descripcion": ("DESCRIPCIÓN", 330),
                "dias_credito": ("DÍAS DE CRÉDITO", 150),
            },
        },
        "estado_cotizacion": {
            "titulo": "Estados de cotización",
            "descripcion": "Estados que representan el avance de una cotización.",
            "campos": [
                ("descripcion", "Descripción")
            ],
            "columnas": {
                "id_estado": ("ID", 70),
                "descripcion": ("DESCRIPCIÓN", 420),
            },
        },
        "garantia": {
            "titulo": "Garantías",
            "descripcion": "Periodos de garantía disponibles para las cotizaciones.",
            "campos": [
                ("tiempo_garantia", "Tiempo de garantía"),
                ("unidad_garantia", "Unidad (días, meses, años, etc.)"),
            ],
            "columnas": {
                "id_garantia": ("ID", 60),
                "tiempo_garantia": ("TIEMPO", 140),
                "unidad_garantia": ("UNIDAD", 180),
            },
        },
    }

    def __init__(self, parent, colors, service, password):
        super().__init__(parent)

        self.colors = colors
        self.service = service
        self.password = password

        self.registros = {}
        self.variables = {}
        self.entradas = {}
        self.arboles = {}
        self.busquedas = {}
        self.contadores = {}
        self.seleccionados = {}

        self.configure(padding=(22, 18))

        self._construir_interfaz()
        self._cargar_todos()

    # =====================================================
    # INTERFAZ
    # =====================================================

    def _construir_interfaz(self):
        header = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text="Parámetros del Sistema",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text=(
                "Administra los catálogos que se utilizan al elaborar "
                "y gestionar las cotizaciones."
            ),
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        for catalogo, config in self.CONFIGURACION.items():
            tab = tk.Frame(
                self.notebook,
                bg=self.colors["background"]
            )
            self.notebook.add(
                tab,
                text=config["titulo"]
            )
            self._construir_pestana(
                tab,
                catalogo,
                config
            )

    def _construir_pestana(self, parent, catalogo, config):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        form_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        form_card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 8)
        )
        form_card.grid_columnconfigure(0, weight=1)

        tk.Label(
            form_card,
            text=config["titulo"],
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=16,
            pady=(13, 2)
        )

        tk.Label(
            form_card,
            text=config["descripcion"],
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 10)
        )

        fields_frame = tk.Frame(
            form_card,
            bg=self.colors["white"]
        )
        fields_frame.pack(
            fill="x",
            padx=16
        )

        fields_frame.grid_columnconfigure(1, weight=1)
        fields_frame.grid_columnconfigure(3, weight=1)

        self.variables[catalogo] = {}
        self.entradas[catalogo] = {}

        for index, (campo, etiqueta) in enumerate(config["campos"]):
            fila = index // 2
            grupo = index % 2
            columna = grupo * 2

            tk.Label(
                fields_frame,
                text=etiqueta,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=fila * 2,
                column=columna,
                sticky="w",
                padx=(0, 12),
                pady=(2, 4)
            )

            variable = tk.StringVar()

            entrada = ttk.Entry(
                fields_frame,
                textvariable=variable
            )
            entrada.grid(
                row=fila * 2 + 1,
                column=columna,
                sticky="ew",
                padx=(0, 18),
                pady=(0, 9)
            )

            self.variables[catalogo][campo] = variable
            self.entradas[catalogo][campo] = entrada

        buttons = tk.Frame(
            form_card,
            bg=self.colors["white"]
        )
        buttons.pack(
            fill="x",
            padx=16,
            pady=(3, 8)
        )

        ttk.Button(
            buttons,
            text="Registrar",
            style="JP.TButton",
            command=lambda c=catalogo: self._registrar(c)
        ).pack(
            side="left",
            padx=(0, 7)
        )

        ttk.Button(
            buttons,
            text="Guardar cambios",
            command=lambda c=catalogo: self._modificar(c)
        ).pack(
            side="left",
            padx=7
        )

        ttk.Button(
            buttons,
            text="Desactivar",
            command=lambda c=catalogo: self._desactivar(c)
        ).pack(
            side="left",
            padx=7
        )

        ttk.Button(
            buttons,
            text="Limpiar",
            command=lambda c=catalogo: self._limpiar(c)
        ).pack(
            side="left",
            padx=7
        )

        tk.Label(
            form_card,
            text=(
                "Los parámetros se desactivan de forma lógica. "
                "No se pueden desactivar si ya están asociados a cotizaciones."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 8),
            anchor="w",
            padx=10,
            pady=7
        ).pack(
            fill="x",
            padx=16,
            pady=(0, 13)
        )

        # ---------------------------------------------
        # TABLA
        # ---------------------------------------------

        table_card = tk.Frame(
            parent,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        table_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(2, weight=1)

        table_header = tk.Frame(
            table_card,
            bg=self.colors["white"]
        )
        table_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=(13, 8)
        )

        tk.Label(
            table_header,
            text="Registros activos",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        contador = tk.Label(
            table_header,
            text="0 registros",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        )
        contador.pack(
            side="left",
            padx=(12, 0)
        )
        self.contadores[catalogo] = contador

        ttk.Button(
            table_header,
            text="Actualizar",
            command=lambda c=catalogo: self._cargar(c)
        ).pack(side="right")

        search_frame = tk.Frame(
            table_card,
            bg=self.colors["white"]
        )
        search_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 8)
        )
        search_frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            search_frame,
            text="Buscar:",
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Segoe UI", 9)
        ).grid(
            row=0,
            column=0,
            padx=(0, 8),
            sticky="w"
        )

        search_var = tk.StringVar()
        self.busquedas[catalogo] = search_var

        search_entry = ttk.Entry(
            search_frame,
            textvariable=search_var
        )
        search_entry.grid(
            row=0,
            column=1,
            sticky="ew"
        )
        search_entry.bind(
            "<KeyRelease>",
            lambda event, c=catalogo: self._filtrar(c)
        )

        tree_frame = tk.Frame(
            table_card,
            bg=self.colors["white"]
        )
        tree_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 10)
        )

        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columnas = tuple(config["columnas"].keys())

        tree = ttk.Treeview(
            tree_frame,
            columns=columnas,
            show="headings",
            style="JP.Treeview",
            selectmode="browse"
        )

        for columna, (titulo, ancho) in config["columnas"].items():
            tree.heading(
                columna,
                text=titulo
            )

            tree.column(
                columna,
                width=ancho,
                minwidth=55,
                anchor=(
                    "w" if columna not in (
                        "id_tipo_cotizacion",
                        "id_origen",
                        "id_moneda",
                        "id_forma_pago",
                        "id_estado",
                        "id_garantia",
                        "dias_credito",
                        "tiempo_garantia"
                    ) else "center"
                ),
                stretch=True
            )

        vertical = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=tree.yview
        )

        horizontal = ttk.Scrollbar(
            tree_frame,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        tree.grid(
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

        tree.bind(
            "<<TreeviewSelect>>",
            lambda event, c=catalogo: self._seleccionar(c)
        )

        self.arboles[catalogo] = tree
        self.registros[catalogo] = []
        self.seleccionados[catalogo] = None

    # =====================================================
    # CARGA Y BÚSQUEDA
    # =====================================================

    def _cargar_todos(self):
        errores = []

        for catalogo in self.CONFIGURACION:
            try:
                self._cargar(
                    catalogo,
                    mostrar_error=False
                )

            except Exception as error:
                errores.append(
                    f"{self.CONFIGURACION[catalogo]['titulo']}: {error}"
                )

        if errores:
            messagebox.showerror(
                "Error al cargar parámetros",
                "No se pudieron cargar algunos catálogos:\n\n"
                + "\n".join(errores),
                parent=self.winfo_toplevel()
            )

    def _cargar(self, catalogo, mostrar_error=True):
        try:
            registros = self.service.listar(
                self.password,
                catalogo
            )

            self.registros[catalogo] = registros
            self._actualizar_tabla(catalogo)
            self._limpiar(
                catalogo,
                enfocar=False
            )

        except Exception as error:
            if mostrar_error:
                messagebox.showerror(
                    "Error de consulta",
                    f"No se pudieron cargar los registros.\n\n{error}",
                    parent=self.winfo_toplevel()
                )
            else:
                raise

    def _actualizar_tabla(self, catalogo):
        tree = self.arboles[catalogo]

        for item in tree.get_children():
            tree.delete(item)

        config = self.CONFIGURACION[catalogo]
        columnas = tuple(config["columnas"].keys())

        termino = self.busquedas[catalogo].get().strip().casefold()
        visibles = 0

        for registro in self.registros[catalogo]:
            texto = " ".join(
                str(registro.get(campo, ""))
                for campo in columnas
            ).casefold()

            if termino and termino not in texto:
                continue

            tree.insert(
                "",
                "end",
                values=tuple(
                    registro.get(campo, "")
                    for campo in columnas
                )
            )

            visibles += 1

        self.contadores[catalogo].configure(
            text=f"{visibles} registro(s)"
        )

    def _filtrar(self, catalogo):
        self._actualizar_tabla(catalogo)

    # =====================================================
    # SELECCIÓN Y FORMULARIO
    # =====================================================

    def _seleccionar(self, catalogo):
        tree = self.arboles[catalogo]
        seleccion = tree.selection()

        if not seleccion:
            return

        valores = tree.item(
            seleccion[0],
            "values"
        )

        config = self.CONFIGURACION[catalogo]
        columnas = tuple(config["columnas"].keys())

        registro = dict(
            zip(columnas, valores)
        )

        claves = {
            "tipo_cotizacion": "id_tipo_cotizacion",
            "origen_solicitud": "id_origen",
            "moneda": "id_moneda",
            "forma_pago": "id_forma_pago",
            "estado_cotizacion": "id_estado",
            "garantia": "id_garantia",
        }

        self.seleccionados[catalogo] = int(
            registro[claves[catalogo]]
        )

        for campo, _ in config["campos"]:
            self.variables[catalogo][campo].set(
                str(registro.get(campo, ""))
            )

    def _obtener_datos(self, catalogo):
        return {
            campo: variable.get()
            for campo, variable in self.variables[catalogo].items()
        }

    def _limpiar(self, catalogo, enfocar=True):
        for variable in self.variables[catalogo].values():
            variable.set("")

        self.seleccionados[catalogo] = None

        tree = self.arboles.get(catalogo)

        if tree is not None:
            seleccion = tree.selection()

            if seleccion:
                tree.selection_remove(seleccion)

        entradas = self.entradas.get(catalogo, {})

        if entradas and enfocar:
            siguiente = next(iter(entradas.values()))
            siguiente.focus_set()

    # =====================================================
    # REGISTRAR
    # =====================================================

    def _registrar(self, catalogo):
        try:
            nuevo_id = self.service.registrar(
                self.password,
                catalogo,
                self._obtener_datos(catalogo)
            )

            messagebox.showinfo(
                "Registro exitoso",
                f"El parámetro se registró correctamente. ID: {nuevo_id}",
                parent=self.winfo_toplevel()
            )

            self._cargar(catalogo)

        except Exception as error:
            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # MODIFICAR
    # =====================================================

    def _modificar(self, catalogo):
        identificador = self.seleccionados.get(catalogo)

        if identificador is None:
            messagebox.showwarning(
                "Selecciona un registro",
                "Selecciona un parámetro de la tabla antes de modificarlo.",
                parent=self.winfo_toplevel()
            )
            return

        try:
            self.service.modificar(
                self.password,
                catalogo,
                identificador,
                self._obtener_datos(catalogo)
            )

            messagebox.showinfo(
                "Actualización exitosa",
                "El parámetro se actualizó correctamente.",
                parent=self.winfo_toplevel()
            )

            self._cargar(catalogo)

        except Exception as error:
            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self.winfo_toplevel()
            )

    # =====================================================
    # DESACTIVAR
    # =====================================================

    def _desactivar(self, catalogo):
        identificador = self.seleccionados.get(catalogo)

        if identificador is None:
            messagebox.showwarning(
                "Selecciona un registro",
                "Selecciona un parámetro de la tabla antes de desactivarlo.",
                parent=self.winfo_toplevel()
            )
            return

        titulo = self.CONFIGURACION[catalogo]["titulo"]

        confirmar = messagebox.askyesno(
            "Confirmar desactivación",
            (
                f"¿Deseas desactivar este registro de {titulo}?\n\n"
                "El registro no se eliminará físicamente."
            ),
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        try:
            self.service.desactivar(
                self.password,
                catalogo,
                identificador
            )

            messagebox.showinfo(
                "Desactivación exitosa",
                "El parámetro se desactivó correctamente.",
                parent=self.winfo_toplevel()
            )

            self._cargar(catalogo)

        except Exception as error:
            messagebox.showerror(
                "No se pudo desactivar",
                str(error),
                parent=self.winfo_toplevel()
            )
