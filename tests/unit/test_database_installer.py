from pathlib import Path
import unittest
from database.installer import split_mysql_script, EXPECTED_TABLES, DatabaseInstaller
from repositories.reporte_repository import ReporteRepository

ROOT = Path(__file__).resolve().parents[2]

class DatabaseInstallerTests(unittest.TestCase):
    def test_splitter_respects_delimiter_and_procedures(self):
        sql = """-- comment\nDELIMITER //\nCREATE PROCEDURE demo()\nBEGIN\n SELECT 1;\n SELECT 2;\nEND //\nDELIMITER ;\nCREATE TABLE t(id INT);\n"""
        statements = split_mysql_script(sql)
        self.assertEqual(len(statements), 2)
        self.assertIn("SELECT 1;", statements[0])
        self.assertIn("SELECT 2;", statements[0])
        self.assertIn("CREATE TABLE t", statements[1])

    def test_new_schema_is_non_destructive_and_has_21_tables(self):
        sql = (ROOT / "database" / "sql" / "01_esquema.sql").read_text(encoding="utf-8")
        self.assertNotIn("DROP DATABASE", sql.upper())
        import re
        tables = set(re.findall(r"CREATE TABLE\s+(\w+)", sql, re.I))
        self.assertEqual(tables, EXPECTED_TABLES)


    def test_schema_importer_skips_database_switch_and_keeps_all_tables(self):
        class FakeCursor:
            def __init__(self): self.statements=[]; self.with_rows=False
            def execute(self, sql): self.statements.append(sql)
            def nextset(self): return None
            def fetchall(self): return []
        cursor=FakeCursor()
        DatabaseInstaller._run_script(cursor, ROOT / "database" / "sql" / "01_esquema.sql")
        self.assertEqual(len(cursor.statements), 21)
        self.assertTrue(all(not x.lstrip().upper().startswith(("USE ", "CREATE DATABASE")) for x in cursor.statements))

    def test_ten_reports_use_current_schema_and_not_legacy_columns(self):
        self.assertEqual(len(ReporteRepository.REPORTES), 10)
        sql = (ROOT / "database" / "sql" / "04_consultas_negocio.sql").read_text(encoding="utf-8")
        for legacy in ("cod_estado", "cod_moneda", "cod_tipo", "vigencia_oferta", "DNI_empleado"):
            self.assertNotIn(legacy.lower(), sql.lower())
        self.assertIn("id_estado", sql)
        self.assertIn("id_moneda", sql)

    def test_procedures_include_quote_crud_and_triggers(self):
        sql = (ROOT / "database" / "sql" / "02_triggers_procedimientos.sql").read_text(encoding="utf-8")
        for name in ("trg_generar_nmr_cotizacion", "sp_crear_cotizacion", "sp_agregar_detalle_cotizacion",
                     "sp_actualizar_cotizacion", "sp_eliminar_detalles_cotizacion", "sp_actualizar_estado_cotizacion"):
            self.assertIn(name, sql)

if __name__ == "__main__":
    unittest.main()
