"""Inicialización no destructiva del esquema MySQL de COTIZEP."""
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
            cur.execute("SELECT VERSION()")
            version_row = cur.fetchone()
            server_version = str(version_row[0]) if version_row else "0.0.0"
            version_text = server_version.split("-", 1)[0]
            if "mariadb" in server_version.lower():
                raise RuntimeError("COTIZEP requiere MySQL Server 8.0.16+; MariaDB no está validado para esta instalación.")
            try:
                version_parts = tuple(int(part) for part in version_text.split(".")[:3])
            except ValueError:
                version_parts = (0, 0, 0)
            if version_parts < (8, 0, 16):
                raise RuntimeError(
                    f"COTIZEP requiere MySQL 8.0.16 o superior para aplicar restricciones CHECK. "
                    f"Versión detectada: {version_text}."
                )
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
            # Determina los objetos requeridos directamente desde los scripts versionados.
            sql_core = (self.sql_dir / "02_triggers_procedimientos.sql").read_text(encoding="utf-8-sig")
            sql_reports = (self.sql_dir / "04_procedimientos_reportes.sql").read_text(encoding="utf-8-sig")
            required_core = set(re.findall(r"CREATE\s+PROCEDURE\s+(\w+)", sql_core, re.IGNORECASE))
            required_reports = set(re.findall(r"CREATE\s+PROCEDURE\s+(\w+)", sql_reports, re.IGNORECASE))
            required_triggers = set(re.findall(r"CREATE\s+TRIGGER\s+(\w+)", sql_core, re.IGNORECASE))

            cur.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=%s AND ROUTINE_TYPE='PROCEDURE'", (self.database.database_name,))
            procedures = {row[0] for row in cur.fetchall()}
            cur.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s", (self.database.database_name,))
            triggers = {row[0] for row in cur.fetchall()}
            cur.execute(
                """SELECT cc.CHECK_CLAUSE
                   FROM information_schema.CHECK_CONSTRAINTS cc
                   INNER JOIN information_schema.TABLE_CONSTRAINTS tc
                     ON tc.CONSTRAINT_SCHEMA = cc.CONSTRAINT_SCHEMA
                    AND tc.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
                   WHERE tc.CONSTRAINT_SCHEMA = %s
                     AND tc.TABLE_NAME = 'COTIZACION'
                     AND tc.CONSTRAINT_NAME = 'ck_cotizacion_impuesto'""",
                (self.database.database_name,),
            )
            tax_constraint = cur.fetchone()
            tax_migration_needed = bool(
                tax_constraint and "EXONERADO" not in str(tax_constraint[0]).upper()
            )
            core_missing = bool((required_core - procedures) or (required_triggers - triggers))
            reports_missing = bool(required_reports - procedures)
            cur.close()
            server.close()

            target = self.database.connect(password)
            try:
                cursor = target.cursor()
                if tax_migration_needed:
                    self._run_script(cursor, self.sql_dir / "05_migracion_regimen_tributario.sql")
                if core_missing:
                    self._run_script(cursor, self.sql_dir / "02_triggers_procedimientos.sql")
                if reports_missing:
                    self._run_script(cursor, self.sql_dir / "04_procedimientos_reportes.sql")
                # El catálogo inicial utiliza INSERT IGNORE / NOT EXISTS y puede
                # ejecutarse de forma segura en cada inicialización.
                self._run_script(cursor, self.sql_dir / "03_catalogos_iniciales.sql")
                target.commit()
                cursor.close()
            except Exception:
                target.rollback()
                raise
            finally:
                target.close()

            verify = self.database.connect(password)
            try:
                cursor = verify.cursor()
                cursor.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=%s AND ROUTINE_TYPE='PROCEDURE'", (self.database.database_name,))
                procedures = {row[0] for row in cursor.fetchall()}
                cursor.execute("SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s", (self.database.database_name,))
                triggers = {row[0] for row in cursor.fetchall()}
                missing_procedures = (required_core | required_reports) - procedures
                if missing_procedures:
                    raise RuntimeError("No se instalaron todos los procedimientos: " + ", ".join(sorted(missing_procedures)))
                if required_triggers - triggers:
                    raise RuntimeError("No se instalaron todos los triggers: " + ", ".join(sorted(required_triggers - triggers)))
                cursor.close()
            finally:
                verify.close()
            return {"database": self.database.database_name, "tables": len(existing), "created": created,
                    "procedures_refreshed": core_missing or reports_missing,
                    "tax_migrated": tax_migration_needed, "seeded": True}
        finally:
            try: server.close()
            except Exception: pass
