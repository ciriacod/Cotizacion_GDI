class CatalogoRepository:
    """Acceso a datos para los catálogos CARGO y ESPECIALIDAD vía Procedimientos Almacenados."""

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

    def insertar_cargo(self, password, nombre, descripcion):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            res = self._ejecutar_procedimiento(cursor, "sp_crear_cargo", (nombre, descripcion))
            connection.commit()
            return res[0]["id_cargo"] if res else None
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar_cargo(self, password, id_cargo, nombre, descripcion):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_actualizar_cargo", (id_cargo, nombre, descripcion))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def desactivar_cargo(self, password, id_cargo):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_desactivar_cargo", (id_cargo,))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def insertar_especialidad(self, password, nombre, descripcion, area, certificacion):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            res = self._ejecutar_procedimiento(
                cursor, "sp_crear_especialidad", (nombre, descripcion, area, certificacion)
            )
            connection.commit()
            return res[0]["id_especialidad"] if res else None
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar_especialidad(self, password, id_especialidad, nombre, descripcion, area, certificacion):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(
                cursor, "sp_actualizar_especialidad", (id_especialidad, nombre, descripcion, area, certificacion)
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

    def desactivar_especialidad(self, password, id_especialidad):
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_desactivar_especialidad", (id_especialidad,))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()