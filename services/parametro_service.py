
from repositories.parametro_repository import ParametroRepository


class ParametroService:
    """Reglas de negocio para los parámetros del sistema."""

    DEFINICIONES = {
        "tipo_cotizacion": {
            "campos": ("descripcion",),
            "longitudes": {"descripcion": 150},
        },
        "origen_solicitud": {
            "campos": ("descripcion",),
            "longitudes": {"descripcion": 150},
        },
        "moneda": {
            "campos": ("nombre", "simbolo", "codigo_iso"),
            "longitudes": {
                "nombre": 30,
                "simbolo": 5,
                "codigo_iso": 3,
            },
        },
        "forma_pago": {
            "campos": ("descripcion", "dias_credito"),
            "longitudes": {"descripcion": 100},
        },
        "estado_cotizacion": {
            "campos": ("descripcion",),
            "longitudes": {"descripcion": 50},
        },
        "garantia": {
            "campos": ("tiempo_garantia", "unidad_garantia"),
            "longitudes": {"unidad_garantia": 20},
        },
    }

    def __init__(self, database):
        self.repository = ParametroRepository(database)

    @staticmethod
    def _validar_texto(valor, campo, maximo):
        texto = str(valor or "").strip()

        if not texto:
            raise ValueError(f"El campo {campo} es obligatorio.")

        if len(texto) > maximo:
            raise ValueError(
                f"El campo {campo} no puede superar {maximo} caracteres."
            )

        return texto

    @staticmethod
    def _validar_entero(valor, campo, minimo=0):
        try:
            numero = int(str(valor).strip())
        except (TypeError, ValueError, AttributeError):
            raise ValueError(f"El campo {campo} debe ser un número entero.")

        if numero < minimo:
            raise ValueError(
                f"El campo {campo} debe ser como mínimo {minimo}."
            )

        return numero

    @staticmethod
    def _validar_id(identificador):
        try:
            valor = int(identificador)
        except (TypeError, ValueError):
            raise ValueError("Selecciona un parámetro válido.")

        if valor <= 0:
            raise ValueError("Selecciona un parámetro válido.")

        return valor

    def listar(self, password, catalogo):
        if catalogo not in self.DEFINICIONES:
            raise ValueError("El catálogo seleccionado no es válido.")

        return self.repository.listar(password, catalogo)

    def _validar_datos(self, catalogo, datos):
        if catalogo not in self.DEFINICIONES:
            raise ValueError("El catálogo seleccionado no es válido.")

        definicion = self.DEFINICIONES[catalogo]
        campos = definicion["campos"]

        if set(datos.keys()) != set(campos):
            raise ValueError("Los datos no corresponden al catálogo.")

        resultado = {}

        if catalogo in ("tipo_cotizacion", "origen_solicitud"):
            resultado["descripcion"] = self._validar_texto(
                datos["descripcion"],
                "descripción",
                definicion["longitudes"]["descripcion"]
            )

        elif catalogo == "moneda":
            resultado["nombre"] = self._validar_texto(
                datos["nombre"],
                "nombre",
                30
            )
            resultado["simbolo"] = self._validar_texto(
                datos["simbolo"],
                "símbolo",
                5
            )
            resultado["codigo_iso"] = self._validar_texto(
                datos["codigo_iso"],
                "código ISO",
                3
            ).upper()

            if len(resultado["codigo_iso"]) != 3:
                raise ValueError("El código ISO debe tener exactamente 3 caracteres.")

        elif catalogo == "forma_pago":
            resultado["descripcion"] = self._validar_texto(
                datos["descripcion"],
                "descripción",
                100
            )
            resultado["dias_credito"] = self._validar_entero(
                datos["dias_credito"],
                "días de crédito",
                0
            )

        elif catalogo == "estado_cotizacion":
            resultado["descripcion"] = self._validar_texto(
                datos["descripcion"],
                "descripción",
                50
            )

        elif catalogo == "garantia":
            resultado["tiempo_garantia"] = self._validar_entero(
                datos["tiempo_garantia"],
                "tiempo de garantía",
                1
            )
            resultado["unidad_garantia"] = self._validar_texto(
                datos["unidad_garantia"],
                "unidad de garantía",
                20
            ).lower()

        return resultado

    def registrar(self, password, catalogo, datos):
        datos_validados = self._validar_datos(catalogo, datos)

        return self.repository.insertar(
            password,
            catalogo,
            datos_validados
        )

    def modificar(self, password, catalogo, identificador, datos):
        identificador = self._validar_id(identificador)
        datos_validados = self._validar_datos(catalogo, datos)

        return self.repository.actualizar(
            password,
            catalogo,
            identificador,
            datos_validados
        )

    def desactivar(self, password, catalogo, identificador):
        identificador = self._validar_id(identificador)

        return self.repository.desactivar(
            password,
            catalogo,
            identificador
        )
