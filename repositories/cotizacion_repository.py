"""Persistencia SQL del modulo de cotizaciones (sin ORM)."""

from __future__ import annotations


class CotizacionRepository:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def _call(cursor, nombre: str, parametros=()):
        marcadores = ", ".join(["%s"] * len(parametros))
        cursor.execute(f"CALL {nombre}({marcadores})", parametros)
        filas = cursor.fetchall() if cursor.with_rows else []
        while cursor.nextset():
            if cursor.with_rows:
                cursor.fetchall()
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
            consultas = {
                "clientes": """
                    SELECT cod_interno, razon_social, ruc
                    FROM CLIENTE WHERE estado='Activo' ORDER BY razon_social
                """,
                "empleados": """
                    SELECT id_empleado, DNI, nombre_completo
                    FROM EMPLEADO WHERE estado='Activo' ORDER BY nombre_completo
                """,
                "tipos": """
                    SELECT id_tipo_cotizacion, descripcion
                    FROM TIPO_COTIZACION WHERE estado='Activo' ORDER BY descripcion
                """,
                "origenes": """
                    SELECT id_origen, descripcion
                    FROM ORIGEN_SOLICITUD WHERE estado='Activo' ORDER BY descripcion
                """,
                "monedas": """
                    SELECT id_moneda, nombre, simbolo, codigo_iso
                    FROM MONEDA WHERE estado='Activo' ORDER BY nombre
                """,
                "formas_pago": """
                    SELECT id_forma_pago, descripcion, dias_credito
                    FROM FORMA_PAGO WHERE estado='Activo' ORDER BY dias_credito, descripcion
                """,
                "garantias": """
                    SELECT id_garantia, tiempo_garantia, unidad_garantia
                    FROM GARANTIA WHERE estado='Activo' ORDER BY tiempo_garantia
                """,
                "estados": """
                    SELECT id_estado, descripcion
                    FROM ESTADO_COTIZACION WHERE estado='Activo' ORDER BY id_estado
                """,
                "productos": """
                    SELECT ps.cod_pro_ser, ps.Descripcion, ps.Precio_referencial,
                           tp.nombre_tipo, um.abreviatura
                    FROM PRODUCTO_SERVICIO ps
                    INNER JOIN TIPO_PRODUCTO tp ON tp.id_tipo = ps.id_tipo
                    INNER JOIN UNIDAD_MEDIDA um ON um.id_unidad = ps.id_unidad
                    WHERE ps.estado='Activo'
                    ORDER BY tp.nombre_tipo, ps.Descripcion
                """,
            }
            resultado = {}
            for clave, sql in consultas.items():
                cursor.execute(sql)
                resultado[clave] = cursor.fetchall()
            return resultado
        finally:
            self._close(cursor, connection)

    def obtener_contactos(self, password, cod_interno):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT id_contacto, nombre_contacto, telefono_contacto, email_contacto
                   FROM CONTACTO_CLIENTE
                   WHERE cod_interno=%s AND estado='Activo'
                   ORDER BY nombre_contacto""",
                (cod_interno,),
            )
            return cursor.fetchall()
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
                cursor.execute("SELECT @ultimo_nmr_cotizacion AS numero")
                row = cursor.fetchone()
                numero = row["numero"] if row else None
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
            cursor.execute(
                "SELECT nmr_cotizacion FROM COTIZACION WHERE nmr_cotizacion=%s FOR UPDATE",
                (numero,),
            )
            if cursor.fetchone() is None:
                raise ValueError("La cotizacion seleccionada ya no existe.")

            self._call(
                cursor, "sp_actualizar_cotizacion",
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
            patron = f"%{(filtro or '').strip()}%"
            cursor.execute(
                """SELECT c.nmr_cotizacion, c.fecha_emision, cl.razon_social,
                          ec.descripcion AS estado, m.codigo_iso AS moneda,
                          c.vigencia_dias,
                          DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY) AS fecha_vencimiento,
                          COALESCE(d.subtotal, 0.00) AS subtotal
                   FROM COTIZACION c
                   INNER JOIN CLIENTE cl ON cl.cod_interno=c.cod_interno_cliente
                   INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                   INNER JOIN MONEDA m ON m.id_moneda=c.id_moneda
                   LEFT JOIN (
                       SELECT nmr_cotizacion, SUM(cantidad * precio_unitario) AS subtotal
                       FROM DETALLE_COTIZACION GROUP BY nmr_cotizacion
                   ) d ON d.nmr_cotizacion=c.nmr_cotizacion
                   WHERE c.nmr_cotizacion LIKE %s OR cl.razon_social LIKE %s
                      OR ec.descripcion LIKE %s
                   ORDER BY c.fecha_emision DESC, c.nmr_cotizacion DESC""",
                (patron, patron, patron),
            )
            return cursor.fetchall()
        finally:
            self._close(cursor, connection)

    def obtener(self, password, numero):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT c.*, cl.ruc, cl.razon_social, cl.direccion_via,
                          di.nombre_distrito, pr.nombre_provincia, de.nombre_departamento,
                          cc.nombre_contacto, cc.telefono_contacto, cc.email_contacto,
                          e.DNI, e.nombre_completo AS responsable,
                          tc.descripcion AS tipo_cotizacion,
                          os.descripcion AS origen_solicitud,
                          m.nombre AS moneda_nombre, m.simbolo AS moneda_simbolo, m.codigo_iso,
                          fp.descripcion AS forma_pago,
                          ec.descripcion AS estado_descripcion,
                          g.tiempo_garantia, g.unidad_garantia
                   FROM COTIZACION c
                   INNER JOIN CLIENTE cl ON cl.cod_interno=c.cod_interno_cliente
                   INNER JOIN DISTRITO di ON di.id_distrito=cl.id_distrito
                   INNER JOIN PROVINCIA pr ON pr.id_provincia=di.id_provincia
                   INNER JOIN DEPARTAMENTO de ON de.id_departamento=pr.id_departamento
                   LEFT JOIN CONTACTO_CLIENTE cc ON cc.id_contacto=c.id_contacto
                   INNER JOIN EMPLEADO e ON e.id_empleado=c.id_empleado
                   INNER JOIN TIPO_COTIZACION tc ON tc.id_tipo_cotizacion=c.id_tipo_cotizacion
                   INNER JOIN ORIGEN_SOLICITUD os ON os.id_origen=c.id_origen
                   INNER JOIN MONEDA m ON m.id_moneda=c.id_moneda
                   INNER JOIN FORMA_PAGO fp ON fp.id_forma_pago=c.id_forma_pago
                   INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                   INNER JOIN GARANTIA g ON g.id_garantia=c.id_garantia
                   WHERE c.nmr_cotizacion=%s""",
                (numero,),
            )
            encabezado = cursor.fetchone()
            if not encabezado:
                return None
            cursor.execute(
                """SELECT d.id_detalle, d.item, d.cod_pro_ser,
                          ps.Descripcion AS descripcion, um.abreviatura AS unidad,
                          d.cantidad, d.precio_unitario, d.alcance_tecnico
                   FROM DETALLE_COTIZACION d
                   INNER JOIN PRODUCTO_SERVICIO ps ON ps.cod_pro_ser=d.cod_pro_ser
                   INNER JOIN UNIDAD_MEDIDA um ON um.id_unidad=ps.id_unidad
                   WHERE d.nmr_cotizacion=%s
                   ORDER BY d.item""",
                (numero,),
            )
            return {"encabezado": encabezado, "detalles": cursor.fetchall()}
        finally:
            self._close(cursor, connection)

    def actualizar_estado(self, password, numero, id_estado):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor()
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
            cursor.execute(
                """SELECT
                       COUNT(DISTINCT c.nmr_cotizacion) AS total_cotizaciones,
                       SUM(CASE WHEN ec.descripcion IN ('En revision','En revisión','Enviada','En negociacion','En negociación') THEN 1 ELSE 0 END) AS pendientes,
                       SUM(CASE WHEN ec.descripcion='Aprobada' THEN 1 ELSE 0 END) AS aprobadas,
                       (SELECT COUNT(*) FROM CLIENTE WHERE estado='Activo') AS clientes
                   FROM COTIZACION c
                   INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado"""
            )
            row = cursor.fetchone() or {}
            return {key: int(value or 0) for key, value in row.items()}
        finally:
            self._close(cursor, connection)

    def listar_estados(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_estado, descripcion FROM ESTADO_COTIZACION WHERE estado='Activo' ORDER BY id_estado"
            )
            return cursor.fetchall()
        finally:
            self._close(cursor, connection)

    def listar_recientes(self, password, limite=8):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT c.nmr_cotizacion, c.fecha_emision, cl.razon_social,
                          e.nombre_completo AS responsable, ec.descripcion AS estado
                   FROM COTIZACION c
                   INNER JOIN CLIENTE cl ON cl.cod_interno=c.cod_interno_cliente
                   INNER JOIN EMPLEADO e ON e.id_empleado=c.id_empleado
                   INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                   ORDER BY c.fecha_emision DESC, c.nmr_cotizacion DESC
                   LIMIT %s""",
                (max(1, min(int(limite), 50)),),
            )
            return cursor.fetchall()
        finally:
            self._close(cursor, connection)
