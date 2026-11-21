-- Plantilla opcional para crear un usuario MySQL de aplicacion con privilegios limitados.
-- Sustituye la contrasena de ejemplo antes de ejecutar. No guardes la contrasena en el proyecto.
-- Ejecutar como administrador de MySQL despues de crear esquema, rutinas y catalogos.

CREATE USER IF NOT EXISTS 'jp_app'@'127.0.0.1' IDENTIFIED BY 'CAMBIAR_POR_UNA_CONTRASENA_LARGA_Y_UNICA';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON cotizacion.* TO 'jp_app'@'127.0.0.1';
FLUSH PRIVILEGES;

-- La aplicacion usa host 127.0.0.1 por defecto. Ajusta el host de esta cuenta si usas otro
-- nombre/IP en config/database.ini. Para conexion desde otra PC, crea una cuenta
-- restringida a la IP o red exacta que corresponda.
-- Evita usar '%' si no es necesario y nunca expongas MySQL directamente a Internet.
