
class EmpleadoRepository:
    """Acceso a datos de empleados y sus catálogos."""

    def __init__(self, database):
        self.database = database

    @staticmethod
    def _ejecutar_procedimiento(cursor, nombre, parametros=()):
        marcadores = ", ".join(["%s"] * len(parametros))

        cursor.execute(
            f"CALL {nombre}({marcadores})",
            parametros
        )

        resultados = cursor.fetchall() if cursor.with_rows else []

        # Consumir los demás resultados evita errores de sincronización.
        while cursor.nextset():
            if cursor.with_rows:
                cursor.fetchall()

        return resultados

    # -------------------------------------------------
    # LISTAR EMPLEADOS
    # -------------------------------------------------

    def obtener_todos(self, password):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            return self._ejecutar_procedimiento(
                cursor,
                "sp_listar_empleados_activos"
            )

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # -------------------------------------------------
    # BUSCAR EMPLEADO POR ID
    # -------------------------------------------------

    def obtener_por_id(self, password, id_empleado):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id_empleado,
                    DNI,
                    nombre_completo,
                    email,
                    telefono,
                    id_cargo,
                    id_especialidad,
                    estado
                FROM EMPLEADO
                WHERE id_empleado = %s
                  AND estado = 'Activo'
                """,
                (id_empleado,)
            )

            return cursor.fetchone()

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # -------------------------------------------------
    # LISTAR CARGOS ACTIVOS
    # -------------------------------------------------

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
                    descripcion
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

    # -------------------------------------------------
    # LISTAR ESPECIALIDADES ACTIVAS
    # -------------------------------------------------

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
                    certificacion_requerida
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

    # -------------------------------------------------
    # REGISTRAR EMPLEADO
    # -------------------------------------------------

    def insertar(
        self,
        password,
        dni,
        nombre_completo,
        email,
        password_hash,
        telefono,
        id_cargo,
        id_especialidad
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_crear_empleado",
                (
                    dni,
                    nombre_completo,
                    email,
                    password_hash,
                    telefono,
                    id_cargo,
                    id_especialidad
                )
            )

            connection.commit()

            if resultados:
                return resultados[0].get("id_empleado")

            return None

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    # -------------------------------------------------
    # MODIFICAR EMPLEADO
    # -------------------------------------------------

    def actualizar(
        self,
        password,
        id_empleado,
        dni,
        nombre_completo,
        email,
        telefono,
        id_cargo,
        id_especialidad
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            # El procedimiento actualiza correo, teléfono,
            # cargo y especialidad.
            self._ejecutar_procedimiento(
                cursor,
                "sp_actualizar_empleado",
                (
                    id_empleado,
                    email,
                    telefono,
                    id_cargo,
                    id_especialidad
                )
            )

            # El procedimiento no contempla DNI ni nombre.
            cursor.execute(
                """
                UPDATE EMPLEADO
                SET
                    DNI = %s,
                    nombre_completo = %s
                WHERE id_empleado = %s
                  AND estado = 'Activo'
                """,
                (
                    dni,
                    nombre_completo,
                    id_empleado
                )
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

    # -------------------------------------------------
    # DESACTIVAR EMPLEADO
    # -------------------------------------------------

    def eliminar(self, password, id_empleado):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            self._ejecutar_procedimiento(
                cursor,
                "sp_eliminar_empleado",
                (id_empleado,)
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
