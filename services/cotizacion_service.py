"""Casos de uso y reglas de negocio para la gestion de cotizaciones."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from repositories.cotizacion_repository import CotizacionRepository
from services.calculadora import calcular_totales, decimal_seguro, dinero


class CotizacionService:
    ESTADOS_VALIDOS = {
        "Borrador", "En revisión", "En revision", "Enviada",
        "En negociación", "En negociacion", "Aprobada", "Rechazada", "Vencida"
    }

    def __init__(self, database):
        self.repository = CotizacionRepository(database)

    def obtener_opciones(self, password):
        return self.repository.obtener_opciones(password)

    def obtener_contactos(self, password, cod_interno):
        return self.repository.obtener_contactos(password, cod_interno)

    @staticmethod
    def _validar_texto(valor, campo, maximo, obligatorio=True):
        texto = "" if valor is None else str(valor).strip()
        if obligatorio and not texto:
            raise ValueError(f"El campo {campo} es obligatorio.")
        if len(texto) > maximo:
            raise ValueError(f"El campo {campo} no puede superar {maximo} caracteres.")
        return texto or None

    @staticmethod
    def _validar_id(valor, campo, obligatorio=True):
        if valor in (None, ""):
            if obligatorio:
                raise ValueError(f"Selecciona {campo}.")
            return None
        try:
            numero = int(valor)
        except (TypeError, ValueError) as error:
            raise ValueError(f"El valor seleccionado para {campo} no es valido.") from error
        if numero <= 0:
            raise ValueError(f"El valor seleccionado para {campo} no es valido.")
        return numero

    @classmethod
    def validar_encabezado(cls, datos):
        try:
            fecha = datos.get("fecha_emision")
            fecha = fecha if isinstance(fecha, date) else date.fromisoformat(str(fecha).strip())
        except (TypeError, ValueError) as error:
            raise ValueError("La fecha de emision debe tener el formato AAAA-MM-DD.") from error

        impuesto = str(datos.get("impuesto", "")).strip().upper()
        if impuesto not in {"SIN IGV", "CON IGV"}:
            raise ValueError("El impuesto debe ser SIN IGV o CON IGV.")

        tasa = decimal_seguro(datos.get("porcentaje_igv", 18), "Porcentaje IGV")
        if tasa < 0 or tasa > 100:
            raise ValueError("El porcentaje IGV debe estar entre 0 y 100.")

        try:
            vigencia = int(datos.get("vigencia_dias"))
        except (TypeError, ValueError) as error:
            raise ValueError("La vigencia debe ser un numero entero de dias.") from error
        if vigencia <= 0:
            raise ValueError("La vigencia debe ser mayor que cero.")

        return {
            "fecha_emision": fecha,
            "id_tipo_cotizacion": cls._validar_id(datos.get("id_tipo_cotizacion"), "el tipo de cotizacion"),
            "id_origen": cls._validar_id(datos.get("id_origen"), "el origen de solicitud"),
            "id_moneda": cls._validar_id(datos.get("id_moneda"), "la moneda"),
            "impuesto": impuesto,
            "porcentaje_igv": tasa,
            "id_forma_pago": cls._validar_id(datos.get("id_forma_pago"), "la forma de pago"),
            "id_garantia": cls._validar_id(datos.get("id_garantia"), "la garantia"),
            "tiempo_ejecucion": cls._validar_texto(datos.get("tiempo_ejecucion"), "tiempo de ejecucion", 30),
            "tiempo_entrega": cls._validar_texto(datos.get("tiempo_entrega"), "tiempo de entrega", 30, False),
            "vigencia_dias": vigencia,
            "exclusiones": cls._validar_texto(datos.get("exclusiones"), "exclusiones", 250, False),
            "observaciones": cls._validar_texto(datos.get("observaciones"), "observaciones", 250, False),
            "cod_interno_cliente": cls._validar_texto(datos.get("cod_interno_cliente"), "cliente", 10),
            "id_contacto": cls._validar_id(datos.get("id_contacto"), "el contacto", False),
            "id_empleado": cls._validar_id(datos.get("id_empleado"), "el responsable"),
        }

    @staticmethod
    def validar_detalles(detalles):
        if not detalles:
            raise ValueError("La cotizacion debe contener al menos un producto o servicio.")
        normalizados = []
        for indice, linea in enumerate(detalles, start=1):
            codigo = str(linea.get("cod_pro_ser", "")).strip()
            if not codigo:
                raise ValueError(f"Selecciona el producto o servicio del item {indice}.")
            valor_cantidad = linea.get("cantidad")
            if isinstance(valor_cantidad, bool):
                raise ValueError(f"La cantidad del item {indice} debe ser entera.")
            try:
                cantidad_decimal = decimal_seguro(valor_cantidad, f"Cantidad del item {indice}")
            except ValueError as error:
                raise ValueError(f"La cantidad del item {indice} debe ser entera.") from error
            if cantidad_decimal != cantidad_decimal.to_integral_value():
                raise ValueError(f"La cantidad del item {indice} debe ser entera.")
            cantidad = int(cantidad_decimal)
            if cantidad <= 0 or cantidad > 2147483647:
                raise ValueError(f"La cantidad del item {indice} debe estar entre 1 y 2147483647.")
            precio = dinero(decimal_seguro(linea.get("precio_unitario"), f"Precio del item {indice}"))
            if precio < 0:
                raise ValueError(f"El precio del item {indice} no puede ser negativo.")
            if precio > Decimal("99999999.99"):
                raise ValueError(f"El precio del item {indice} supera el maximo admitido por DECIMAL(10,2).")
            alcance = str(linea.get("alcance_tecnico") or "").strip() or None
            if alcance and len(alcance) > 300:
                raise ValueError(f"El alcance tecnico del item {indice} supera 300 caracteres.")
            normalizados.append({
                "cod_pro_ser": codigo,
                "cantidad": cantidad,
                "precio_unitario": precio,
                "alcance_tecnico": alcance,
            })
        return normalizados

    def calcular(self, detalles, impuesto, porcentaje_igv):
        return calcular_totales(detalles, impuesto, porcentaje_igv)

    def crear(self, password, encabezado, detalles):
        datos = self.validar_encabezado(encabezado)
        lineas = self.validar_detalles(detalles)
        self.calcular(lineas, datos["impuesto"], datos["porcentaje_igv"])
        return self.repository.crear_con_detalles(password, datos, lineas)

    def actualizar(self, password, numero, encabezado, detalles):
        datos = self.validar_encabezado(encabezado)
        lineas = self.validar_detalles(detalles)
        self.calcular(lineas, datos["impuesto"], datos["porcentaje_igv"])
        return self.repository.actualizar_con_detalles(password, numero, datos, lineas)

    def listar(self, password, filtro=""):
        return self.repository.listar(password, filtro)

    def obtener(self, password, numero):
        return self.repository.obtener(password, numero)

    def listar_estados(self, password):
        return self.repository.listar_estados(password)

    def actualizar_estado(self, password, numero, id_estado):
        if not numero:
            raise ValueError("Selecciona una cotizacion.")
        return self.repository.actualizar_estado(password, numero, self._validar_id(id_estado, "el estado"))

    def resumen_dashboard(self, password):
        return self.repository.obtener_resumen_dashboard(password)

    def recientes(self, password, limite=8):
        return self.repository.listar_recientes(password, limite)
