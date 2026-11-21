import unittest
from decimal import Decimal

from services.calculadora import calcular_subtotal, calcular_totales


class CalculadoraTests(unittest.TestCase):
    def test_subtotal_cantidad_por_precio(self):
        self.assertEqual(calcular_subtotal(3, "12.50"), Decimal("37.50"))

    def test_total_con_igv(self):
        result = calcular_totales(
            [{"cantidad": 2, "precio_unitario": Decimal("50.00")}],
            "CON IGV", "18",
        )
        self.assertEqual(result["subtotal"], Decimal("100.00"))
        self.assertEqual(result["igv"], Decimal("18.00"))
        self.assertEqual(result["total"], Decimal("118.00"))

    def test_total_sin_igv(self):
        result = calcular_totales(
            [{"cantidad": 2, "precio_unitario": "50.00"}], "SIN IGV", 18,
        )
        self.assertEqual(result["igv"], Decimal("0.00"))
        self.assertEqual(result["total"], Decimal("100.00"))

    def test_cantidad_cero_es_rechazada(self):
        with self.assertRaises(ValueError):
            calcular_subtotal(0, "10.00")

    def test_precio_negativo_es_rechazado(self):
        with self.assertRaises(ValueError):
            calcular_subtotal(1, "-0.01")

    def test_no_acepta_cotizacion_sin_detalles(self):
        with self.assertRaises(ValueError):
            calcular_totales([], "SIN IGV", 18)


if __name__ == "__main__":
    unittest.main()
