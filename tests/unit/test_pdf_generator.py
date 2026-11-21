import tempfile
import unittest
from pathlib import Path
from datetime import date
from decimal import Decimal

from utils.pdf_generator import generar_cotizacion_pdf


class PdfGeneratorTests(unittest.TestCase):
    def test_generates_pdf_with_quote_data(self):
        data = {
            "encabezado": {
                "nmr_cotizacion": "JP.261100001", "fecha_emision": date(2026, 11, 20),
                "estado_descripcion": "Borrador", "razon_social": "Cliente de prueba S.A.C.",
                "ruc": "20123456789", "direccion_via": "Av. Prueba 100",
                "nombre_distrito": "Arequipa", "nombre_provincia": "Arequipa",
                "nombre_departamento": "Arequipa", "responsable": "Noelia Gonzales",
                "tipo_cotizacion": "Suministro", "origen_solicitud": "Solicitud directa",
                "moneda_nombre": "Soles", "moneda_simbolo": "S/.", "codigo_iso": "PEN",
                "impuesto": "CON IGV", "porcentaje_igv": Decimal("18.00"),
                "forma_pago": "Al contado", "tiempo_ejecucion": "5 dias", "tiempo_entrega": "7 dias",
                "vigencia_dias": 15, "tiempo_garantia": 12, "unidad_garantia": "meses",
                "exclusiones": "No aplica", "observaciones": "Sin observaciones",
            },
            "detalles": [{
                "item": 1, "cod_pro_ser": "EQU08601", "descripcion": "Compresor Scroll",
                "unidad": "UND", "cantidad": 2, "precio_unitario": Decimal("100.00"),
                "alcance_tecnico": "Suministro",
            }],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "cotizacion.pdf"
            created = generar_cotizacion_pdf(data, destination)
            self.assertTrue(created.exists())
            self.assertGreater(created.stat().st_size, 1000)
            self.assertEqual(created.read_bytes()[:4], b"%PDF")


if __name__ == "__main__":
    unittest.main()
