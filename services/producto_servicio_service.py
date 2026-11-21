
from decimal import Decimal, InvalidOperation
import re

from repositories.producto_servicio_repository import (
    ProductoServicioRepository
)


class ProductoServicioService:
    """Reglas de negocio de productos, servicios y catálogos."""

    def __init__(self, database):
        self.repository = ProductoServicioRepository(database)

    # =================================================
    # VALIDACIONES GENERALES
    # =================================================

    @staticmethod
    def _texto(valor, etiqueta, maximo, obligatorio=True):
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

    @staticmethod
    def _id(valor, etiqueta):
        try:
            identificador = int(valor)

        except (TypeError, ValueError):
            raise ValueError(
                f"Selecciona {etiqueta} válido."
            )

        if identificador <= 0:
            raise ValueError(
                f"Selecciona {etiqueta} válido."
            )

        return identificador

    # =================================================
    # VALIDAR PRECIO
    # =================================================

    @staticmethod
    def _precio(valor):
        try:
            precio = Decimal(
                str(valor).strip().replace(",", ".")
            )

        except (InvalidOperation, AttributeError):
            raise ValueError(
                "Ingresa un precio numérico válido."
            )

        if not precio.is_finite():
            raise ValueError(
                "El precio debe ser un número finito."
            )

        if precio < 0:
            raise ValueError(
                "El precio referencial no puede ser negativo."
            )

        if precio > Decimal("99999999.99"):
            raise ValueError(
                "El precio supera el máximo permitido."
            )

        if precio.as_tuple().exponent < -2:
            raise ValueError(
                "El precio admite como máximo dos decimales."
            )

        return precio.quantize(Decimal("0.01"))

    # =================================================
    # VALIDAR AÑO
    # =================================================

    @staticmethod
    def _anio(valor):
        texto = (valor or "").strip()

        if not texto:
            return None

        if not re.fullmatch(r"\d{4}", texto):
            raise ValueError(
                "El año debe tener cuatro dígitos o quedar vacío."
            )

        anio = int(texto)

        if not 1901 <= anio <= 2155:
            raise ValueError(
                "El año debe estar entre 1901 y 2155."
            )

        return anio

    # =================================================
    # CONSULTAS
    # =================================================

    def listar_catalogo(self, password):
        return self.repository.obtener_catalogo(password)

    def buscar_item(self, password, codigo):
        codigo = self._texto(codigo, "código", 8)

        return self.repository.obtener_por_codigo(
            password,
            codigo
        )

    def listar_unidades(self, password):
        return self.repository.obtener_unidades(password)

    def listar_tipos(self, password):
        return self.repository.obtener_tipos(password)

    # =================================================
    # VALIDAR DATOS DE PRODUCTO / SERVICIO
    # =================================================

    def _validar_item(
        self,
        password,
        descripcion,
        id_unidad,
        id_tipo,
        precio,
        marca=None,
        modelo=None,
        anio=None,
        nmr_parte=None
    ):
        descripcion = self._texto(
            descripcion,
            "descripción",
            350
        )

        id_unidad = self._id(
            id_unidad,
            "una unidad de medida"
        )

        id_tipo = self._id(
            id_tipo,
            "un tipo de producto"
        )

        precio = self._precio(precio)
        tipo_nombre = self.repository.obtener_nombre_tipo(password, id_tipo)
        tipo_normalizado = (tipo_nombre or "").strip().casefold()

        if tipo_normalizado in {"equipo", "material"}:

            marca = self._texto(
                marca,
                "marca",
                50
            )

            modelo = self._texto(
                modelo,
                "modelo",
                50
            )

            nmr_parte = self._texto(
                nmr_parte,
                "número de parte",
                50
            )

            anio = self._anio(anio)

        elif tipo_normalizado == "servicio":
            marca = None
            modelo = None
            anio = None
            nmr_parte = None

        else:
            raise ValueError(
                "El tipo seleccionado no es compatible con el generador "
                "de códigos actual. Usa Equipo, Material o Servicio."
            )

        return (
            descripcion,
            id_unidad,
            id_tipo,
            precio,
            marca,
            modelo,
            anio,
            nmr_parte
        )

    # =================================================
    # REGISTRAR PRODUCTO / SERVICIO
    # =================================================

    def registrar_item(
        self,
        password,
        descripcion,
        id_unidad,
        id_tipo,
        precio,
        marca=None,
        modelo=None,
        anio=None,
        nmr_parte=None
    ):
        datos = self._validar_item(
            password,
            descripcion,
            id_unidad,
            id_tipo,
            precio,
            marca,
            modelo,
            anio,
            nmr_parte
        )

        return self.repository.insertar_item(
            password,
            *datos
        )

    # =================================================
    # MODIFICAR PRODUCTO / SERVICIO
    # =================================================

    def modificar_item(
        self,
        password,
        codigo,
        descripcion,
        id_unidad,
        id_tipo,
        precio,
        marca=None,
        modelo=None,
        anio=None,
        nmr_parte=None
    ):
        codigo = self._texto(
            codigo,
            "código",
            8
        )

        datos = self._validar_item(
            password,
            descripcion,
            id_unidad,
            id_tipo,
            precio,
            marca,
            modelo,
            anio,
            nmr_parte
        )

        return self.repository.actualizar_item(
            password,
            codigo,
            *datos
        )

    # =================================================
    # DESACTIVAR PRODUCTO / SERVICIO
    # =================================================

    def desactivar_item(self, password, codigo):
        codigo = self._texto(
            codigo,
            "código",
            8
        )

        return self.repository.desactivar_item(
            password,
            codigo
        )

    # =================================================
    # UNIDADES DE MEDIDA
    # =================================================

    def registrar_unidad(self, password, nombre, abreviatura):
        nombre = self._texto(
            nombre,
            "nombre de unidad",
            50
        )

        abreviatura = self._texto(
            abreviatura,
            "abreviatura",
            5
        )

        return self.repository.insertar_unidad(
            password,
            nombre,
            abreviatura
        )

    def modificar_unidad(
        self,
        password,
        id_unidad,
        nombre,
        abreviatura
    ):
        id_unidad = self._id(
            id_unidad,
            "unidad de medida"
        )

        nombre = self._texto(
            nombre,
            "nombre de unidad",
            50
        )

        abreviatura = self._texto(
            abreviatura,
            "abreviatura",
            5
        )

        return self.repository.actualizar_unidad(
            password,
            id_unidad,
            nombre,
            abreviatura
        )

    def desactivar_unidad(self, password, id_unidad):
        id_unidad = self._id(
            id_unidad,
            "unidad de medida"
        )

        return self.repository.desactivar_unidad(
            password,
            id_unidad
        )

    # =================================================
    # TIPOS DE PRODUCTO
    # =================================================

    def modificar_tipo(
        self,
        password,
        id_tipo,
        nombre,
        descripcion
    ):
        id_tipo = self._id(
            id_tipo,
            "tipo de producto"
        )

        actual = self.repository.obtener_nombre_tipo(password, id_tipo)
        if (actual or "").strip().casefold() not in {"equipo", "material", "servicio"}:
            raise ValueError("Solo se pueden editar los tipos Equipo, Material o Servicio.")

        nombre = self._texto(
            nombre,
            "nombre del tipo",
            50
        )
        if nombre.casefold() != actual.casefold():
            raise ValueError("No se puede cambiar el nombre de Equipo, Material o Servicio porque define la clasificación y el código del catálogo.")

        descripcion = self._texto(
            descripcion,
            "descripción",
            150,
            obligatorio=False
        )

        return self.repository.actualizar_tipo(
            password,
            id_tipo,
            nombre,
            descripcion
        )
