"""Interfaz de registro, edicion, consulta y emision de cotizaciones."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from tkinter import ttk, messagebox, filedialog

from utils.pdf_generator import generar_cotizacion_pdf


class CotizacionesView(ttk.Frame):
    def __init__(self, parent, colors, service, password, on_saved=None):
        super().__init__(parent)
        self.colors = colors
        self.service = service
        self.password = password
        self.on_saved = on_saved
        self.opciones = {}
        self.maps = {}
        self.detalles = []
        self.numero_edicion = None
        self._construir()
        self._cargar_opciones()
        self._nuevo()
        self._cargar_lista()

    def _label(self, parent, text, row, col, colspan=1):
        ttk.Label(parent, text=text).grid(row=row, column=col, columnspan=colspan, sticky="w", padx=6, pady=(5, 1))

    def _entry(self, parent, key, text, row, col, width=22):
        self._label(parent, text, row, col)
        widget = ttk.Entry(parent, width=width)
        widget.grid(row=row + 1, column=col, sticky="ew", padx=6, pady=(0, 5))
        self.vars[key] = widget
        return widget

    def _combo(self, parent, key, text, row, col, width=25, callback=None):
        self._label(parent, text, row, col)
        widget = ttk.Combobox(parent, width=width, state="readonly")
        widget.grid(row=row + 1, column=col, sticky="ew", padx=6, pady=(0, 5))
        self.vars[key] = widget
        if callback:
            widget.bind("<<ComboboxSelected>>", callback)
        return widget

    def _construir(self):
        self.configure(padding=16)
        heading = ttk.Frame(self)
        heading.pack(fill="x", pady=(0, 10))
        ttk.Label(heading, text="Gestión de cotizaciones", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Label(heading, text="Registro comercial, partidas, estados y emisión PDF", foreground="#64748B").pack(side="right")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        self.tab_editor = ttk.Frame(self.tabs, padding=8)
        self.tab_listado = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(self.tab_editor, text="Nueva / editar cotización")
        self.tabs.add(self.tab_listado, text="Consultar cotizaciones")

        self.vars = {}
        form = ttk.LabelFrame(self.tab_editor, text="Datos generales y condiciones", padding=8)
        form.pack(fill="x", pady=(0, 8))
        for i in range(4):
            form.columnconfigure(i, weight=1)
        self._entry(form, "fecha_emision", "Fecha emisión (AAAA-MM-DD)", 0, 0, 18)
        self._combo(form, "cliente", "Cliente", 0, 1, 32, self._cliente_cambiado)
        self._combo(form, "contacto", "Contacto", 0, 2, 25)
        self._combo(form, "empleado", "Responsable", 0, 3, 25)
        self._combo(form, "tipo", "Tipo de cotización", 2, 0, 24)
        self._combo(form, "origen", "Origen de solicitud", 2, 1, 24)
        self._combo(form, "moneda", "Moneda", 2, 2, 20)
        self._combo(form, "forma_pago", "Forma de pago", 2, 3, 20)
        self._combo(form, "garantia", "Garantía", 4, 0, 20)
        self._combo(form, "impuesto", "Impuesto", 4, 1, 16)
        self.vars["impuesto"].configure(values=["SIN IGV", "CON IGV"])
        self.vars["impuesto"].bind("<<ComboboxSelected>>", lambda _e: self._actualizar_totales())
        self._entry(form, "porcentaje_igv", "Porcentaje IGV", 4, 2, 12)
        self._entry(form, "vigencia_dias", "Vigencia (días)", 4, 3, 12)
        self._entry(form, "tiempo_ejecucion", "Tiempo de ejecución", 6, 0)
        self._entry(form, "tiempo_entrega", "Tiempo de entrega", 6, 1)
        self._entry(form, "exclusiones", "Exclusiones", 6, 2)
        self._entry(form, "observaciones", "Observaciones", 6, 3)

        detail = ttk.LabelFrame(self.tab_editor, text="Partidas de la cotización", padding=8)
        detail.pack(fill="both", expand=True, pady=(0, 8))
        for i in range(5):
            detail.columnconfigure(i, weight=1 if i in (0, 4) else 0)
        self._combo(detail, "producto", "Producto / servicio", 0, 0, 38, self._producto_cambiado)
        self._entry(detail, "cantidad", "Cantidad entera", 0, 1, 10)
        self._entry(detail, "precio", "Precio unitario", 0, 2, 14)
        self._entry(detail, "alcance", "Alcance técnico (opcional)", 0, 3, 30)
        ttk.Button(detail, text="Agregar partida", command=self._agregar_detalle).grid(row=1, column=4, padx=6, pady=5, sticky="ew")
        cols = ("item", "codigo", "descripcion", "unidad", "cantidad", "precio", "subtotal", "alcance")
        self.tree_detalles = ttk.Treeview(detail, columns=cols, show="headings", height=5)
        names = {"item":"Ítem", "codigo":"Código", "descripcion":"Descripción", "unidad":"Unidad", "cantidad":"Cant.", "precio":"P. unitario", "subtotal":"Subtotal", "alcance":"Alcance técnico"}
        widths = {"item":45, "codigo":90, "descripcion":220, "unidad":60, "cantidad":65, "precio":95, "subtotal":95, "alcance":180}
        for c in cols:
            self.tree_detalles.heading(c, text=names[c])
            self.tree_detalles.column(c, width=widths[c], anchor="w" if c in ("descripcion", "alcance") else "center")
        self.tree_detalles.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=6, pady=(5, 3))
        ttk.Button(detail, text="Retirar partida seleccionada", command=self._quitar_detalle).grid(row=3, column=0, sticky="w", padx=6, pady=(2, 5))
        self.total_label = ttk.Label(detail, text="Subtotal: 0.00 | IGV: 0.00 | Total: 0.00", font=("Segoe UI", 10, "bold"))
        self.total_label.grid(row=3, column=1, columnspan=4, sticky="e", padx=6, pady=(2, 5))
        detail.rowconfigure(2, weight=1)

        actions = ttk.Frame(self.tab_editor)
        actions.pack(fill="x")
        ttk.Button(actions, text="Nueva cotización", command=self._nuevo).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Guardar cotización", command=self._guardar).pack(side="left", padx=5)
        ttk.Button(actions, text="Actualizar listado", command=self._cargar_lista).pack(side="left", padx=5)
        ttk.Label(actions, text="Los borradores requieren al menos una partida para guardarse.", foreground="#64748B").pack(side="right")

        search = ttk.Frame(self.tab_listado)
        search.pack(fill="x", pady=(0, 8))
        ttk.Label(search, text="Buscar por número, cliente o estado:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(search, textvariable=self.search_var, width=32).pack(side="left", padx=8)
        ttk.Button(search, text="Buscar", command=self._cargar_lista).pack(side="left")
        ttk.Button(search, text="Mostrar todos", command=lambda: (self.search_var.set(""), self._cargar_lista())).pack(side="left", padx=5)
        cols = ("numero", "fecha", "cliente", "estado", "moneda", "subtotal", "vencimiento")
        self.tree_quotes = ttk.Treeview(self.tab_listado, columns=cols, show="headings", height=16)
        labels = {"numero":"N° cotización", "fecha":"Fecha", "cliente":"Cliente", "estado":"Estado", "moneda":"Moneda", "subtotal":"Subtotal", "vencimiento":"Vencimiento"}
        widths = {"numero":130, "fecha":95, "cliente":270, "estado":120, "moneda":75, "subtotal":100, "vencimiento":105}
        for c in cols:
            self.tree_quotes.heading(c, text=labels[c])
            self.tree_quotes.column(c, width=widths[c], anchor="w" if c == "cliente" else "center")
        self.tree_quotes.pack(fill="both", expand=True)
        controls = ttk.Frame(self.tab_listado)
        controls.pack(fill="x", pady=(8, 0))
        ttk.Button(controls, text="Abrir para editar", command=self._cargar_seleccion).pack(side="left")
        ttk.Label(controls, text="Cambiar estado:").pack(side="left", padx=(18, 5))
        self.estado_var = tk.StringVar()
        self.estado_combo = ttk.Combobox(controls, textvariable=self.estado_var, state="readonly", width=22)
        self.estado_combo.pack(side="left")
        ttk.Button(controls, text="Aplicar estado", command=self._cambiar_estado).pack(side="left", padx=5)
        ttk.Button(controls, text="Generar PDF", command=self._generar_pdf).pack(side="right")

    def _cargar_opciones(self):
        try:
            self.opciones = self.service.obtener_opciones(self.password)
            definiciones = {
                "cliente": ("clientes", lambda x: f"{x['razon_social']} | {x['ruc']}", "cod_interno"),
                "empleado": ("empleados", lambda x: f"{x['nombre_completo']} | DNI {x['DNI']}", "id_empleado"),
                "tipo": ("tipos", lambda x: x["descripcion"], "id_tipo_cotizacion"),
                "origen": ("origenes", lambda x: x["descripcion"], "id_origen"),
                "moneda": ("monedas", lambda x: f"{x['codigo_iso']} - {x['nombre']}", "id_moneda"),
                "forma_pago": ("formas_pago", lambda x: x["descripcion"], "id_forma_pago"),
                "garantia": ("garantias", lambda x: f"{x['tiempo_garantia']} {x['unidad_garantia']}", "id_garantia"),
                "producto": ("productos", lambda x: f"{x['cod_pro_ser']} | {x['Descripcion']}", "cod_pro_ser"),
            }
            for key, (source, label_fn, id_key) in definiciones.items():
                items = self.opciones.get(source, [])
                labels = [label_fn(item) for item in items]
                self.vars[key]["values"] = labels
                self.maps[key] = {label_fn(item): item[id_key] for item in items}
                self.maps.setdefault(f"{key}_items", {label_fn(item): item for item in items})
            estados = self.opciones.get("estados", [])
            self.estado_items = {x["descripcion"]: x["id_estado"] for x in estados}
            self.estado_combo["values"] = list(self.estado_items)
            self.vars["contacto"]["values"] = ["Sin contacto"]
            self.maps["contacto"] = {"Sin contacto": None}
        except Exception as error:
            messagebox.showerror("No se pudieron cargar las opciones", str(error), parent=self)

    def _cliente_cambiado(self, _event=None):
        label = self.vars["cliente"].get()
        cod = self.maps.get("cliente", {}).get(label)
        self.maps["contacto_items"] = {"Sin contacto": None}
        self.maps["contacto"] = {"Sin contacto": None}
        values = ["Sin contacto"]
        if cod:
            try:
                contacts = self.service.obtener_contactos(self.password, cod)
                for c in contacts:
                    name = f"{c['nombre_contacto']} | {c.get('telefono_contacto') or '-'}"
                    values.append(name)
                    self.maps["contacto"][name] = c["id_contacto"]
                    self.maps["contacto_items"][name] = c
            except Exception as error:
                messagebox.showerror("Contactos", str(error), parent=self)
        self.vars["contacto"]["values"] = values
        self.vars["contacto"].set("Sin contacto")

    def _producto_cambiado(self, _event=None):
        item = self.maps.get("producto_items", {}).get(self.vars["producto"].get())
        if item:
            self.vars["precio"].delete(0, "end")
            self.vars["precio"].insert(0, str(item["Precio_referencial"]))

    def _nuevo(self):
        self.numero_edicion = None
        for key, widget in self.vars.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, "end")
            else:
                widget.set("")
        self.vars["fecha_emision"].insert(0, date.today().isoformat())
        self.vars["vigencia_dias"].insert(0, "15")
        self.vars["porcentaje_igv"].insert(0, "18")
        self.vars["tiempo_ejecucion"].insert(0, "Por definir")
        self.vars["exclusiones"].insert(0, "No aplica")
        self.vars["observaciones"].insert(0, "Sin observaciones")
        self.vars["impuesto"].set("SIN IGV")
        self.vars["contacto"]["values"] = ["Sin contacto"]
        self.vars["contacto"].set("Sin contacto")
        self.detalles.clear()
        self._refrescar_detalles()

    def _agregar_detalle(self):
        label = self.vars["producto"].get()
        item = self.maps.get("producto_items", {}).get(label)
        if not item:
            messagebox.showwarning("Partida", "Selecciona un producto o servicio.", parent=self)
            return
        try:
            cantidad = int(self.vars["cantidad"].get().strip())
            precio = Decimal(self.vars["precio"].get().strip().replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if cantidad <= 0 or precio < 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Partida", "La cantidad debe ser entera positiva y el precio no puede ser negativo.", parent=self)
            return
        self.detalles.append({
            "cod_pro_ser": item["cod_pro_ser"],
            "descripcion": item["Descripcion"],
            "unidad": item["abreviatura"],
            "cantidad": cantidad,
            "precio_unitario": precio,
            "alcance_tecnico": self.vars["alcance"].get().strip() or None,
        })
        for key in ("cantidad", "alcance"):
            self.vars[key].delete(0, "end")
        self._refrescar_detalles()
        self._actualizar_totales()

    def _quitar_detalle(self):
        selected = self.tree_detalles.selection()
        if not selected:
            return
        index = int(selected[0])
        if 0 <= index < len(self.detalles):
            self.detalles.pop(index)
        self._refrescar_detalles()
        self._actualizar_totales()

    def _refrescar_detalles(self):
        for row in self.tree_detalles.get_children():
            self.tree_detalles.delete(row)
        for i, line in enumerate(self.detalles, start=1):
            subtotal = Decimal(line["cantidad"]) * Decimal(str(line["precio_unitario"]))
            self.tree_detalles.insert("", "end", iid=str(i - 1), values=(i, line["cod_pro_ser"], line.get("descripcion", ""), line.get("unidad", ""), line["cantidad"], f"{Decimal(str(line['precio_unitario'])):.2f}", f"{subtotal:.2f}", line.get("alcance_tecnico") or ""))

    def _actualizar_totales(self):
        try:
            impuesto = self.vars["impuesto"].get() or "SIN IGV"
            tasa = self.vars["porcentaje_igv"].get() or "18"
            total = self.service.calcular(self.detalles, impuesto, tasa)
            self.total_label.configure(text=f"Subtotal: {total['subtotal']:.2f} | IGV: {total['igv']:.2f} | Total: {total['total']:.2f}")
        except Exception:
            self.total_label.configure(text="Subtotal: 0.00 | IGV: 0.00 | Total: 0.00")

    def _encabezado_form(self):
        def selected_id(key):
            return self.maps.get(key, {}).get(self.vars[key].get())
        return {
            "fecha_emision": self.vars["fecha_emision"].get(),
            "id_tipo_cotizacion": selected_id("tipo"),
            "id_origen": selected_id("origen"),
            "id_moneda": selected_id("moneda"),
            "impuesto": self.vars["impuesto"].get(),
            "porcentaje_igv": self.vars["porcentaje_igv"].get(),
            "id_forma_pago": selected_id("forma_pago"),
            "id_garantia": selected_id("garantia"),
            "tiempo_ejecucion": self.vars["tiempo_ejecucion"].get(),
            "tiempo_entrega": self.vars["tiempo_entrega"].get(),
            "vigencia_dias": self.vars["vigencia_dias"].get(),
            "exclusiones": self.vars["exclusiones"].get(),
            "observaciones": self.vars["observaciones"].get(),
            "cod_interno_cliente": selected_id("cliente"),
            "id_contacto": self.maps.get("contacto", {}).get(self.vars["contacto"].get()),
            "id_empleado": selected_id("empleado"),
        }

    def _guardar(self):
        try:
            header = self._encabezado_form()
            if self.numero_edicion:
                self.service.actualizar(self.password, self.numero_edicion, header, self.detalles)
                messagebox.showinfo("Cotización", f"La cotización {self.numero_edicion} se actualizó correctamente.", parent=self)
            else:
                numero = self.service.crear(self.password, header, self.detalles)
                self.numero_edicion = numero
                messagebox.showinfo("Cotización", f"La cotización {numero} se registró correctamente.", parent=self)
            self._cargar_lista()
            if self.on_saved:
                self.on_saved()
            self.tabs.select(self.tab_listado)
        except Exception as error:
            messagebox.showerror("No se pudo guardar la cotización", str(error), parent=self)

    def _cargar_lista(self):
        for row in self.tree_quotes.get_children():
            self.tree_quotes.delete(row)
        try:
            rows = self.service.listar(self.password, self.search_var.get() if hasattr(self, "search_var") else "")
            for i, row in enumerate(rows):
                fecha = row.get("fecha_emision")
                vence = row.get("fecha_vencimiento")
                self.tree_quotes.insert("", "end", iid=str(i), values=(row["nmr_cotizacion"], fecha, row["razon_social"], row["estado"], row["moneda"], f"{Decimal(str(row['subtotal'])):.2f}", vence or "-"))
            self._rows_quotes = rows
        except Exception as error:
            messagebox.showerror("Listado de cotizaciones", str(error), parent=self)

    def _cargar_seleccion(self):
        selected = self.tree_quotes.selection()
        if not selected:
            messagebox.showwarning("Cotización", "Selecciona una cotización del listado.", parent=self)
            return
        numero = self.tree_quotes.item(selected[0], "values")[0]
        try:
            data = self.service.obtener(self.password, numero)
            if not data:
                raise ValueError("La cotización ya no existe.")
            h = data["encabezado"]
            self._nuevo()
            self.numero_edicion = numero
            value_by_id = {
                "tipo": ("id_tipo_cotizacion", "tipo"),
                "origen": ("id_origen", "origen"),
                "moneda": ("id_moneda", "moneda"),
                "forma_pago": ("id_forma_pago", "forma_pago"),
                "garantia": ("id_garantia", "garantia"),
                "empleado": ("id_empleado", "empleado"),
            }
            for key, (field, map_key) in value_by_id.items():
                target = next((label for label, ident in self.maps.get(map_key, {}).items() if ident == h[field]), "")
                self.vars[key].set(target)
            target = next((label for label, ident in self.maps.get("cliente", {}).items() if ident == h["cod_interno_cliente"]), "")
            self.vars["cliente"].set(target)
            self._cliente_cambiado()
            contact_id = h.get("id_contacto")
            contact_label = next((label for label, ident in self.maps.get("contacto", {}).items() if ident == contact_id), "Sin contacto")
            self.vars["contacto"].set(contact_label)
            fields = {"fecha_emision":"fecha_emision", "impuesto":"impuesto", "porcentaje_igv":"porcentaje_igv", "vigencia_dias":"vigencia_dias", "tiempo_ejecucion":"tiempo_ejecucion", "tiempo_entrega":"tiempo_entrega", "exclusiones":"exclusiones", "observaciones":"observaciones"}
            for key, field in fields.items():
                self.vars[key].delete(0, "end")
                self.vars[key].insert(0, str(h.get(field) or ""))
            self.detalles = [{
                "cod_pro_ser": x["cod_pro_ser"], "descripcion": x["descripcion"], "unidad": x["unidad"],
                "cantidad": x["cantidad"], "precio_unitario": x["precio_unitario"], "alcance_tecnico": x.get("alcance_tecnico")
            } for x in data["detalles"]]
            self._refrescar_detalles()
            self._actualizar_totales()
            self.tabs.select(self.tab_editor)
        except Exception as error:
            messagebox.showerror("Abrir cotización", str(error), parent=self)

    def _cambiar_estado(self):
        selected = self.tree_quotes.selection()
        status = self.estado_var.get()
        if not selected or not status:
            messagebox.showwarning("Estado", "Selecciona la cotización y el nuevo estado.", parent=self)
            return
        numero = self.tree_quotes.item(selected[0], "values")[0]
        if not messagebox.askyesno("Confirmar cambio", f"¿Cambiar el estado de {numero} a '{status}'?", parent=self):
            return
        try:
            self.service.actualizar_estado(self.password, numero, self.estado_items[status])
            self._cargar_lista()
            if self.on_saved:
                self.on_saved()
            messagebox.showinfo("Estado", "El estado se actualizó correctamente.", parent=self)
        except Exception as error:
            messagebox.showerror("Estado", str(error), parent=self)

    def _generar_pdf(self):
        selected = self.tree_quotes.selection()
        if not selected:
            messagebox.showwarning("PDF", "Selecciona una cotización del listado.", parent=self)
            return
        numero = self.tree_quotes.item(selected[0], "values")[0]
        try:
            data = self.service.obtener(self.password, numero)
            if not data:
                raise ValueError("La cotización ya no existe.")
            suggested = f"Cotizacion_{numero.replace('.', '_')}.pdf"
            path = filedialog.asksaveasfilename(parent=self, title="Guardar cotización PDF", defaultextension=".pdf", initialfile=suggested, filetypes=[("Documento PDF", "*.pdf")])
            if not path:
                return
            output = generar_cotizacion_pdf(data, path)
            messagebox.showinfo("PDF generado", f"Documento guardado en:\n{output}", parent=self)
        except Exception as error:
            messagebox.showerror("Generación PDF", str(error), parent=self)
