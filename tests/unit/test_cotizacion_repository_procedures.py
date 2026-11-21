import unittest
from repositories.cotizacion_repository import CotizacionRepository

class FakeCursor:
    def __init__(self):
        self.with_rows=False; self.rows=[]; self.calls=[]; self.closed=False
    def execute(self, sql, params=()):
        self.calls.append((sql, params)); self.with_rows=False; self.rows=[]
        if "CALL sp_crear_cotizacion" in sql:
            self.with_rows=True; self.rows=[{"nmr_cotizacion":"JP.261100001"}]
        elif "CALL sp_actualizar_cotizacion" in sql:
            self.with_rows=True; self.rows=[{"nmr_cotizacion":"JP.261100001"}]
        elif "SELECT nmr_cotizacion FROM COTIZACION" in sql:
            self.with_rows=True; self.rows=[{"nmr_cotizacion":"JP.261100001"}]
    def fetchall(self): return self.rows
    def fetchone(self): return self.rows[0] if self.rows else None
    def nextset(self): return None
    def close(self): self.closed=True

class FakeConnection:
    def __init__(self): self.c=FakeCursor(); self.commits=0; self.rollbacks=0; self.closed=False
    def cursor(self, dictionary=False): return self.c
    def start_transaction(self): pass
    def commit(self): self.commits+=1
    def rollback(self): self.rollbacks+=1
    def close(self): self.closed=True

class FakeDatabase:
    def __init__(self): self.connection=FakeConnection()
    def connect(self,password): return self.connection

class CotizacionRepositoryProcedureTests(unittest.TestCase):
    def setUp(self):
        self.db=FakeDatabase(); self.repo=CotizacionRepository(self.db)
        self.header={"fecha_emision":"2026-11-20", "id_tipo_cotizacion":1,"id_origen":1,"id_moneda":1,
          "impuesto":"SIN IGV","porcentaje_igv":18,"id_forma_pago":1,"id_garantia":1,
          "tiempo_ejecucion":"5 dias","tiempo_entrega":None,"vigencia_dias":15,"exclusiones":None,
          "observaciones":None,"cod_interno_cliente":"CLI001","id_contacto":None,"id_empleado":1}
        self.details=[{"cod_pro_ser":"SER0001","cantidad":1,"precio_unitario":100,"alcance_tecnico":None}]

    def test_create_uses_stored_procedures_and_commits_transaction(self):
        number=self.repo.crear_con_detalles("pw",self.header,self.details)
        self.assertEqual(number,"JP.261100001")
        calls=[sql for sql,_ in self.db.connection.c.calls]
        self.assertTrue(any("CALL sp_crear_cotizacion" in x for x in calls))
        self.assertTrue(any("CALL sp_agregar_detalle_cotizacion" in x for x in calls))
        self.assertEqual(self.db.connection.commits,1)
        self.assertEqual(self.db.connection.rollbacks,0)

    def test_update_uses_stored_procedures_for_header_and_details(self):
        self.repo.actualizar_con_detalles("pw", "JP.261100001", self.header, self.details)
        calls=[sql for sql,_ in self.db.connection.c.calls]
        self.assertTrue(any("CALL sp_actualizar_cotizacion" in x for x in calls))
        self.assertTrue(any("CALL sp_eliminar_detalles_cotizacion" in x for x in calls))
        self.assertTrue(any("CALL sp_agregar_detalle_cotizacion" in x for x in calls))
        self.assertEqual(self.db.connection.commits,1)

    def test_state_change_uses_stored_procedure(self):
        self.repo.actualizar_estado("pw","JP.261100001",2)
        calls=[sql for sql,_ in self.db.connection.c.calls]
        self.assertTrue(any("CALL sp_actualizar_estado_cotizacion" in x for x in calls))
        self.assertEqual(self.db.connection.commits,1)

if __name__ == '__main__': unittest.main()
