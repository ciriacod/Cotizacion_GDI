"""Verificacion no destructiva de una instancia MySQL preparada.

Uso: python -m tests.integration.check_database
No inserta, modifica ni elimina registros.
"""

from getpass import getpass

from database.connection import DatabaseConnection

EXPECTED_TRIGGERS = {
    "trg_generar_cod_cliente",
    "trg_generar_cod_pro_ser",
    "trg_generar_nmr_cotizacion",
}
EXPECTED_PROCEDURES = {
    "sp_crear_cliente", "sp_actualizar_cliente", "sp_eliminar_cliente",
    "sp_crear_contacto_cliente", "sp_crear_empleado", "sp_listar_empleados_activos",
    "sp_actualizar_empleado", "sp_eliminar_empleado", "sp_crear_producto_servicio",
    "sp_eliminar_producto_servicio", "sp_crear_cotizacion", "sp_agregar_detalle_cotizacion",
    "sp_actualizar_cotizacion", "sp_eliminar_detalles_cotizacion", "sp_actualizar_estado_cotizacion",
}

EXPECTED_TABLES = {
    "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "CARGO", "ESPECIALIDAD", "EMPLEADO",
    "CLIENTE", "CONTACTO_CLIENTE", "UNIDAD_MEDIDA", "TIPO_PRODUCTO", "PRODUCTO_SERVICIO",
    "PRODUCTO", "SERVICIO", "TIPO_COTIZACION", "ORIGEN_SOLICITUD", "MONEDA",
    "FORMA_PAGO", "ESTADO_COTIZACION", "GARANTIA", "COTIZACION", "DETALLE_COTIZACION",
}


def main():
    password = getpass("Contrasena del usuario MySQL: ")
    database = DatabaseConnection()
    connection = database.connect(password)
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        actual = {row[0].upper() for row in cursor.fetchall()}
        missing = sorted(EXPECTED_TABLES - actual)
        if missing:
            raise RuntimeError("Faltan tablas: " + ", ".join(missing))
        cursor.execute(
            "SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s",
            (database.database_name,),
        )
        actual_triggers = {row[0] for row in cursor.fetchall()}
        cursor.execute(
            "SELECT ROUTINE_NAME FROM information_schema.ROUTINES "
            "WHERE ROUTINE_SCHEMA=%s AND ROUTINE_TYPE='PROCEDURE'",
            (database.database_name,),
        )
        actual_procedures = {row[0] for row in cursor.fetchall()}
        missing_triggers = sorted(EXPECTED_TRIGGERS - actual_triggers)
        missing_procedures = sorted(EXPECTED_PROCEDURES - actual_procedures)
        cursor.execute("SELECT COUNT(*) FROM TIPO_PRODUCTO WHERE nombre_tipo IN ('Equipo','Material','Servicio') AND estado='Activo'")
        types = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ESTADO_COTIZACION WHERE descripcion='Borrador' AND estado='Activo'")
        draft = cursor.fetchone()[0]
        cursor.execute(
            """SELECT COUNT(*) FROM PRODUCTO_SERVICIO ps
               INNER JOIN TIPO_PRODUCTO tp ON tp.id_tipo=ps.id_tipo
               LEFT JOIN PRODUCTO p ON p.cod_pro_ser=ps.cod_pro_ser
               LEFT JOIN SERVICIO s ON s.cod_pro_ser=ps.cod_pro_ser
               WHERE (LOWER(tp.nombre_tipo) IN ('equipo','material') AND (p.cod_pro_ser IS NULL OR s.cod_pro_ser IS NOT NULL))
                  OR (LOWER(tp.nombre_tipo)='servicio' AND (s.cod_pro_ser IS NULL OR p.cod_pro_ser IS NOT NULL))
                  OR LOWER(tp.nombre_tipo) NOT IN ('equipo','material','servicio')"""
        )
        invalid_subtypes = cursor.fetchone()[0]
        print("Conexion MySQL: OK")
        print(f"Tablas encontradas: {len(actual)} (se requieren {len(EXPECTED_TABLES)})")
        print(f"Triggers: {len(actual_triggers)}/{len(EXPECTED_TRIGGERS)}; "
              f"procedimientos: {len(actual_procedures)}/{len(EXPECTED_PROCEDURES)}")
        if missing_triggers:
            print("Triggers faltantes: " + ", ".join(missing_triggers))
        if missing_procedures:
            print("Procedimientos faltantes: " + ", ".join(missing_procedures))
        print(f"Tipos base activos: {types}/3; estado Borrador activo: {'si' if draft else 'no'}")
        print(f"Registros con subtipo Producto/Servicio inconsistente: {invalid_subtypes}")
        if invalid_subtypes:
            raise RuntimeError("Hay registros PRODUCTO_SERVICIO sin el subtipo correcto o con subtipos duplicados.")
        if types != 3 or draft != 1:
            raise RuntimeError("Faltan catalogos base. Ejecuta database/sql/03_catalogos_iniciales.sql.")
        if missing_triggers or missing_procedures:
            raise RuntimeError("Faltan triggers o procedimientos. Ejecuta database/sql/02_triggers_procedimientos.sql.")
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
