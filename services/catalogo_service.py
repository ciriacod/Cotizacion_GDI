
from repositories.catalogo_repository import CatalogoRepository


class CatalogoService:
    """Reglas de validación para cargos y especialidades."""

    def __init__(self, database):
        self.repository = CatalogoRepository(database)

    # =================================================
    # VALIDACIONES GENERALES
    # =================================================

    @staticmethod
    def _validar_id(valor, etiqueta):
        try:
            identificador = int(valor)

        except (TypeError, ValueError):
            raise ValueError(
                f"Selecciona un {etiqueta} válido."
            )

        if identificador <= 0:
            raise ValueError(
                f"Selecciona un {etiqueta} válido."
            )

        return identificador

    @staticmethod
    def _texto(
        valor,
        etiqueta,
        maximo,
        obligatorio=True
    ):
        texto = (valor or "").strip()

        if obligatorio and not texto:
            raise ValueError(
                f"El campo {etiqueta} es obligatorio."
            )

        if len(texto) > maximo:
            raise ValueError(
                f"El campo {etiqueta} no puede superar "
                f"{maximo} caracteres."
            )

        return texto or None

    # =================================================
    # CONSULTAS
    # =================================================

    def listar_cargos(self, password):
        return self.repository.obtener_cargos(password)

    def listar_especialidades(self, password):
        return self.repository.obtener_especialidades(password)

    # =================================================
    # REGISTRAR CARGO
    # =================================================

    def registrar_cargo(
        self,
        password,
        nombre,
        descripcion
    ):
        nombre = self._texto(
            nombre,
            "nombre del cargo",
            30
        )

        descripcion = self._texto(
            descripcion,
            "descripción",
            350,
            obligatorio=False
        )

        return self.repository.insertar_cargo(
            password,
            nombre,
            descripcion
        )

    # =================================================
    # MODIFICAR CARGO
    # =================================================

    def modificar_cargo(
        self,
        password,
        id_cargo,
        nombre,
        descripcion
    ):
        id_cargo = self._validar_id(
            id_cargo,
            "cargo"
        )

        nombre = self._texto(
            nombre,
            "nombre del cargo",
            30
        )

        descripcion = self._texto(
            descripcion,
            "descripción",
            350,
            obligatorio=False
        )

        return self.repository.actualizar_cargo(
            password,
            id_cargo,
            nombre,
            descripcion
        )

    # =================================================
    # DESACTIVAR CARGO
    # =================================================

    def desactivar_cargo(self, password, id_cargo):
        id_cargo = self._validar_id(
            id_cargo,
            "cargo"
        )

        return self.repository.desactivar_cargo(
            password,
            id_cargo
        )

    # =================================================
    # REGISTRAR ESPECIALIDAD
    # =================================================

    def registrar_especialidad(
        self,
        password,
        nombre,
        descripcion,
        area,
        certificacion
    ):
        datos = self._validar_especialidad(
            nombre,
            descripcion,
            area,
            certificacion
        )

        return self.repository.insertar_especialidad(
            password,
            *datos
        )

    # =================================================
    # MODIFICAR ESPECIALIDAD
    # =================================================

    def modificar_especialidad(
        self,
        password,
        id_especialidad,
        nombre,
        descripcion,
        area,
        certificacion
    ):
        id_especialidad = self._validar_id(
            id_especialidad,
            "especialidad"
        )

        datos = self._validar_especialidad(
            nombre,
            descripcion,
            area,
            certificacion
        )

        return self.repository.actualizar_especialidad(
            password,
            id_especialidad,
            *datos
        )

    # =================================================
    # DESACTIVAR ESPECIALIDAD
    # =================================================

    def desactivar_especialidad(
        self,
        password,
        id_especialidad
    ):
        id_especialidad = self._validar_id(
            id_especialidad,
            "especialidad"
        )

        return self.repository.desactivar_especialidad(
            password,
            id_especialidad
        )

    # =================================================
    # VALIDAR ESPECIALIDAD
    # =================================================

    @classmethod
    def _validar_especialidad(
        cls,
        nombre,
        descripcion,
        area,
        certificacion
    ):
        return (
            cls._texto(
                nombre,
                "nombre de la especialidad",
                40
            ),

            cls._texto(
                descripcion,
                "descripción",
                350,
                obligatorio=False
            ),

            cls._texto(
                area,
                "área de conocimiento",
                40
            ),

            cls._texto(
                certificacion,
                "certificación requerida",
                40,
                obligatorio=False
            )
        )
