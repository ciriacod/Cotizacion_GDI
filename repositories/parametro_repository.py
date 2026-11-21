
class ParametroRepository:
    """Acceso a datos de los seis catálogos de parámetros."""

    CATALOGOS = {
        "tipo_cotizacion": {
            "tabla": "TIPO_COTIZACION",
            "pk": "id_tipo_cotizacion",
            "campos": ("descripcion",),
            "orden": "descripcion",
            "referencia": ("id_tipo_cotizacion", "TIPO_COTIZACION"),
        },
        "origen_solicitud": {
            "tabla": "ORIGEN_SOLICITUD",
            "pk": "id_origen",
            "campos": ("descripcion",),
            "orden": "descripcion",
            "referencia": ("id_origen", "ORIGEN_SOLICITUD"),
        },
        "moneda": {
            "tabla": "MONEDA",
            "pk": "id_moneda",
            "campos": ("nombre", "simbolo", "codigo_iso"),
            "orden": "nombre",
            "referencia": ("id_moneda", "MONEDA"),
        },
        "forma_pago": {
            "tabla": "FORMA_PAGO",
            "pk": "id_forma_pago",
            "campos": ("descripcion", "dias_credito"),
            "orden": "descripcion",
            "referencia": ("id_forma_pago", "FORMA_PAGO"),
        },
        "estado_cotizacion": {
            "tabla": "ESTADO_COTIZACION",
            "pk": "id_estado",
            "campos": ("descripcion",),
            "orden": "id_estado",
            "referencia": ("id_estado", "ESTADO_COTIZACION"),
        },
        "garantia": {
            "tabla": "GARANTIA",
            "pk": "id_garantia",
            "campos": ("tiempo_garantia", "unidad_garantia"),
            "orden": "tiempo_garantia",
            "referencia": ("id_garantia", "GARANTIA"),
        },
    }

    COLUMNAS_COTIZACION = {
        "tipo_cotizacion": "id_tipo_cotizacion",
        "origen_solicitud": "id_origen",
        "moneda": "id_moneda",
        "forma_pago": "id_forma_pago",
        "estado_cotizacion": "id_estado",
        "garantia": "id_garantia",
    }

    def __init__(self, database):
        self.database = database

    @classmethod
    def _configuracion(cls, catalogo):
        if catalogo not in cls.CATALOGOS:
            raise ValueError("El catálogo solicitado no es válido.")
        return cls.CATALOGOS[catalogo]

    def listar(self, password, catalogo):
        config = self._configuracion(catalogo)
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            columnas = ", ".join(
                [config["pk"], *config["campos"], "estado"]
            )

            cursor.execute(
                f"""
                SELECT {columnas}
                FROM {config["tabla"]}
                WHERE estado = 'Activo'
                ORDER BY {config["orden"]}
                """
            )
            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def insertar(self, password, catalogo, datos):
        config = self._configuracion(catalogo)

        if set(datos.keys()) != set(config["campos"]):
            raise ValueError("Los campos enviados no corresponden al catálogo.")

        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            columnas = ", ".join(config["campos"])
            marcadores = ", ".join(["%s"] * len(config["campos"]))
            valores = tuple(datos[campo] for campo in config["campos"])

            cursor.execute(
                f"""
                INSERT INTO {config["tabla"]} ({columnas})
                VALUES ({marcadores})
                """,
                valores
            )

            nuevo_id = cursor.lastrowid
            connection.commit()
            return nuevo_id

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar(self, password, catalogo, identificador, datos):
        config = self._configuracion(catalogo)

        if set(datos.keys()) != set(config["campos"]):
            raise ValueError("Los campos enviados no corresponden al catálogo.")

        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                f"""
                SELECT 1
                FROM {config["tabla"]}
                WHERE {config["pk"]} = %s
                  AND estado = 'Activo'
                FOR UPDATE
                """,
                (identificador,)
            )

            if cursor.fetchone() is None:
                raise ValueError("El parámetro no existe o está inactivo.")

            asignaciones = ", ".join(
                f"{campo} = %s" for campo in config["campos"]
            )
            valores = tuple(datos[campo] for campo in config["campos"])

            cursor.execute(
                f"""
                UPDATE {config["tabla"]}
                SET {asignaciones}
                WHERE {config["pk"]} = %s
                  AND estado = 'Activo'
                """,
                (*valores, identificador)
            )

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def desactivar(self, password, catalogo, identificador):
        config = self._configuracion(catalogo)
        columna_referencia = self.COLUMNAS_COTIZACION[catalogo]

        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                f"""
                SELECT 1
                FROM {config["tabla"]}
                WHERE {config["pk"]} = %s
                  AND estado = 'Activo'
                FOR UPDATE
                """,
                (identificador,)
            )

            if cursor.fetchone() is None:
                raise ValueError("El parámetro no existe o ya está inactivo.")

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM COTIZACION
                WHERE {columna_referencia} = %s
                """,
                (identificador,)
            )

            cantidad = cursor.fetchone()[0]

            if cantidad > 0:
                raise ValueError(
                    "No se puede desactivar este parámetro porque está "
                    f"utilizado en {cantidad} cotización(es)."
                )

            cursor.execute(
                f"""
                UPDATE {config["tabla"]}
                SET estado = 'Inactivo'
                WHERE {config["pk"]} = %s
                  AND estado = 'Activo'
                """,
                (identificador,)
            )

            if cursor.rowcount == 0:
                raise ValueError("No se pudo desactivar el parámetro.")

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
