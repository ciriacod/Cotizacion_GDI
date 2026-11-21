
import tkinter as tk
from tkinter import ttk, messagebox


class ContactosView(tk.Toplevel):

    def __init__(
        self,
        parent,
        colors,
        service,
        password,
        cod_interno,
        razon_social
    ):
        super().__init__(parent)

        self.colors = colors
        self.service = service
        self.password = password
        self.cod_interno = cod_interno
        self.razon_social = razon_social

        self.contactos = []
        self.contacto_seleccionado = None

        self.title("Gestión de contactos")
        self.geometry("950x570")
        self.minsize(800, 480)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.configure(bg=self.colors["background"])

        self.construir_interfaz()
        self.cargar_contactos()

    # -------------------------------------------------
    # INTERFAZ PRINCIPAL
    # -------------------------------------------------

    def construir_interfaz(self):

        encabezado = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        encabezado.pack(
            fill="x",
            padx=22,
            pady=(20, 15)
        )

        tk.Label(
            encabezado,
            text="Gestión de Contactos",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            encabezado,
            text=(
                f"Cliente: {self.cod_interno} - "
                f"{self.razon_social}"
            ),
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(5, 0))

        contenido = tk.Frame(
            self,
            bg=self.colors["background"]
        )
        contenido.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(0, 20)
        )

        panel_formulario = tk.Frame(
            contenido,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            width=285
        )
        panel_formulario.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )
        panel_formulario.pack_propagate(False)

        self.construir_formulario(panel_formulario)

        panel_tabla = tk.Frame(
            contenido,
            bg=self.colors["white"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        panel_tabla.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.construir_tabla(panel_tabla)

    # -------------------------------------------------
    # FORMULARIO
    # -------------------------------------------------

    def construir_formulario(self, parent):

        tk.Label(
            parent,
            text="Datos del contacto",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(20, 18)
        )

        self.entries = {}

        campos = [
            ("nombre_contacto", "Nombre del contacto"),
            ("telefono_contacto", "Teléfono"),
            ("email_contacto", "Correo electrónico")
        ]

        for clave, etiqueta in campos:

            tk.Label(
                parent,
                text=etiqueta,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Segoe UI", 9, "bold")
            ).pack(
                anchor="w",
                padx=18,
                pady=(7, 5)
            )

            entrada = ttk.Entry(
                parent,
                font=("Segoe UI", 10)
            )
            entrada.pack(
                fill="x",
                padx=18,
                ipady=5
            )

            self.entries[clave] = entrada

        botones = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        botones.pack(
            fill="x",
            padx=18,
            pady=(22, 5)
        )

        ttk.Button(
            botones,
            text="Registrar contacto",
            style="JP.TButton",
            command=self.registrar_contacto
        ).pack(fill="x", pady=4)

        ttk.Button(
            botones,
            text="Guardar cambios",
            command=self.modificar_contacto
        ).pack(fill="x", pady=4)

        ttk.Button(
            botones,
            text="Desactivar contacto",
            command=self.eliminar_contacto
        ).pack(fill="x", pady=4)

        ttk.Button(
            botones,
            text="Limpiar formulario",
            command=self.limpiar_formulario
        ).pack(fill="x", pady=4)

        tk.Label(
            parent,
            text=(
                "Selecciona un contacto de la tabla "
                "para modificar sus datos."
            ),
            bg=self.colors["blue_light"],
            fg=self.colors["navy"],
            font=("Segoe UI", 8),
            wraplength=235,
            justify="left",
            padx=12,
            pady=10
        ).pack(
            fill="x",
            padx=18,
            pady=(18, 15)
        )

    # -------------------------------------------------
    # TABLA
    # -------------------------------------------------

    def construir_tabla(self, parent):

        encabezado = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        encabezado.pack(
            fill="x",
            padx=18,
            pady=(18, 12)
        )

        tk.Label(
            encabezado,
            text="Contactos registrados",
            bg=self.colors["white"],
            fg=self.colors["navy"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            encabezado,
            text="Actualizar",
            command=self.cargar_contactos
        ).pack(side="right")

        self.total_label = tk.Label(
            parent,
            text="Total de contactos: 0",
            bg=self.colors["white"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        )
        self.total_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 10)
        )

        tabla_frame = tk.Frame(
            parent,
            bg=self.colors["white"]
        )
        tabla_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        columnas = (
            "id_contacto",
            "nombre",
            "telefono",
            "email"
        )

        self.tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            style="JP.Treeview"
        )

        encabezados = {
            "id_contacto": "ID",
            "nombre": "NOMBRE",
            "telefono": "TELÉFONO",
            "email": "CORREO ELECTRÓNICO"
        }

        anchos = {
            "id_contacto": 55,
            "nombre": 190,
            "telefono": 110,
            "email": 210
        }

        for columna in columnas:

            self.tree.heading(
                columna,
                text=encabezados[columna]
            )

            self.tree.column(
                columna,
                width=anchos[columna],
                minwidth=55,
                anchor="w"
            )

        scrollbar_vertical = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar_horizontal = ttk.Scrollbar(
            tabla_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=scrollbar_vertical.set,
            xscrollcommand=scrollbar_horizontal.set
        )

        self.tree.pack(
            side="top",
            fill="both",
            expand=True
        )

        scrollbar_vertical.pack(
            side="right",
            fill="y"
        )

        scrollbar_horizontal.pack(
            side="bottom",
            fill="x"
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.seleccionar_contacto
        )

    # -------------------------------------------------
    # CARGAR CONTACTOS
    # -------------------------------------------------

    def cargar_contactos(self):

        try:
            self.contactos = self.service.listar_contactos(
                self.password,
                self.cod_interno
            )

            self.filtrar_contactos()

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los contactos.\n\n{error}",
                parent=self
            )

    # -------------------------------------------------
    # MOSTRAR CONTACTOS
    # -------------------------------------------------

    def filtrar_contactos(self):

        for elemento in self.tree.get_children():
            self.tree.delete(elemento)

        for contacto in self.contactos:

            id_contacto = str(
                contacto.get("id_contacto", "")
            )

            self.tree.insert(
                "",
                "end",
                iid=id_contacto,
                values=(
                    id_contacto,
                    contacto.get("nombre_contacto", ""),
                    contacto.get("telefono_contacto") or "",
                    contacto.get("email_contacto") or ""
                )
            )

        self.total_label.config(
            text=f"Total de contactos: {len(self.contactos)}"
        )

    # -------------------------------------------------
    # SELECCIONAR CONTACTO
    # -------------------------------------------------

    def seleccionar_contacto(self, event=None):

        seleccion = self.tree.selection()

        if not seleccion:
            return

        id_contacto = seleccion[0]

        contacto = next(
            (
                item
                for item in self.contactos
                if str(item.get("id_contacto")) == id_contacto
            ),
            None
        )

        if not contacto:
            return

        self.contacto_seleccionado = id_contacto

        self.entries["nombre_contacto"].delete(0, tk.END)
        self.entries["nombre_contacto"].insert(
            0,
            contacto.get("nombre_contacto", "")
        )

        self.entries["telefono_contacto"].delete(0, tk.END)
        self.entries["telefono_contacto"].insert(
            0,
            contacto.get("telefono_contacto") or ""
        )

        self.entries["email_contacto"].delete(0, tk.END)
        self.entries["email_contacto"].insert(
            0,
            contacto.get("email_contacto") or ""
        )

    # -------------------------------------------------
    # OBTENER DATOS
    # -------------------------------------------------

    def obtener_datos_formulario(self):

        return {
            "nombre_contacto": self.entries[
                "nombre_contacto"
            ].get().strip(),

            "telefono_contacto": self.entries[
                "telefono_contacto"
            ].get().strip(),

            "email_contacto": self.entries[
                "email_contacto"
            ].get().strip()
        }

    # -------------------------------------------------
    # REGISTRAR CONTACTO
    # -------------------------------------------------

    def registrar_contacto(self):

        datos = self.obtener_datos_formulario()

        try:
            id_contacto = self.service.registrar_contacto(
                self.password,
                self.cod_interno,
                datos["nombre_contacto"],
                datos["telefono_contacto"],
                datos["email_contacto"]
            )

            messagebox.showinfo(
                "Contacto registrado",
                (
                    "El contacto se registró correctamente.\n"
                    f"Identificador: {id_contacto}"
                ),
                parent=self
            )

            self.limpiar_formulario()
            self.cargar_contactos()

        except Exception as error:

            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=self
            )

    # -------------------------------------------------
    # MODIFICAR CONTACTO
    # -------------------------------------------------

    def modificar_contacto(self):

        if not self.contacto_seleccionado:

            messagebox.showwarning(
                "Selecciona un contacto",
                "Selecciona un contacto de la tabla.",
                parent=self
            )
            return

        datos = self.obtener_datos_formulario()

        confirmar = messagebox.askyesno(
            "Confirmar modificación",
            "¿Deseas guardar los cambios de este contacto?",
            parent=self
        )

        if not confirmar:
            return

        try:
            self.service.modificar_contacto(
                self.password,
                self.cod_interno,
                self.contacto_seleccionado,
                datos["nombre_contacto"],
                datos["telefono_contacto"],
                datos["email_contacto"]
            )

            messagebox.showinfo(
                "Actualización correcta",
                "Los datos del contacto fueron actualizados.",
                parent=self
            )

            self.limpiar_formulario()
            self.cargar_contactos()

        except Exception as error:

            messagebox.showerror(
                "No se pudo modificar",
                str(error),
                parent=self
            )

    # -------------------------------------------------
    # DESACTIVAR CONTACTO
    # -------------------------------------------------

    def eliminar_contacto(self):

        if not self.contacto_seleccionado:

            messagebox.showwarning(
                "Selecciona un contacto",
                "Selecciona un contacto de la tabla.",
                parent=self
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar desactivación",
            (
                "¿Deseas desactivar este contacto?\n\n"
                "El registro se conservará en la base de datos."
            ),
            parent=self
        )

        if not confirmar:
            return

        try:
            self.service.eliminar_contacto(
                self.password,
                self.cod_interno,
                self.contacto_seleccionado
            )

            messagebox.showinfo(
                "Contacto desactivado",
                "El contacto fue desactivado correctamente.",
                parent=self
            )

            self.limpiar_formulario()
            self.cargar_contactos()

        except Exception as error:

            messagebox.showerror(
                "No se pudo desactivar",
                str(error),
                parent=self
            )

    # -------------------------------------------------
    # LIMPIAR FORMULARIO
    # -------------------------------------------------

    def limpiar_formulario(self):

        for entrada in self.entries.values():
            entrada.delete(0, tk.END)

        self.contacto_seleccionado = None

        seleccion = self.tree.selection()

        if seleccion:
            self.tree.selection_remove(seleccion)
