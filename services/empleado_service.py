
import base64
import hashlib
import os
import re
import secrets

from repositories.empleado_repository import EmpleadoRepository


class EmpleadoService:
    """Validaciones y reglas de negocio de empleados."""

    ITERACIONES_HASH = 310000

    def __init__(self, database):
        self.repository = EmpleadoRepository(database)

    # -------------------------------------------------
    # HASH TECNICO REQUERIDO POR EL ESQUEMA
    # -------------------------------------------------

    @classmethod
    def generar_hash_tecnico(cls):
        """Genera un hash no utilizable como cuenta de acceso del aplicativo.

        EMPLEADO.password_hash es NOT NULL en el esquema fisico, pero el
        analisis funcional excluye cuentas de usuario. Por eso se almacena
        un secreto aleatorio desconocido y no recuperable.
        """
        secreto = secrets.token_urlsafe(48)
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", secreto.encode("utf-8"), salt, cls.ITERACIONES_HASH
        )
        salt_text = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
        digest_text = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        return f"pbkdf2_sha256${cls.ITERACIONES_HASH}${salt_text}${digest_text}"

    # -------------------------------------------------
    # CONSULTAS
    # -------------------------------------------------

    def listar_empleados(self, password):
        return self.repository.obtener_todos(password)

    def buscar_empleado(self, password, id_empleado):
        return self.repository.obtener_por_id(
            password,
            self._validar_id(id_empleado, "empleado")
        )

    def listar_cargos(self, password):
        return self.repository.obtener_cargos(password)

    def listar_especialidades(self, password):
        return self.repository.obtener_especialidades(password)

    # -------------------------------------------------
    # VALIDACIONES GENERALES
    # -------------------------------------------------

    @staticmethod
    def _validar_id(valor, etiqueta):
        try:
            numero = int(valor)

        except (TypeError, ValueError):
            raise ValueError(
                f"Selecciona un {etiqueta} válido."
            )

        if numero <= 0:
            raise ValueError(
                f"Selecciona un {etiqueta} válido."
            )

        return numero

    @staticmethod
    def _validar_datos(
        dni,
        nombre,
        email,
        telefono,
        id_cargo,
        id_especialidad
    ):
        dni = (dni or "").strip()
        nombre = (nombre or "").strip()
        email = (email or "").strip().lower()
        telefono = (telefono or "").strip() or None

        if not re.fullmatch(r"\d{8}", dni):
            raise ValueError(
                "El DNI debe contener exactamente 8 dígitos."
            )

        if not nombre:
            raise ValueError(
                "El nombre completo es obligatorio."
            )

        if len(nombre) > 200:
            raise ValueError(
                "El nombre no puede superar 200 caracteres."
            )

        if (
            len(email) > 350
            or not re.fullmatch(
                r"[^\s@]+@[^\s@]+\.[^\s@]+",
                email
            )
        ):
            raise ValueError(
                "Ingresa un correo electrónico válido."
            )

        if telefono and len(telefono) > 15:
            raise ValueError(
                "El teléfono no puede superar 15 caracteres."
            )

        return (
            dni,
            nombre,
            email,
            telefono,
            EmpleadoService._validar_id(
                id_cargo,
                "cargo"
            ),
            EmpleadoService._validar_id(
                id_especialidad,
                "especialidad"
            )
        )

    # -------------------------------------------------
    # REGISTRAR
    # -------------------------------------------------

    def registrar_empleado(
        self,
        password_db,
        dni,
        nombre,
        email,
        telefono,
        id_cargo,
        id_especialidad
    ):
        datos = self._validar_datos(
            dni,
            nombre,
            email,
            telefono,
            id_cargo,
            id_especialidad
        )

        password_hash = self.generar_hash_tecnico()

        return self.repository.insertar(
            password_db,
            *datos[:3],
            password_hash,
            *datos[3:]
        )

    # -------------------------------------------------
    # MODIFICAR
    # -------------------------------------------------

    def modificar_empleado(
        self,
        password_db,
        id_empleado,
        dni,
        nombre,
        email,
        telefono,
        id_cargo,
        id_especialidad
    ):
        id_empleado = self._validar_id(
            id_empleado,
            "empleado"
        )

        datos = self._validar_datos(
            dni,
            nombre,
            email,
            telefono,
            id_cargo,
            id_especialidad
        )

        return self.repository.actualizar(
            password_db,
            id_empleado,
            *datos
        )

    # -------------------------------------------------
    # DESACTIVAR
    # -------------------------------------------------

    def eliminar_empleado(self, password_db, id_empleado):
        return self.repository.eliminar(
            password_db,
            self._validar_id(id_empleado, "empleado")
        )
