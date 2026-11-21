
class ProductoServicioRepository:
    """Acceso a datos para productos, servicios y catálogos auxiliares."""

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

    # =================================================
    # CONSULTAR PRODUCTOS Y SERVICIOS
    # =================================================

    def obtener_catalogo(self, password):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    ps.cod_pro_ser,
                    ps.Descripcion AS descripcion,
                    ps.id_unidad,
                    ps.id_tipo,
                    um.nombre_unidad,
                    um.abreviatura,
                    tp.nombre_tipo,
                    ps.Precio_referencial AS precio_referencial,
                    ps.estado,
                    p.marca,
                    p.modelo,
                    p.`año` AS anio,
                    p.nmr_parte,
                    CASE
                        WHEN sv.cod_pro_ser IS NOT NULL THEN 'Servicio'
                        ELSE 'Producto'
                    END AS clasificacion
                FROM PRODUCTO_SERVICIO ps
                INNER JOIN UNIDAD_MEDIDA um
                    ON um.id_unidad = ps.id_unidad
                INNER JOIN TIPO_PRODUCTO tp
                    ON tp.id_tipo = ps.id_tipo
                LEFT JOIN PRODUCTO p
                    ON p.cod_pro_ser = ps.cod_pro_ser
                LEFT JOIN SERVICIO sv
                    ON sv.cod_pro_ser = ps.cod_pro_ser
                WHERE ps.estado = 'Activo'
                ORDER BY ps.cod_pro_ser
                """
            )

            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # =================================================
    # BUSCAR POR CÓDIGO
    # =================================================

    def obtener_por_codigo(self, password, codigo):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    ps.cod_pro_ser,
                    ps.Descripcion AS descripcion,
                    ps.id_unidad,
                    ps.id_tipo,
                    ps.Precio_referencial AS precio_referencial,
                    ps.estado,
                    p.marca,
                    p.modelo,
                    p.`año` AS anio,
                    p.nmr_parte,
                    sv.cod_pro_ser AS codigo_servicio
                FROM PRODUCTO_SERVICIO ps
                LEFT JOIN PRODUCTO p
                    ON p.cod_pro_ser = ps.cod_pro_ser
                LEFT JOIN SERVICIO sv
                    ON sv.cod_pro_ser = ps.cod_pro_ser
                WHERE ps.cod_pro_ser = %s
                  AND ps.estado = 'Activo'
                """,
                (codigo,)
            )

            return cursor.fetchone()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # =================================================
    # CONSULTAR UNIDADES DE MEDIDA
    # =================================================

    def obtener_unidades(self, password):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_unidad,
                    nombre_unidad,
                    abreviatura,
                    estado
                FROM UNIDAD_MEDIDA
                WHERE estado = 'Activo'
                ORDER BY nombre_unidad
                """
            )

            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # =================================================
    # CONSULTAR TIPOS DE PRODUCTO
    # =================================================

    def obtener_tipos(self, password):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_tipo,
                    nombre_tipo,
                    descripcion,
                    estado
                FROM TIPO_PRODUCTO
                WHERE estado = 'Activo'
                ORDER BY id_tipo
                """
            )

            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    def obtener_nombre_tipo(self, password, id_tipo):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT nombre_tipo FROM TIPO_PRODUCTO WHERE id_tipo=%s AND estado='Activo'",
                (id_tipo,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    # =================================================
    # REGISTRAR PRODUCTO O SERVICIO
    # =================================================

    def insertar_item(
        self,
        password,
        descripcion,
        id_unidad,
        id_tipo,
        precio,
        marca=None,
        modelo=None,
        anio=None,
        nmr_parte=None
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_crear_producto_servicio",
                (
                    descripcion,
                    id_unidad,
                    id_tipo,
                    precio
                )
            )

            cursor.execute(
                "SELECT nombre_tipo FROM TIPO_PRODUCTO WHERE id_tipo=%s AND estado='Activo'",
                (id_tipo,),
            )
            tipo_row = cursor.fetchone()
            tipo_nombre = (tipo_row["nombre_tipo"] if tipo_row else "").strip().casefold()
            codigo = None

            if resultados:
                codigo = resultados[0].get("cod_pro_ser")

            if not codigo:
                cursor.execute(
                    "SELECT @ultimo_cod_pro_ser AS cod_pro_ser"
                )

                fila = cursor.fetchone()
                codigo = fila.get("cod_pro_ser") if fila else None

            if not codigo:
                raise RuntimeError(
                    "MySQL no devolvió el código del producto o servicio."
                )

            if tipo_nombre in {"equipo", "material"}:

                cursor.execute(
                    """
                    INSERT INTO PRODUCTO (
                        cod_pro_ser,
                        marca,
                        modelo,
                        `año`,
                        nmr_parte
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        codigo,
                        marca,
                        modelo,
                        anio,
                        nmr_parte
                    )
                )

            elif tipo_nombre == "servicio":

                cursor.execute(
                    """
                    INSERT INTO SERVICIO (cod_pro_ser)
                    VALUES (%s)
                    """,
                    (codigo,)
                )

            else:
                raise ValueError(
                    "El tipo seleccionado no está soportado. Se admiten únicamente Equipo, Material o Servicio."
                )

            connection.commit()
            return codigo

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # =================================================
    # MODIFICAR PRODUCTO O SERVICIO
    # =================================================

    def actualizar_item(
        self,
        password,
        codigo,
        descripcion,
        id_unidad,
        id_tipo,
        precio,
        marca=None,
        modelo=None,
        anio=None,
        nmr_parte=None
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT ps.id_tipo, tp.nombre_tipo
                FROM PRODUCTO_SERVICIO ps
                INNER JOIN TIPO_PRODUCTO tp ON tp.id_tipo=ps.id_tipo
                WHERE ps.cod_pro_ser = %s
                  AND ps.estado = 'Activo'
                FOR UPDATE
                """,
                (codigo,)
            )

            actual = cursor.fetchone()

            if actual is None:
                raise ValueError(
                    "El producto o servicio no existe o está inactivo."
                )

            if int(actual["id_tipo"]) != int(id_tipo):
                raise ValueError(
                    "No se permite cambiar el tipo de un registro existente. "
                    "El código y su clasificación se generan según el tipo."
                )

            cursor.execute(
                """
                UPDATE PRODUCTO_SERVICIO
                SET
                    Descripcion = %s,
                    id_unidad = %s,
                    Precio_referencial = %s
                WHERE cod_pro_ser = %s
                  AND estado = 'Activo'
                """,
                (
                    descripcion,
                    id_unidad,
                    precio,
                    codigo
                )
            )

            tipo_nombre = actual["nombre_tipo"].strip().casefold()
            if tipo_nombre in {"equipo", "material"}:

                cursor.execute(
                    """
                    UPDATE PRODUCTO
                    SET
                        marca = %s,
                        modelo = %s,
                        `año` = %s,
                        nmr_parte = %s
                    WHERE cod_pro_ser = %s
                    """,
                    (
                        marca,
                        modelo,
                        anio,
                        nmr_parte,
                        codigo
                    )
                )

                if cursor.rowcount == 0:
                    cursor.execute(
                        """
                        SELECT 1
                        FROM PRODUCTO
                        WHERE cod_pro_ser = %s
                        """,
                        (codigo,)
                    )

                    if cursor.fetchone() is None:
                        raise ValueError(
                            "No se encontró la ficha técnica del producto."
                        )

            elif tipo_nombre == "servicio":

                cursor.execute(
                    """
                    SELECT 1
                    FROM SERVICIO
                    WHERE cod_pro_ser = %s
                    """,
                    (codigo,)
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "No se encontró la clasificación de servicio."
                    )

            else:
                raise ValueError(
                    "El tipo de registro no es válido."
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

    # =================================================
    # DESACTIVAR PRODUCTO O SERVICIO
    # =================================================

    def desactivar_item(self, password, codigo):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            self._ejecutar_procedimiento(
                cursor,
                "sp_eliminar_producto_servicio",
                (codigo,)
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

    # =================================================
    # REGISTRAR UNIDAD DE MEDIDA
    # =================================================

    def insertar_unidad(self, password, nombre, abreviatura):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO UNIDAD_MEDIDA (
                    nombre_unidad,
                    abreviatura
                )
                VALUES (%s, %s)
                """,
                (nombre, abreviatura)
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

    # =================================================
    # MODIFICAR UNIDAD DE MEDIDA
    # =================================================

    def actualizar_unidad(
        self,
        password,
        id_unidad,
        nombre,
        abreviatura
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE UNIDAD_MEDIDA
                SET
                    nombre_unidad = %s,
                    abreviatura = %s
                WHERE id_unidad = %s
                  AND estado = 'Activo'
                """,
                (
                    nombre,
                    abreviatura,
                    id_unidad
                )
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    SELECT 1
                    FROM UNIDAD_MEDIDA
                    WHERE id_unidad = %s
                      AND estado = 'Activo'
                    """,
                    (id_unidad,)
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "La unidad no existe o está inactiva."
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

    # =================================================
    # DESACTIVAR UNIDAD DE MEDIDA
    # =================================================

    def desactivar_unidad(self, password, id_unidad):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM PRODUCTO_SERVICIO
                WHERE id_unidad = %s
                  AND estado = 'Activo'
                """,
                (id_unidad,)
            )

            if cursor.fetchone()[0] > 0:
                raise ValueError(
                    "No se puede desactivar esta unidad porque está siendo "
                    "utilizada por productos o servicios activos. Cambia "
                    "primero sus unidades de medida."
                )

            cursor.execute(
                """
                UPDATE UNIDAD_MEDIDA
                SET estado = 'Inactivo'
                WHERE id_unidad = %s
                  AND estado = 'Activo'
                """,
                (id_unidad,)
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "La unidad no existe o ya está inactiva."
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

    # =================================================
    # MODIFICAR TIPO DE PRODUCTO
    # =================================================

    def actualizar_tipo(
        self,
        password,
        id_tipo,
        nombre,
        descripcion
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE TIPO_PRODUCTO
                SET
                    nombre_tipo = %s,
                    descripcion = %s
                WHERE id_tipo = %s
                  AND estado = 'Activo'
                """,
                (
                    nombre,
                    descripcion,
                    id_tipo
                )
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    SELECT 1
                    FROM TIPO_PRODUCTO
                    WHERE id_tipo = %s
                      AND estado = 'Activo'
                    """,
                    (id_tipo,)
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "El tipo no existe o está inactivo."
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
