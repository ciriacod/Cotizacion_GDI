
import re

from repositories.cliente_repository import ClienteRepository


class ClienteService:

    def __init__(self, database):
        self.repository = ClienteRepository(database)

    # =====================================================
    # VALIDACIONES
    # =====================================================

    def validar_cliente(
        self,
        ruc,
        razon_social,
        direccion_via,
        cod_distrito
    ):
        ruc = str(ruc).strip()
        razon_social = str(razon_social).strip()
        direccion_via = str(direccion_via).strip()

        if not ruc:
            raise ValueError("El RUC es obligatorio.")

        if not ruc.isdigit() or len(ruc) != 11:
            raise ValueError(
                "El RUC debe contener exactamente 11 dígitos."
            )

        if not razon_social:
            raise ValueError(
                "La razón social es obligatoria."
            )

        if len(razon_social) > 150:
            raise ValueError(
                "La razón social no puede superar 150 caracteres."
            )

        if not direccion_via:
            raise ValueError(
                "La dirección es obligatoria."
            )

        if len(direccion_via) > 200:
            raise ValueError(
                "La dirección no puede superar 200 caracteres."
            )

        if cod_distrito is None or str(cod_distrito).strip() == "":
            raise ValueError(
                "Debes seleccionar un distrito."
            )

        try:
            cod_distrito = int(cod_distrito)
        except (TypeError, ValueError):
            raise ValueError(
                "El distrito seleccionado no es válido."
            )

        return (
            ruc,
            razon_social,
            direccion_via,
            cod_distrito
        )

    def validar_contacto(
        self,
        nombre_contacto,
        telefono_contacto,
        email_contacto
    ):
        nombre_contacto = str(nombre_contacto).strip()
        telefono_contacto = str(telefono_contacto or "").strip()
        email_contacto = str(email_contacto or "").strip()

        if not nombre_contacto:
            raise ValueError(
                "El nombre del contacto es obligatorio."
            )

        if len(nombre_contacto) > 100:
            raise ValueError(
                "El nombre del contacto supera los 100 caracteres."
            )

        if len(telefono_contacto) > 15:
            raise ValueError(
                "El teléfono no puede superar 15 caracteres."
            )

        if len(email_contacto) > 100:
            raise ValueError(
                "El correo no puede superar 100 caracteres."
            )

        if email_contacto:
            patron_email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

            if not re.match(patron_email, email_contacto):
                raise ValueError(
                    "El formato del correo electrónico no es válido."
                )

        return (
            nombre_contacto,
            telefono_contacto or None,
            email_contacto or None
        )

    # =====================================================
    # OPERACIONES DE CLIENTES
    # =====================================================

    def listar_clientes(self, password):
        return self.repository.obtener_todos(password)

    def listar_distritos(self, password):
        return self.repository.obtener_distritos(password)

    def buscar_cliente(self, password, cod_interno):
        if not cod_interno:
            raise ValueError(
                "Debes indicar el código del cliente."
            )

        return self.repository.obtener_por_codigo(
            password,
            cod_interno
        )

    def registrar_cliente(
        self,
        password,
        ruc,
        razon_social,
        direccion_via,
        cod_distrito
    ):
        datos = self.validar_cliente(
            ruc,
            razon_social,
            direccion_via,
            cod_distrito
        )

        return self.repository.insertar(
            password,
            *datos
        )

    def modificar_cliente(
        self,
        password,
        cod_interno,
        ruc,
        razon_social,
        direccion_via,
        cod_distrito
    ):
        if not cod_interno:
            raise ValueError(
                "Debes seleccionar un cliente."
            )

        datos = self.validar_cliente(
            ruc,
            razon_social,
            direccion_via,
            cod_distrito
        )

        return self.repository.actualizar(
            password,
            cod_interno,
            *datos
        )

    def eliminar_cliente(self, password, cod_interno):
        if not cod_interno:
            raise ValueError(
                "Debes seleccionar un cliente."
            )

        return self.repository.eliminar(
            password,
            cod_interno
        )

    # =====================================================
    # OPERACIONES DE CONTACTOS
    # =====================================================

    def listar_contactos(self, password, cod_interno):
        if not cod_interno:
            raise ValueError(
                "Debes seleccionar un cliente."
            )

        return self.repository.obtener_contactos(
            password,
            cod_interno
        )

    def registrar_contacto(
        self,
        password,
        cod_interno,
        nombre_contacto,
        telefono_contacto,
        email_contacto
    ):
        if not cod_interno:
            raise ValueError(
                "Debes seleccionar un cliente."
            )

        datos = self.validar_contacto(
            nombre_contacto,
            telefono_contacto,
            email_contacto
        )

        return self.repository.insertar_contacto(
            password,
            cod_interno,
            *datos
        )

    def modificar_contacto(
        self,
        password,
        cod_interno,
        id_contacto,
        nombre_contacto,
        telefono_contacto,
        email_contacto
    ):
        if not cod_interno or not id_contacto:
            raise ValueError(
                "Debes seleccionar un contacto."
            )

        datos = self.validar_contacto(
            nombre_contacto,
            telefono_contacto,
            email_contacto
        )

        return self.repository.actualizar_contacto(
            password,
            cod_interno,
            id_contacto,
            *datos
        )

    def eliminar_contacto(
        self,
        password,
        cod_interno,
        id_contacto
    ):
        if not cod_interno or not id_contacto:
            raise ValueError(
                "Debes seleccionar un contacto."
            )

        return self.repository.eliminar_contacto(
            password,
            cod_interno,
            id_contacto
        )
