import unittest
from datetime import date

from services.cotizacion_service import CotizacionService


class CotizacionServiceTests(unittest.TestCase):
    def test_valida_encabezado_y_normaliza_fecha(self):
        header = CotizacionService.validar_encabezado({
            "fecha_emision": "2026-11-20",
            "id_tipo_cotizacion": "1", "id_origen": "2", "id_moneda": "1",
            "impuesto": "CON IGV", "porcentaje_igv": "18", "id_forma_pago": "1",
            "id_garantia": "3", "tiempo_ejecucion": "5 dias", "tiempo_entrega": "7 dias",
            "vigencia_dias": "15", "exclusiones": "No aplica", "observaciones": "",
            "cod_interno_cliente": "CLI001", "id_contacto": "", "id_empleado": "1",
        })
        self.assertEqual(header["fecha_emision"], date(2026, 11, 20))
        self.assertEqual(header["id_contacto"], None)
        self.assertEqual(header["vigencia_dias"], 15)

    def test_rechaza_vigencia_cero(self):
        payload = {
            "fecha_emision": "2026-11-20", "id_tipo_cotizacion": 1, "id_origen": 1,
            "id_moneda": 1, "impuesto": "SIN IGV", "porcentaje_igv": 18,
            "id_forma_pago": 1, "id_garantia": 1, "tiempo_ejecucion": "5 dias",
            "vigencia_dias": 0, "cod_interno_cliente": "CLI001", "id_empleado": 1,
        }
        with self.assertRaisesRegex(ValueError, "mayor que cero"):
            CotizacionService.validar_encabezado(payload)

    def test_rechaza_impuesto_desconocido(self):
        payload = {
            "fecha_emision": "2026-11-20", "id_tipo_cotizacion": 1, "id_origen": 1,
            "id_moneda": 1, "impuesto": "EXONERADO", "porcentaje_igv": 18,
            "id_forma_pago": 1, "id_garantia": 1, "tiempo_ejecucion": "5 dias",
            "vigencia_dias": 15, "cod_interno_cliente": "CLI001", "id_empleado": 1,
        }
        with self.assertRaisesRegex(ValueError, "SIN IGV o CON IGV"):
            CotizacionService.validar_encabezado(payload)

    def test_rechaza_detalle_sin_producto(self):
        with self.assertRaisesRegex(ValueError, "producto o servicio"):
            CotizacionService.validar_detalles([{"cantidad": 1, "precio_unitario": 10}])

    def test_valida_detalle(self):
        rows = CotizacionService.validar_detalles([{
            "cod_pro_ser": "EQU08601", "cantidad": "2", "precio_unitario": "125.50",
            "alcance_tecnico": "Instalacion y puesta en marcha",
        }])
        self.assertEqual(rows[0]["cantidad"], 2)
        self.assertEqual(str(rows[0]["precio_unitario"]), "125.50")


    def test_rechaza_cantidad_fraccionaria(self):
        with self.assertRaisesRegex(ValueError, "debe ser entera"):
            CotizacionService.validar_detalles([{
                "cod_pro_ser": "EQU08601", "cantidad": "1.5", "precio_unitario": "10.00"
            }])

    def test_rechaza_cantidad_fuera_de_rango_int(self):
        with self.assertRaisesRegex(ValueError, "2147483647"):
            CotizacionService.validar_detalles([{
                "cod_pro_ser": "EQU08601", "cantidad": "2147483648", "precio_unitario": "10.00"
            }])

    def test_redondea_precio_a_dos_decimales(self):
        rows = CotizacionService.validar_detalles([{
            "cod_pro_ser": "EQU08601", "cantidad": "1", "precio_unitario": "10.125"
        }])
        self.assertEqual(str(rows[0]["precio_unitario"]), "10.13")

    def test_rechaza_precio_superior_a_decimal_10_2(self):
        with self.assertRaisesRegex(ValueError, r"DECIMAL\(10,2\)"):
            CotizacionService.validar_detalles([{
                "cod_pro_ser": "EQU08601", "cantidad": "1", "precio_unitario": "100000000.00"
            }])

if __name__ == "__main__":
    unittest.main()
