"""Persistencia SQL del modulo de cotizaciones mediante Procedimientos Almacenados."""

from __future__ import annotations


class CotizacionRepository:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def _call_all(cursor, nombre: str, parametros=()):
        marcadores = ", ".join(["%s"] * len(parametros))
        cursor.execute(f"CALL {nombre}({marcadores})", parametros)
        filas = cursor.fetchall() if cursor.with_rows else []
        while cursor.nextset():
            if cursor.with_rows:
                cursor.fetchall()
        return filas

    @classmethod
    def _call(cls, cursor, nombre: str, parametros=()):
        filas = cls._call_all(cursor, nombre, parametros)
        return filas[0] if filas else None

    @staticmethod
    def _close(cursor, connection):
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    def obtener_opciones(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return {
                "clientes": self._call_all(cursor, "sp_listar_clientes_activos"),
                "empleados": self._call_all(cursor, "sp_listar_empleados_activos"),
                "tipos": self._call_all(cursor, "sp_listar_parametros", ("tipo_cotizacion",)),
                "origenes": self._call_all(cursor, "sp_listar_parametros", ("origen_solicitud",)),
                "monedas": self._call_all(cursor, "sp_listar_parametros", ("moneda",)),
                "formas_pago": self._call_all(cursor, "sp_listar_parametros", ("forma_pago",)),
                "garantias": self._call_all(cursor, "sp_listar_parametros", ("garantia",)),
                "estados": self._call_all(cursor, "sp_listar_parametros", ("estado_cotizacion",)),
                "productos": [
                    {
                        "cod_pro_ser": p["cod_pro_ser"],
                        "Descripcion": p["descripcion"],
                        "Precio_referencial": p["precio_referencial"],
                        "nombre_tipo": p["nombre_tipo"],
                        "abreviatura": p["abreviatura"],
                    }
                    for p in self._call_all(cursor, "sp_listar_catalogo_activo")
                ],
            }
        finally:
            self._close(cursor, connection)

    def obtener_contactos(self, password, cod_interno):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._call_all(cursor, "sp_listar_contactos_cliente", (cod_interno,))
        finally:
            self._close(cursor, connection)

    def crear_con_detalles(self, password, encabezado, detalles):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            fila = self._call(
                cursor,
                "sp_crear_cotizacion",
                (
                    encabezado["fecha_emision"], encabezado["id_tipo_cotizacion"],
                    encabezado["id_origen"], encabezado["id_moneda"], encabezado["impuesto"],
                    encabezado["porcentaje_igv"], encabezado["id_forma_pago"],
                    encabezado["id_garantia"], encabezado["tiempo_ejecucion"],
                    encabezado["tiempo_entrega"], encabezado["vigencia_dias"],
                    encabezado["exclusiones"], encabezado["observaciones"],
                    encabezado["cod_interno_cliente"], encabezado["id_contacto"],
                    encabezado["id_empleado"],
                ),
            )
            numero = (fila or {}).get("nmr_cotizacion")
            if not numero:
                raise RuntimeError("MySQL no devolvio el numero de cotizacion generado.")
            self._insertar_detalles(cursor, numero, detalles)
            connection.commit()
            return numero
        except Exception:
            connection.rollback()
            raise
        finally:
            self._close(cursor, connection)

    def actualizar_con_detalles(self, password, numero, encabezado, detalles):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._call(
                cursor,
                "sp_actualizar_cotizacion",
                (
                    numero, encabezado["fecha_emision"], encabezado["id_tipo_cotizacion"],
                    encabezado["id_origen"], encabezado["id_moneda"], encabezado["impuesto"],
                    encabezado["porcentaje_igv"], encabezado["id_forma_pago"], encabezado["id_garantia"],
                    encabezado["tiempo_ejecucion"], encabezado["tiempo_entrega"], encabezado["vigencia_dias"],
                    encabezado["exclusiones"], encabezado["observaciones"], encabezado["cod_interno_cliente"],
                    encabezado["id_contacto"], encabezado["id_empleado"],
                ),
            )
            self._call(cursor, "sp_eliminar_detalles_cotizacion", (numero,))
            self._insertar_detalles(cursor, numero, detalles)
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            self._close(cursor, connection)

    def _insertar_detalles(self, cursor, numero, detalles):
        for linea in detalles:
            self._call(
                cursor,
                "sp_agregar_detalle_cotizacion",
                (
                    numero, linea["cod_pro_ser"], linea["cantidad"],
                    linea["precio_unitario"], linea["alcance_tecnico"],
                ),
            )

    def listar(self, password, filtro=""):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._call_all(cursor, "sp_listar_cotizaciones", (filtro or "",))
        finally:
            self._close(cursor, connection)

    def obtener(self, password, numero):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            encabezado = self._call(cursor, "sp_obtener_cotizacion_encabezado", (numero,))
            if not encabezado:
                return None
            detalles = self._call_all(cursor, "sp_obtener_cotizacion_detalles", (numero,))
            return {"encabezado": encabezado, "detalles": detalles}
        finally:
            self._close(cursor, connection)

    def actualizar_estado(self, password, numero, id_estado):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._call(cursor, "sp_actualizar_estado_cotizacion", (numero, id_estado))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            self._close(cursor, connection)

    def obtener_resumen_dashboard(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            row = self._call(cursor, "sp_obtener_resumen_dashboard") or {}
            return {key: int(value or 0) for key, value in row.items()}
        finally:
            self._close(cursor, connection)

    def listar_estados(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._call_all(cursor, "sp_listar_parametros", ("estado_cotizacion",))
        finally:
            self._close(cursor, connection)

    def listar_recientes(self, password, limite=8):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._call_all(cursor, "sp_listar_cotizaciones_recientes", (int(limite),))
        finally:
            self._close(cursor, connection)