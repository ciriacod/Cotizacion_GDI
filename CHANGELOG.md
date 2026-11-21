# CHANGELOG - JP Cotiza

## 1.1.0 - 2026-11-20

- Se incorpora un asistente inicial de conexión a MySQL.
- La aplicación crea la base configurada si no existe e importa el esquema no destructivo de 21 tablas.
- Se verifica la existencia de procedimientos y triggers requeridos; se instalan cuando faltan.
- Los catálogos iniciales se ejecutan de forma idempotente.
- La contraseña MySQL se mantiene en memoria y no se escribe en archivos de configuración.
- Se agregan procedimientos para actualizar cabecera, reemplazar partidas y cambiar el estado de cotizaciones.
- El alta, edición, detalle y cambio de estado de cotizaciones usan procedimientos almacenados; los triggers generan códigos y número mensual.
- Se corrige el mapeo de identificadores al cargar una cotización para edición.
- Se corrige un conflicto de layout Tkinter (`grid`/`pack`) que impedía mostrar el formulario de cotizaciones.
- Se alinea la documentación SQL de los diez reportes con los nombres reales del esquema actualizado.
- Se agrega construcción de ejecutable Windows con PyInstaller (`build_windows.bat`).
- Se actualiza la identidad de ventana a JP Cotiza.
- Se mantiene la inicialización no destructiva: no se elimina ni trunca una base existente.

## Validación

- Pruebas unitarias: 31 aprobadas; ver `tests/unit`.
- Compilación estática: `python -m compileall -q .`.
- La integración contra un servidor MySQL real debe ejecutarse en el entorno de instalación.
