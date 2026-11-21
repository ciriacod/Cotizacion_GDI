
class ClienteRepository:
    """
    Acceso a datos del módulo de clientes y contactos.

    Utiliza los procedimientos almacenados definidos en la nueva
    base de datos y consultas SQL para las operaciones que todavía
    no tienen un procedimiento almacenado.
    """

    def __init__(self, database):
        self.database = database

    @staticmethod
    def _ejecutar_procedimiento(cursor, nombre, parametros=()):
        """
        Ejecuta un procedimiento almacenado y devuelve su primer
        conjunto de resultados, si existe.
        """
        marcadores = ", ".join(["%s"] * len(parametros))
        consulta = f"CALL {nombre}({marcadores})"

        cursor.execute(consulta, parametros)

        resultados = []

        if cursor.with_rows:
            resultados = cursor.fetchall()

        # Consumir posibles conjuntos de resultados adicionales.
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

    # =====================================================
    # CLIENTES
    # =====================================================

    def obtener_todos(self, password):
        connection = self.database.connect(password)

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    c.cod_interno,
                    c.ruc,
                    c.razon_social,
                    c.direccion_via,
                    c.id_distrito AS cod_distrito,
                    d.nombre_distrito,
                    p.nombre_provincia,
                    dep.nombre_departamento
                FROM CLIENTE AS c
                INNER JOIN DISTRITO AS d
                    ON c.id_distrito = d.id_distrito
                INNER JOIN PROVINCIA AS p
                    ON d.id_provincia = p.id_provincia
                INNER JOIN DEPARTAMENTO AS dep
                    ON p.id_departamento = dep.id_departamento
                WHERE c.estado = 'Activo'
                ORDER BY c.razon_social
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def obtener_distritos(self, password):
        connection = self.database.connect(password)

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    d.id_distrito AS cod_distrito,
                    d.nombre_distrito,
                    p.nombre_provincia,
                    dep.nombre_departamento
                FROM DISTRITO AS d
                INNER JOIN PROVINCIA AS p
                    ON d.id_provincia = p.id_provincia
                INNER JOIN DEPARTAMENTO AS dep
                    ON p.id_departamento = dep.id_departamento
                WHERE d.estado = 'Activo'
                  AND p.estado = 'Activo'
                  AND dep.estado = 'Activo'
                ORDER BY
                    dep.nombre_departamento,
                    p.nombre_provincia,
                    d.nombre_distrito
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def obtener_por_codigo(self, password, cod_interno):
        connection = self.database.connect(password)

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    cod_interno,
                    ruc,
                    razon_social,
                    direccion_via,
                    id_distrito AS cod_distrito
                FROM CLIENTE
                WHERE cod_interno = %s
                  AND estado = 'Activo'
            """, (cod_interno,))

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def insertar(
        self,
        password,
        ruc,
        razon_social,
        direccion_via,
        cod_distrito
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_crear_cliente",
                (
                    ruc,
                    razon_social,
                    direccion_via,
                    self._obtener_id_distrito(cod_distrito)
                )
            )

            if not resultados:
                raise RuntimeError(
                    "El procedimiento no devolvió el cliente registrado."
                )

            cliente = resultados[0]
            codigo = cliente.get("cod_interno")

            if not codigo:
                raise RuntimeError(
                    "No se pudo recuperar el código del cliente registrado."
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

    def actualizar(
        self,
        password,
        cod_interno,
        ruc,
        razon_social,
        direccion_via,
        cod_distrito
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor()

            # El procedimiento actualiza razón social, dirección y distrito.
            self._ejecutar_procedimiento(
                cursor,
                "sp_actualizar_cliente",
                (
                    cod_interno,
                    razon_social,
                    direccion_via,
                    self._obtener_id_distrito(cod_distrito)
                )
            )

            # El procedimiento SQL entregado no contempla el RUC.
            # Se actualiza aquí para conservar la funcionalidad del formulario.
            cursor.execute("""
                UPDATE CLIENTE
                SET ruc = %s
                WHERE cod_interno = %s
                  AND estado = 'Activo'
            """, (ruc, cod_interno))

            filas = cursor.rowcount

            connection.commit()
            return filas

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
            cursor = connection.cursor()

            cursor.execute("""
                SELECT cod_interno
                FROM CLIENTE
                WHERE cod_interno = %s
                  AND estado = 'Activo'
            """, (cod_interno,))

            existe = cursor.fetchone()

            if not existe:
                connection.commit()
                return 0

            self._ejecutar_procedimiento(
                cursor,
                "sp_eliminar_cliente",
                (cod_interno,)
            )

            connection.commit()
            return 1

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    # =====================================================
    # CONTACTOS DEL CLIENTE
    # =====================================================

    def obtener_contactos(self, password, cod_interno):
        connection = self.database.connect(password)

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id_contacto,
                    cod_interno,
                    nombre_contacto,
                    telefono_contacto,
                    email_contacto
                FROM CONTACTO_CLIENTE
                WHERE cod_interno = %s
                  AND estado = 'Activo'
                ORDER BY nombre_contacto
            """, (cod_interno,))

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def insertar_contacto(
        self,
        password,
        cod_interno,
        nombre_contacto,
        telefono_contacto,
        email_contacto
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            connection.start_transaction()
            cursor = connection.cursor(dictionary=True)

            resultados = self._ejecutar_procedimiento(
                cursor,
                "sp_crear_contacto_cliente",
                (
                    cod_interno,
                    nombre_contacto,
                    telefono_contacto,
                    email_contacto
                )
            )

            if not resultados:
                raise RuntimeError(
                    "No se pudo recuperar el contacto registrado."
                )

            id_contacto = resultados[0].get("id_contacto")

            if id_contacto is None:
                raise RuntimeError(
                    "El procedimiento no devolvió el identificador del contacto."
                )

            connection.commit()
            return id_contacto

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def actualizar_contacto(
        self,
        password,
        cod_interno,
        nro_contacto,
        nombre_contacto,
        telefono_contacto,
        email_contacto
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE CONTACTO_CLIENTE
                SET
                    nombre_contacto = %s,
                    telefono_contacto = %s,
                    email_contacto = %s
                WHERE cod_interno = %s
                  AND id_contacto = %s
                  AND estado = 'Activo'
            """, (
                nombre_contacto,
                telefono_contacto,
                email_contacto,
                cod_interno,
                nro_contacto
            ))

            filas = cursor.rowcount
            connection.commit()

            return filas

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def eliminar_contacto(
        self,
        password,
        cod_interno,
        nro_contacto
    ):
        connection = self.database.connect(password)
        cursor = None

        try:
            cursor = connection.cursor()

            # El contacto se desactiva en lugar de borrarse físicamente.
            cursor.execute("""
                UPDATE CONTACTO_CLIENTE
                SET estado = 'Inactivo'
                WHERE cod_interno = %s
                  AND id_contacto = %s
                  AND estado = 'Activo'
            """, (cod_interno, nro_contacto))

            filas = cursor.rowcount
            connection.commit()

            return filas

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
