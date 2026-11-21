# JP Cotiza 1.1.0

Aplicación de escritorio para la gestión de cotizaciones comerciales de J.P. Ingeniería y Servicios S.R.L.

## Requisitos

- Windows 10/11 (la aplicación también conserva compatibilidad de desarrollo con Python en Linux).
- Servidor MySQL 8.0 o superior instalado y en ejecución.
- Para el primer inicio, una cuenta administradora de MySQL con permisos `CREATE`, `CREATE ROUTINE`, `TRIGGER`, `SELECT`, `INSERT`, `UPDATE`, `DELETE` y `EXECUTE` sobre la base que se instalará.
- Para el uso diario, puede utilizarse una cuenta de aplicación con permisos DML y `EXECUTE`.

> MySQL Server es necesario. JP Cotiza ya no requiere Docker y no utiliza SQLite para simular la base, porque el flujo depende de procedimientos almacenados y triggers propios de MySQL.

## Inicio

1. Instala e inicia MySQL Server 8.0+.
2. Ejecuta `JP_Cotiza.exe` (o `python main.py` en desarrollo).
3. En la pantalla inicial introduce host, puerto, base de datos, usuario y contraseña MySQL.
4. Pulsa **Conectar e inicializar JP Cotiza**.
5. Si la base no existe, el asistente la crea e instala las 21 tablas. Luego verifica/instala los procedimientos y triggers y ejecuta los catálogos iniciales idempotentes.
6. Registra al menos un cliente, un empleado responsable y productos/servicios antes de crear una cotización.

La contraseña no se guarda. Los parámetros de conexión se almacenan en `%APPDATA%\JP_Cotiza\database.ini` en Windows o `~/.config/jp_cotiza/database.ini` en Linux.

## Cotizaciones

El alta utiliza `sp_crear_cotizacion` y `sp_agregar_detalle_cotizacion`. El trigger `trg_generar_nmr_cotizacion` genera el número mensual. La actualización utiliza `sp_actualizar_cotizacion`, `sp_eliminar_detalles_cotizacion` y `sp_agregar_detalle_cotizacion`; los cambios de estado usan `sp_actualizar_estado_cotizacion`. Las operaciones de cabecera y detalle se ejecutan en una transacción.

## Reportes

La aplicación incluye los diez reportes definidos en `database/sql/04_consultas_negocio.sql`: periodo, estados, ranking de clientes, productos/servicios, próximas a vencer, pendientes, evolución mensual, desempeño por responsable, aprobadas por cliente y tipo de trabajo. Permite visualizar y exportar CSV.

## Ejecutable Windows

En Windows, abre la carpeta del proyecto y ejecuta `build_windows.bat`. El script crea un entorno de compilación, instala dependencias y genera `dist\JP_Cotiza.exe` mediante PyInstaller. El EXE se construye en Windows; no es posible generar un binario Windows válido desde un entorno Linux.

## Pruebas

```bash
python -m unittest discover -s tests/unit -v
python -m compileall -q .
python -m tests.integration.check_database
```

La última prueba requiere una base MySQL ya configurada. La verificación unitaria/estática no sustituye una prueba de integración real con MySQL.
