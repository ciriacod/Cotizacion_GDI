"""Generacion del documento comercial PDF sin alterar la base de datos."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from services.calculadora import calcular_totales


def _fmt(value):
    return f"{Decimal(str(value or 0)):.2f}"


def _paragraph(value, style):
    text = "-" if value in (None, "") else escape(str(value)).replace("\n", "<br/>")
    return Paragraph(text, style)


def generar_cotizacion_pdf(datos: dict, destino: str | Path) -> Path:
    encabezado = datos["encabezado"]
    detalles = datos["detalles"]
    totales = calcular_totales(detalles, encabezado["impuesto"], encabezado["porcentaje_igv"])
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(destino), pagesize=A4,
        rightMargin=17 * mm, leftMargin=17 * mm,
        topMargin=15 * mm, bottomMargin=17 * mm,
        title=f"Cotizacion {encabezado['nmr_cotizacion']}",
        author="J.P. Ingenieria y Servicios S.R.L.",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="JPTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17, leading=20, textColor=colors.HexColor("#17365D"), alignment=TA_CENTER, spaceAfter=5))
    styles.add(ParagraphStyle(name="JPSub", parent=styles["Normal"], fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.HexColor("#526477")))
    styles.add(ParagraphStyle(name="JPHead", parent=styles["Heading2"], fontSize=9, leading=11, textColor=colors.HexColor("#17365D"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="JPBody", parent=styles["BodyText"], fontSize=8, leading=11))
    styles.add(ParagraphStyle(name="JPSmall", parent=styles["BodyText"], fontSize=7, leading=9))
    styles.add(ParagraphStyle(name="JPRight", parent=styles["BodyText"], fontSize=8, leading=10, alignment=TA_RIGHT))

    story = [
        Paragraph("JP INGENIERIA Y SERVICIOS S.R.L.", styles["JPTitle"]),
        Paragraph("Ingenieria, suministro, instalacion y mantenimiento de sistemas HVAC", styles["JPSub"]),
        Spacer(1, 4 * mm),
    ]
    summary = [
        [Paragraph("COTIZACION COMERCIAL", styles["Heading2"]), Paragraph(f"<b>{escape(str(encabezado['nmr_cotizacion']))}</b>", styles["JPRight"])],
        [Paragraph("Fecha de emision", styles["JPSmall"]), Paragraph(str(encabezado["fecha_emision"]), styles["JPRight"])],
        [Paragraph("Estado", styles["JPSmall"]), Paragraph(escape(str(encabezado.get("estado_descripcion", "Borrador"))), styles["JPRight"])],
    ]
    table = Table(summary, colWidths=[95 * mm, 80 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF1F8")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B8C7D8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D6DEE8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    direccion = ", ".join(filter(None, [encabezado.get("direccion_via"), encabezado.get("nombre_distrito"), encabezado.get("nombre_provincia"), encabezado.get("nombre_departamento")]))
    info_cliente = [
        [Paragraph("<b>CLIENTE</b>", styles["JPBody"]), Paragraph(escape(str(encabezado.get("razon_social", ""))), styles["JPBody"])],
        [Paragraph("RUC", styles["JPSmall"]), Paragraph(escape(str(encabezado.get("ruc", ""))), styles["JPBody"])],
        [Paragraph("Direccion", styles["JPSmall"]), Paragraph(escape(direccion), styles["JPBody"])],
        [Paragraph("Contacto", styles["JPSmall"]), Paragraph(escape(str(encabezado.get("nombre_contacto") or "No especificado")), styles["JPBody"])],
        [Paragraph("Telefono / correo", styles["JPSmall"]), Paragraph(escape(" / ".join(filter(None, [encabezado.get("telefono_contacto"), encabezado.get("email_contacto")])) or "-"), styles["JPBody"])],
        [Paragraph("Responsable", styles["JPSmall"]), Paragraph(escape(str(encabezado.get("responsable", ""))), styles["JPBody"])],
    ]
    client_table = Table(info_cliente, colWidths=[35 * mm, 140 * mm])
    client_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F6FA")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [Paragraph("INFORMACION DEL CLIENTE", styles["JPHead"]), client_table]

    story.append(Paragraph("DETALLE DE LA OFERTA", styles["JPHead"]))
    item_data = [["Item", "Codigo", "Descripcion", "Unidad", "Cant.", "P. unitario", "Subtotal"]]
    for i, linea in enumerate(detalles, start=1):
        subtotal = Decimal(str(linea["cantidad"])) * Decimal(str(linea["precio_unitario"]))
        item_data.append([
            str(linea.get("item", i)), str(linea.get("cod_pro_ser", "")),
            _paragraph(linea.get("descripcion", ""), styles["JPSmall"]),
            str(linea.get("unidad", "")), str(linea["cantidad"]),
            _fmt(linea["precio_unitario"]), _fmt(subtotal),
        ])
    item_table = Table(item_data, colWidths=[10 * mm, 20 * mm, 69 * mm, 16 * mm, 13 * mm, 22 * mm, 25 * mm], repeatRows=1)
    item_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
        ("ALIGN", (0, 0), (1, -1), "CENTER"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(item_table)

    moneda = encabezado.get("codigo_iso") or encabezado.get("moneda_nombre") or ""
    totals_data = [
        ["Subtotal", f"{moneda} {_fmt(totales['subtotal'])}"],
        [f"IGV ({_fmt(totales['porcentaje_igv'])}%)" if encabezado["impuesto"] == "CON IGV" else "IGV (No aplicado)", f"{moneda} {_fmt(totales['igv'])}"],
        ["TOTAL", f"{moneda} {_fmt(totales['total'])}"],
    ]
    totals_table = Table(totals_data, colWidths=[45 * mm, 45 * mm], hAlign="RIGHT")
    totals_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"), ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#EAF1F8")),
        ("LINEABOVE", (0, 2), (-1, 2), 0.8, colors.HexColor("#17365D")),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [Spacer(1, 3 * mm), totals_table, Paragraph("CONDICIONES COMERCIALES", styles["JPHead"])]

    conditions = [
        ("Tipo", encabezado.get("tipo_cotizacion")), ("Origen", encabezado.get("origen_solicitud")),
        ("Moneda", f"{encabezado.get('moneda_nombre', '')} ({moneda})"),
        ("Impuesto", encabezado.get("impuesto")), ("Forma de pago", encabezado.get("forma_pago")),
        ("Tiempo de ejecucion", encabezado.get("tiempo_ejecucion")),
        ("Tiempo de entrega", encabezado.get("tiempo_entrega")),
        ("Vigencia", f"{encabezado.get('vigencia_dias')} dias"),
        ("Garantia", f"{encabezado.get('tiempo_garantia')} {encabezado.get('unidad_garantia')}"),
        ("Exclusiones", encabezado.get("exclusiones") or "No aplica"),
        ("Observaciones", encabezado.get("observaciones") or "Sin observaciones"),
    ]
    condition_data = [[Paragraph(f"<b>{escape(str(k))}</b>", styles["JPSmall"]), _paragraph(v, styles["JPBody"])] for k, v in conditions if v not in (None, "")]
    cond_table = Table(condition_data, colWidths=[38 * mm, 137 * mm])
    cond_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F6FA")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [cond_table, Spacer(1, 8 * mm), Paragraph("Documento generado por el Sistema de Gestion de Cotizaciones JP.", styles["JPSub"])]

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D7E0EA"))
        canvas.line(17 * mm, 12 * mm, A4[0] - 17 * mm, 12 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#718096"))
        canvas.drawString(17 * mm, 8 * mm, "J.P. Ingenieria y Servicios S.R.L. - Cotizacion comercial")
        canvas.drawRightString(A4[0] - 17 * mm, 8 * mm, f"Pagina {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return destino
