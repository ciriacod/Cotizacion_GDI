"""Calculos monetarios comunes para cotizaciones."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTAVO = Decimal("0.01")


def decimal_seguro(valor, campo="importe") -> Decimal:
    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, AttributeError, TypeError, ValueError) as error:
        raise ValueError(f"{campo}: ingresa un numero valido.") from error
    if not numero.is_finite():
        raise ValueError(f"{campo}: el valor debe ser finito.")
    return numero


def dinero(valor) -> Decimal:
    return decimal_seguro(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def calcular_subtotal(cantidad: int, precio_unitario) -> Decimal:
    if isinstance(cantidad, bool) or int(cantidad) != cantidad or int(cantidad) <= 0:
        raise ValueError("La cantidad debe ser un entero mayor que cero.")
    precio = dinero(precio_unitario)
    if precio < 0:
        raise ValueError("El precio unitario no puede ser negativo.")
    return dinero(Decimal(int(cantidad)) * precio)


def calcular_totales(detalles, impuesto: str, porcentaje_igv=18) -> dict:
    if not detalles:
        raise ValueError("Agrega al menos un detalle a la cotizacion.")

    subtotal = dinero(sum(
        (calcular_subtotal(linea["cantidad"], linea["precio_unitario"]) for linea in detalles),
        Decimal("0.00")
    ))
    tasa = decimal_seguro(porcentaje_igv, "Porcentaje IGV")
    if tasa < 0 or tasa > 100:
        raise ValueError("El porcentaje IGV debe estar entre 0 y 100.")

    if impuesto == "CON IGV":
        igv = dinero(subtotal * tasa / Decimal("100"))
    elif impuesto == "SIN IGV":
        igv = Decimal("0.00")
    else:
        raise ValueError("El regimen de impuesto debe ser SIN IGV o CON IGV.")

    return {
        "subtotal": subtotal,
        "porcentaje_igv": tasa,
        "igv": igv,
        "total": dinero(subtotal + igv),
    }
