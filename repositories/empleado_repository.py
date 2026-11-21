class EmpleadoRepository:
    """Acceso a datos de empleados y sus catálogos vía Procedimientos Almacenados."""

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

    def obtener_todos(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_empleados_activos")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_por_id(self, password, id_empleado):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            filas = self._ejecutar_procedimiento(cursor, "sp_obtener_empleado_por_id", (id_empleado,))
            return filas[0] if filas else None
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_cargos(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_cargos_activos")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def obtener_especialidades(self, password):
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_especialidades_activas")
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def insertar(self, password, dni, nombre_completo, email, password_hash, telefono, id_cargo, id_especialidad):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_crear_empleado",
                (dni, nombre_completo, email, password_hash, telefono, id_cargo, id_especialidad),
            )
            connection.commit()
            return resultados[0].get("id_empleado") if resultados else None
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar(self, password, id_empleado, dni, nombre_completo, email, telefono, id_cargo, id_especialidad):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(
                cursor,
                "sp_actualizar_empleado",
                (id_empleado, dni, nombre_completo, email, telefono, id_cargo, id_especialidad),
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

    def eliminar(self, password, id_empleado):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_eliminar_empleado", (id_empleado,))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()