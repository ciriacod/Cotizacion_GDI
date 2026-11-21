
class CatalogoRepository:
    """Acceso a datos para los catálogos CARGO y ESPECIALIDAD."""

    def __init__(self, database):
        self.database = database

    # =================================================
    # CONSULTAR CARGOS
    # =================================================

    def obtener_cargos(self, password):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_cargo,
                    nombre_cargo,
                    descripcion,
                    estado
                FROM CARGO
                WHERE estado = 'Activo'
                ORDER BY nombre_cargo
                """
            )

            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    # =================================================
    # CONSULTAR ESPECIALIDADES
    # =================================================

    def obtener_especialidades(self, password):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_especialidad,
                    nombre_especialidad,
                    descripcion,
                    area_conocimiento,
                    certificacion_requerida,
                    estado
                FROM ESPECIALIDAD
                WHERE estado = 'Activo'
                ORDER BY nombre_especialidad
                """
            )

            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    # =================================================
    # REGISTRAR CARGO
    # =================================================

    def insertar_cargo(self, password, nombre, descripcion):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO CARGO (
                    nombre_cargo,
                    descripcion
                )
                VALUES (%s, %s)
                """,
                (nombre, descripcion)
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
    # MODIFICAR CARGO
    # =================================================

    def actualizar_cargo(
        self,
        password,
        id_cargo,
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
                UPDATE CARGO
                SET
                    nombre_cargo = %s,
                    descripcion = %s
                WHERE id_cargo = %s
                  AND estado = 'Activo'
                """,
                (nombre, descripcion, id_cargo)
            )

            # rowcount puede ser cero si los datos no cambiaron.
            # Por eso verificamos que el registro siga existiendo.
            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    SELECT 1
                    FROM CARGO
                    WHERE id_cargo = %s
                      AND estado = 'Activo'
                    """,
                    (id_cargo,)
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "El cargo no existe o ya no está activo."
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
    # DESACTIVAR CARGO
    # =================================================

    def desactivar_cargo(self, password, id_cargo):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE CARGO
                SET estado = 'Inactivo'
                WHERE id_cargo = %s
                  AND estado = 'Activo'
                """,
                (id_cargo,)
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "El cargo no existe o ya está inactivo."
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
    # REGISTRAR ESPECIALIDAD
    # =================================================

    def insertar_especialidad(
        self,
        password,
        nombre,
        descripcion,
        area,
        certificacion
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO ESPECIALIDAD (
                    nombre_especialidad,
                    descripcion,
                    area_conocimiento,
                    certificacion_requerida
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    nombre,
                    descripcion,
                    area,
                    certificacion
                )
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
    # MODIFICAR ESPECIALIDAD
    # =================================================

    def actualizar_especialidad(
        self,
        password,
        id_especialidad,
        nombre,
        descripcion,
        area,
        certificacion
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE ESPECIALIDAD
                SET
                    nombre_especialidad = %s,
                    descripcion = %s,
                    area_conocimiento = %s,
                    certificacion_requerida = %s
                WHERE id_especialidad = %s
                  AND estado = 'Activo'
                """,
                (
                    nombre,
                    descripcion,
                    area,
                    certificacion,
                    id_especialidad
                )
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    SELECT 1
                    FROM ESPECIALIDAD
                    WHERE id_especialidad = %s
                      AND estado = 'Activo'
                    """,
                    (id_especialidad,)
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "La especialidad no existe o ya no está activa."
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
    # DESACTIVAR ESPECIALIDAD
    # =================================================

    def desactivar_especialidad(
        self,
        password,
        id_especialidad
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE ESPECIALIDAD
                SET estado = 'Inactivo'
                WHERE id_especialidad = %s
                  AND estado = 'Activo'
                """,
                (id_especialidad,)
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "La especialidad no existe o ya está inactiva."
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
