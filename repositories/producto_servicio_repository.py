class ProductoServicioRepository:
    """Acceso a datos para productos, servicios y catálogos vía Procedimientos Almacenados."""

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

    def obtener_catalogo(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_catalogo_activo")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_por_codigo(self, password, codigo):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            filas = self._ejecutar_procedimiento(cursor, "sp_obtener_producto_por_codigo", (codigo,))
            return filas[0] if filas else None
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_unidades(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_unidades_activas")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_tipos(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_tipos_producto")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_nombre_tipo(self, password, id_tipo):
        tipos = self.obtener_tipos(password)
        for t in tipos:
            if int(t["id_tipo"]) == int(id_tipo):
                return t["nombre_tipo"]
        return None

    def insertar_item(
        self, password, descripcion, id_unidad, id_tipo, precio,
        marca=None, modelo=None, anio=None, nmr_parte=None
    ):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_registrar_item_completo",
                (descripcion, id_unidad, id_tipo, precio, marca, modelo, anio, nmr_parte),
            )
            codigo = resultados[0].get("cod_pro_ser") if resultados else None
            if not codigo:
                raise RuntimeError("MySQL no devolvió el código del producto o servicio.")
            connection.commit()
            return codigo
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar_item(
        self, password, codigo, descripcion, id_unidad, id_tipo, precio,
        marca=None, modelo=None, anio=None, nmr_parte=None
    ):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(
                cursor,
                "sp_actualizar_item_completo",
                (codigo, descripcion, id_unidad, id_tipo, precio, marca, modelo, anio, nmr_parte),
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

    def desactivar_item(self, password, codigo):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_eliminar_producto_servicio", (codigo,))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def insertar_unidad(self, password, nombre, abreviatura):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(cursor, "sp_crear_unidad", (nombre, abreviatura))
            connection.commit()
            return resultados[0]["id_unidad"] if resultados else None
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar_unidad(self, password, id_unidad, nombre, abreviatura):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_actualizar_unidad", (id_unidad, nombre, abreviatura))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def desactivar_unidad(self, password, id_unidad):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_desactivar_unidad", (id_unidad,))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar_tipo(self, password, id_tipo, nombre, descripcion):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_actualizar_tipo_producto", (id_tipo, nombre, descripcion))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()