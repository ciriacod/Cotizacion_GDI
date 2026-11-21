"""Inicialización no destructiva del esquema MySQL de JP Cotiza."""
from __future__ import annotations
import re
from database.connection import resource_path

EXPECTED_TABLES = {
    "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "CARGO", "ESPECIALIDAD", "EMPLEADO",
    "CLIENTE", "CONTACTO_CLIENTE", "UNIDAD_MEDIDA", "TIPO_PRODUCTO", "PRODUCTO_SERVICIO",
    "PRODUCTO", "SERVICIO", "TIPO_COTIZACION", "ORIGEN_SOLICITUD", "MONEDA", "FORMA_PAGO",
    "ESTADO_COTIZACION", "GARANTIA", "COTIZACION", "DETALLE_COTIZACION"
}


def split_mysql_script(script: str):
    """Divide scripts MySQL respetando DELIMITER y delimitadores dentro de cadenas."""
    delimiter = ";"
    buffer, statements = [], []
    for line in script.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("DELIMITER "):
            delimiter = stripped.split(None, 1)[1]
            continue
        buffer.append(line)
        joined = "\n".join(buffer).rstrip()
        if joined.endswith(delimiter):
            statement = joined[:-len(delimiter)].strip()
            if statement:
                statements.append(statement)
            buffer = []
    tail = "\n".join(buffer).strip()
    if tail:
        statements.append(tail)
    return statements


class DatabaseInstaller:
    def __init__(self, database):
        self.database = database
        self.sql_dir = resource_path("database", "sql")

    @staticmethod
    def _run_script(cursor, path):
        script = path.read_text(encoding="utf-8-sig")
        for statement in split_mysql_script(script):
            normalized = re.sub(r"(?m)^\s*--.*$", "", statement).strip()
            if re.match(r"^(USE|CREATE\s+DATABASE)\b", normalized, re.IGNORECASE):
                continue
            cursor.execute(statement)
            if cursor.with_rows:
                cursor.fetchall()
            while cursor.nextset():
                if cursor.with_rows:
                    cursor.fetchall()

    def initialize(self, password):
        server = self.database.connect_server(password)
        created = False
        try:
            cur = server.cursor()
            cur.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s", (self.database.database_name,))
            schema_exists = cur.fetchone() is not None
            if not schema_exists:
                db_name = self.database.database_name.replace("`", "``")
                cur.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cur.execute("SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'", (self.database.database_name,))
            existing = {row[0].upper() for row in cur.fetchall()}
            if not existing:
                cur.close(); server.close()
                target = self.database.connect(password)
                try:
                    cursor = target.cursor()
                    self._run_script(cursor, self.sql_dir / "01_esquema.sql")
                    target.commit()
                    cursor.close()
                except Exception:
                    target.rollback(); raise
                finally:
                    target.close()
                created = True
                server = self.database.connect_server(password)
                cur = server.cursor()
                cur.execute("SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'", (self.database.database_name,))
                existing = {row[0].upper() for row in cur.fetchall()}
            missing = EXPECTED_TABLES - existing
            if missing:
                raise RuntimeError("La base de datos existe pero está incompleta. Faltan tablas: " + ", ".join(sorted(missing)) + ". No se borró ni modificó información; restaura una copia o usa una BD vacía.")
            cur.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=%s AND ROUTINE_TYPE='PROCEDURE'", (self.database.database_name,))
            procedures = {row[0] for row in cur.fetchall()}
            cur.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s", (self.database.database_name,))
            triggers = {row[0] for row in cur.fetchall()}
            required_procedures = {
                "sp_crear_cliente", "sp_actualizar_cliente", "sp_eliminar_cliente",
                "sp_crear_contacto_cliente", "sp_crear_empleado", "sp_listar_empleados_activos",
                "sp_actualizar_empleado", "sp_eliminar_empleado", "sp_crear_producto_servicio",
                "sp_eliminar_producto_servicio", "sp_crear_cotizacion", "sp_agregar_detalle_cotizacion",
                "sp_actualizar_cotizacion", "sp_eliminar_detalles_cotizacion", "sp_actualizar_estado_cotizacion",
            }
            required_triggers = {"trg_generar_cod_cliente", "trg_generar_cod_pro_ser", "trg_generar_nmr_cotizacion"}
            routines_missing = bool(required_procedures - procedures or required_triggers - triggers)
            cur.close(); server.close()

            target = self.database.connect(password)
            try:
                cursor = target.cursor()
                if routines_missing:
                    self._run_script(cursor, self.sql_dir / "02_triggers_procedimientos.sql")
                # El script de catálogos es idempotente (INSERT IGNORE / NOT EXISTS).
                self._run_script(cursor, self.sql_dir / "03_catalogos_iniciales.sql")
                target.commit()
                cursor.close()
            except Exception:
                target.rollback(); raise
            finally:
                target.close()

            verify = self.database.connect(password)
            try:
                cursor = verify.cursor()
                cursor.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=%s AND ROUTINE_TYPE='PROCEDURE'", (self.database.database_name,))
                procedures = {row[0] for row in cursor.fetchall()}
                cursor.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s", (self.database.database_name,))
                triggers = {row[0] for row in cursor.fetchall()}
                if required_procedures - procedures:
                    raise RuntimeError("No se instalaron todos los procedimientos: " + ", ".join(sorted(required_procedures - procedures)))
                if required_triggers - triggers:
                    raise RuntimeError("No se instalaron todos los triggers: " + ", ".join(sorted(required_triggers - triggers)))
                cursor.close()
            finally:
                verify.close()
            return {"database": self.database.database_name, "tables": len(existing), "created": created,
                    "procedures_refreshed": routines_missing, "seeded": True}
        finally:
            try: server.close()
            except Exception: pass
