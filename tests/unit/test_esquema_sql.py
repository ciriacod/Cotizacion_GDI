import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class EsquemaSqlTests(unittest.TestCase):
    def test_esquema_define_21_tablas(self):
        sql = (ROOT / "database/sql/01_esquema.sql").read_text(encoding="utf-8")
        self.assertEqual(sql.upper().count("CREATE TABLE "), 21)

    def test_script_de_esquema_no_elimina_la_base(self):
        sql = (ROOT / "database/sql/01_esquema.sql").read_text(encoding="utf-8").upper()
        self.assertNotIn("DROP DATABASE", sql)

    def test_script_de_catalogos_no_contiene_operaciones_destructivas(self):
        sql = (ROOT / "database/sql/03_catalogos_iniciales.sql").read_text(encoding="utf-8").upper()
        self.assertNotIn("TRUNCATE TABLE", sql)
        self.assertNotIn("DELETE FROM", sql)
        self.assertIn("INSERT IGNORE", sql)

    def test_no_quedan_referencias_a_login_de_empleados(self):
        sql = (ROOT / "database/sql/02_triggers_procedimientos.sql").read_text(encoding="utf-8").lower()
        self.assertNotIn("sp_obtener_empleado_login", sql)
        self.assertNotIn("sp_actualizar_password_empleado", sql)

    def test_demo_explicito_y_protegido(self):
        sql = (ROOT / "database/sql/opcional/05_datos_demo_REINICIA_TODO.sql").read_text(encoding="utf-8").upper()
        self.assertIn("JP_CONFIRMAR_REINICIO_DEMO", sql)
        self.assertIn("TRUNCATE TABLE", sql)
        self.assertIn("NO", sql)
        self.assertIn("CREATE PROCEDURE SP_EJECUTAR_CARGA_DEMO", sql)
        self.assertIn("IF COALESCE(@JP_CONFIRMAR_REINICIO_DEMO, 'NO') <> 'SI' THEN", sql)
        self.assertLess(sql.index("ELSE"), sql.index("TRUNCATE TABLE"))
        self.assertGreater(sql.index("END IF;"), sql.index("TRUNCATE TABLE"))


    def test_trigger_numera_cotizaciones_por_mes(self):
        sql = (ROOT / "database/sql/02_triggers_procedimientos.sql").read_text(encoding="utf-8")
        self.assertIn("WHERE nmr_cotizacion LIKE CONCAT(v_prefijo, '%')", sql)

    def test_catalogo_garantia_es_idempotente_sin_requerir_unique(self):
        sql = (ROOT / "database/sql/03_catalogos_iniciales.sql").read_text(encoding="utf-8").upper()
        self.assertIn("INSERT INTO GARANTIA", sql)
        self.assertIn("WHERE NOT EXISTS", sql)

if __name__ == "__main__":
    unittest.main()
