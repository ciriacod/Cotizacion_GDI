class ClienteRepository:
    """Acceso a datos del módulo de clientes y contactos vía Procedimientos Almacenados."""

    def __init__(self, database):
        self.database = database

    @staticmethod
    def _ejecutar_procedimiento(cursor, nombre, parametros=()):
        marcadores = ", ".join(["%s"] * len(parametros))
        cursor.execute(f"CALL {nombre}({marcadores})", parametros)
        resultados = cursor.fetchall() if cursor.with_rows else []
        while cursor.nextset():
            if cursor.with_rows:
                cursor.fetchall()
        return resultados

    @staticmethod
    def _obtener_id_distrito(valor):
        try:
            return int(valor)
        except (TypeError, ValueError):
            raise ValueError("El distrito seleccionado no es válido.")

    def obtener_todos(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_clientes_activos")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_distritos(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_distritos_activos")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_por_codigo(self, password, cod_interno):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            filas = self._ejecutar_procedimiento(cursor, "sp_obtener_cliente_por_codigo", (cod_interno,))
            return filas[0] if filas else None
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def insertar(self, password, ruc, razon_social, direccion_via, cod_distrito):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_crear_cliente",
                (ruc, razon_social, direccion_via, self._obtener_id_distrito(cod_distrito)),
            )
            if not resultados or not resultados[0].get("cod_interno"):
                raise RuntimeError("No se pudo recuperar el código del cliente registrado.")
            connection.commit()
            return resultados[0]["cod_interno"]
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar(self, password, cod_interno, ruc, razon_social, direccion_via, cod_distrito):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_actualizar_cliente",
                (cod_interno, ruc, razon_social, direccion_via, self._obtener_id_distrito(cod_distrito)),
            )
            connection.commit()
            return resultados[0]["filas_afectadas"] if resultados else 1
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def eliminar(self, password, cod_interno):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(cursor, "sp_eliminar_cliente", (cod_interno,))
            connection.commit()
            return resultados[0]["filas_afectadas"] if resultados else 0
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_contactos(self, password, cod_interno):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_contactos_cliente", (cod_interno,))
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def insertar_contacto(self, password, cod_interno, nombre_contacto, telefono_contacto, email_contacto):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_crear_contacto_cliente",
                (cod_interno, nombre_contacto, telefono_contacto, email_contacto),
            )
            if not resultados or resultados[0].get("id_contacto") is None:
                raise RuntimeError("No se pudo recuperar el identificador del contacto.")
            connection.commit()
            return resultados[0]["id_contacto"]
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar_contacto(self, password, cod_interno, nro_contacto, nombre_contacto, telefono_contacto, email_contacto):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_actualizar_contacto_cliente",
                (cod_interno, nro_contacto, nombre_contacto, telefono_contacto, email_contacto),
            )
            connection.commit()
            return resultados[0]["filas_afectadas"] if resultados else 1
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def eliminar_contacto(self, password, cod_interno, nro_contacto):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(
                cursor, "sp_eliminar_contacto_cliente", (cod_interno, nro_contacto)
            )
            connection.commit()
            return resultados[0]["filas_afectadas"] if resultados else 1
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()