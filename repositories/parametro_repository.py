class ParametroRepository:
    """Acceso a datos de los seis catálogos de parámetros vía Procedimientos Almacenados."""

    CATALOGOS = {
        "tipo_cotizacion": ("descripcion",),
        "origen_solicitud": ("descripcion",),
        "moneda": ("nombre", "simbolo", "codigo_iso"),
        "forma_pago": ("descripcion", "dias_credito"),
        "estado_cotizacion": ("descripcion",),
        "garantia": ("tiempo_garantia", "unidad_garantia"),
    }

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

    @classmethod
    def _campos(cls, catalogo):
        if catalogo not in cls.CATALOGOS:
            raise ValueError("El catálogo solicitado no es válido.")
        return cls.CATALOGOS[catalogo]

    def listar(self, password, catalogo):
        self._campos(catalogo)
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            return self._ejecutar_procedimiento(cursor, "sp_listar_parametros", (catalogo,))
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def insertar(self, password, catalogo, datos):
        campos = self._campos(catalogo)
        if set(datos.keys()) != set(campos):
            raise ValueError("Los campos enviados no corresponden al catálogo.")

        vals = [datos[c] for c in campos]
        while len(vals) < 3:
            vals.append(None)

        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            res = self._ejecutar_procedimiento(
                cursor, "sp_insertar_parametro", (catalogo, vals[0], vals[1], vals[2])
            )
            connection.commit()
            return res[0]["nuevo_id"] if res else None
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar(self, password, catalogo, identificador, datos):
        campos = self._campos(catalogo)
        if set(datos.keys()) != set(campos):
            raise ValueError("Los campos enviados no corresponden al catálogo.")

        vals = [datos[c] for c in campos]
        while len(vals) < 3:
            vals.append(None)

        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(
                cursor, "sp_actualizar_parametro", (catalogo, identificador, vals[0], vals[1], vals[2])
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
        self._campos(catalogo)
        connection = self.database.connect(password)
        cursor = None
        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)
            self._ejecutar_procedimiento(cursor, "sp_desactivar_parametro", (catalogo, identificador))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()