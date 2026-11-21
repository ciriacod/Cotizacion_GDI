-- =============================================================================
-- 2. SCRIPT DE PROGRAMACIÓN EN EL SGBD: TRIGGERS Y PROCEDIMIENTOS ALMACENADOS
-- Empresa: J.P. Ingeniería y Servicios S.R.L.
-- Módulo: Gestión de Cotizaciones Comerciales (HVAC)
-- Gestor: MySQL 8.0+
-- =============================================================================

USE cotizacion;

DELIMITER //

-- =============================================================================
-- SECCIÓN 1: DISPARADORES (TRIGGERS) PARA GENERACIÓN AUTOMÁTICA DE CÓDIGOS
-- =============================================================================

DROP TRIGGER IF EXISTS trg_generar_cod_cliente //
CREATE TRIGGER trg_generar_cod_cliente
BEFORE INSERT ON CLIENTE
FOR EACH ROW
BEGIN
    DECLARE v_ultimo_num INT DEFAULT 0;
    IF NEW.cod_interno IS NULL OR TRIM(NEW.cod_interno) = '' THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(cod_interno, 4) AS UNSIGNED)), 0)
        INTO v_ultimo_num
        FROM CLIENTE
        WHERE cod_interno LIKE 'CLI%';
        
        SET NEW.cod_interno = CONCAT('CLI', LPAD(v_ultimo_num + 1, 3, '0'));
    END IF;
    SET @ultimo_cod_cliente = NEW.cod_interno;
END //

DROP TRIGGER IF EXISTS trg_generar_cod_pro_ser //
CREATE TRIGGER trg_generar_cod_pro_ser
BEFORE INSERT ON PRODUCTO_SERVICIO
FOR EACH ROW
BEGIN
    DECLARE v_ultimo_num INT DEFAULT 0;
    IF NEW.cod_pro_ser IS NULL OR TRIM(NEW.cod_pro_ser) = '' THEN
        IF NEW.id_tipo = 1 THEN
            SELECT COALESCE(MAX(CAST(SUBSTRING(cod_pro_ser, 4) AS UNSIGNED)), 8600)
            INTO v_ultimo_num FROM PRODUCTO_SERVICIO WHERE cod_pro_ser LIKE 'EQU%';
            SET NEW.cod_pro_ser = CONCAT('EQU', LPAD(v_ultimo_num + 1, 5, '0'));
        ELSEIF NEW.id_tipo = 2 THEN
            SELECT COALESCE(MAX(CAST(SUBSTRING(cod_pro_ser, 4) AS UNSIGNED)), 1900)
            INTO v_ultimo_num FROM PRODUCTO_SERVICIO WHERE cod_pro_ser LIKE 'MAT%';
            SET NEW.cod_pro_ser = CONCAT('MAT', LPAD(v_ultimo_num + 1, 4, '0'));
        ELSE
            SELECT COALESCE(MAX(CAST(SUBSTRING(cod_pro_ser, 4) AS UNSIGNED)), 0)
            INTO v_ultimo_num FROM PRODUCTO_SERVICIO WHERE cod_pro_ser LIKE 'SER%';
            SET NEW.cod_pro_ser = CONCAT('SER', LPAD(v_ultimo_num + 1, 4, '0'));
        END IF;
    END IF;
    SET @ultimo_cod_pro_ser = NEW.cod_pro_ser;
END //

DROP TRIGGER IF EXISTS trg_generar_nmr_cotizacion //
CREATE TRIGGER trg_generar_nmr_cotizacion
BEFORE INSERT ON COTIZACION
FOR EACH ROW
BEGIN
    DECLARE v_prefijo VARCHAR(8);
    DECLARE v_ultimo_correlativo INT DEFAULT 0;
    
    IF NEW.nmr_cotizacion IS NULL OR TRIM(NEW.nmr_cotizacion) = '' THEN
        SET v_prefijo = CONCAT('JP.', DATE_FORMAT(NEW.fecha_emision, '%y%m'));
        
        SELECT COALESCE(MAX(CAST(RIGHT(nmr_cotizacion, 5) AS UNSIGNED)), 0)
        INTO v_ultimo_correlativo
        FROM COTIZACION
        WHERE nmr_cotizacion LIKE 'JP.%';
        
        SET NEW.nmr_cotizacion = CONCAT(v_prefijo, LPAD(v_ultimo_correlativo + 1, 5, '0'));
    END IF;
    SET @ultimo_nmr_cotizacion = NEW.nmr_cotizacion;
END //


-- =============================================================================
-- SECCIÓN 2: PROCEDIMIENTOS ALMACENADOS - CLIENTES Y CONTACTOS
-- =============================================================================

DROP PROCEDURE IF EXISTS sp_crear_cliente //
CREATE PROCEDURE sp_crear_cliente(
    IN p_ruc VARCHAR(11),
    IN p_razon_social VARCHAR(150),
    IN p_direccion_via VARCHAR(200),
    IN p_id_distrito INT
)
BEGIN
    INSERT INTO CLIENTE (cod_interno, ruc, razon_social, direccion_via, id_distrito, estado)
    VALUES (NULL, p_ruc, p_razon_social, p_direccion_via, p_id_distrito, 'Activo');
    
    SELECT * FROM CLIENTE WHERE cod_interno = @ultimo_cod_cliente;
END //

DROP PROCEDURE IF EXISTS sp_listar_clientes_activos //
CREATE PROCEDURE sp_listar_clientes_activos()
BEGIN
    SELECT
        c.cod_interno,
        c.ruc,
        c.razon_social,
        c.direccion_via,
        c.id_distrito AS cod_distrito,
        d.nombre_distrito,
        p.nombre_provincia,
        dep.nombre_departamento,
        c.estado
    FROM CLIENTE c
    INNER JOIN DISTRITO d ON c.id_distrito = d.id_distrito
    INNER JOIN PROVINCIA p ON d.id_provincia = p.id_provincia
    INNER JOIN DEPARTAMENTO dep ON p.id_departamento = dep.id_departamento
    WHERE c.estado = 'Activo'
    ORDER BY c.razon_social;
END //

DROP PROCEDURE IF EXISTS sp_obtener_cliente_por_codigo //
CREATE PROCEDURE sp_obtener_cliente_por_codigo(
    IN p_cod_interno VARCHAR(10)
)
BEGIN
    SELECT
        cod_interno,
        ruc,
        razon_social,
        direccion_via,
        id_distrito AS cod_distrito
    FROM CLIENTE
    WHERE cod_interno = p_cod_interno
      AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_listar_distritos_activos //
CREATE PROCEDURE sp_listar_distritos_activos()
BEGIN
    SELECT
        d.id_distrito AS cod_distrito,
        d.nombre_distrito,
        p.nombre_provincia,
        dep.nombre_departamento
    FROM DISTRITO d
    INNER JOIN PROVINCIA p ON d.id_provincia = p.id_provincia
    INNER JOIN DEPARTAMENTO dep ON p.id_departamento = dep.id_departamento
    WHERE d.estado = 'Activo'
      AND p.estado = 'Activo'
      AND dep.estado = 'Activo'
    ORDER BY dep.nombre_departamento, p.nombre_provincia, d.nombre_distrito;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_cliente //
CREATE PROCEDURE sp_actualizar_cliente(
    IN p_cod_interno VARCHAR(10),
    IN p_ruc VARCHAR(11),
    IN p_razon_social VARCHAR(150),
    IN p_direccion_via VARCHAR(200),
    IN p_id_distrito INT
)
BEGIN
    UPDATE CLIENTE
    SET ruc = p_ruc,
        razon_social = p_razon_social,
        direccion_via = p_direccion_via,
        id_distrito = p_id_distrito
    WHERE cod_interno = p_cod_interno AND estado = 'Activo';
    
    SELECT ROW_COUNT() AS filas_afectadas;
END //

DROP PROCEDURE IF EXISTS sp_eliminar_cliente //
CREATE PROCEDURE sp_eliminar_cliente(
    IN p_cod_interno VARCHAR(10)
)
BEGIN
    UPDATE CLIENTE SET estado = 'Inactivo' WHERE cod_interno = p_cod_interno AND estado = 'Activo';
    SELECT ROW_COUNT() AS filas_afectadas;
    UPDATE CONTACTO_CLIENTE SET estado = 'Inactivo' WHERE cod_interno = p_cod_interno;
END //

DROP PROCEDURE IF EXISTS sp_listar_contactos_cliente //
CREATE PROCEDURE sp_listar_contactos_cliente(
    IN p_cod_interno VARCHAR(10)
)
BEGIN
    SELECT
        id_contacto,
        cod_interno,
        nombre_contacto,
        telefono_contacto,
        email_contacto
    FROM CONTACTO_CLIENTE
    WHERE cod_interno = p_cod_interno
      AND estado = 'Activo'
    ORDER BY nombre_contacto;
END //

DROP PROCEDURE IF EXISTS sp_crear_contacto_cliente //
CREATE PROCEDURE sp_crear_contacto_cliente(
    IN p_cod_interno VARCHAR(10),
    IN p_nombre_contacto VARCHAR(100),
    IN p_telefono_contacto VARCHAR(15),
    IN p_email_contacto VARCHAR(100)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM CLIENTE WHERE cod_interno = p_cod_interno AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cliente no existe o está inactivo.';
    END IF;

    INSERT INTO CONTACTO_CLIENTE (cod_interno, nombre_contacto, telefono_contacto, email_contacto, estado)
    VALUES (p_cod_interno, p_nombre_contacto, p_telefono_contacto, p_email_contacto, 'Activo');

    SELECT * FROM CONTACTO_CLIENTE WHERE id_contacto = LAST_INSERT_ID();
END //

DROP PROCEDURE IF EXISTS sp_actualizar_contacto_cliente //
CREATE PROCEDURE sp_actualizar_contacto_cliente(
    IN p_cod_interno VARCHAR(10),
    IN p_id_contacto INT,
    IN p_nombre_contacto VARCHAR(100),
    IN p_telefono_contacto VARCHAR(15),
    IN p_email_contacto VARCHAR(100)
)
BEGIN
    UPDATE CONTACTO_CLIENTE
    SET nombre_contacto = p_nombre_contacto,
        telefono_contacto = p_telefono_contacto,
        email_contacto = p_email_contacto
    WHERE cod_interno = p_cod_interno
      AND id_contacto = p_id_contacto
      AND estado = 'Activo';
      
    SELECT ROW_COUNT() AS filas_afectadas;
END //

DROP PROCEDURE IF EXISTS sp_eliminar_contacto_cliente //
CREATE PROCEDURE sp_eliminar_contacto_cliente(
    IN p_cod_interno VARCHAR(10),
    IN p_id_contacto INT
)
BEGIN
    UPDATE CONTACTO_CLIENTE
    SET estado = 'Inactivo'
    WHERE cod_interno = p_cod_interno
      AND id_contacto = p_id_contacto
      AND estado = 'Activo';
      
    SELECT ROW_COUNT() AS filas_afectadas;
END //


-- =============================================================================
-- SECCIÓN 3: PROCEDIMIENTOS ALMACENADOS - EMPLEADOS, CARGOS Y ESPECIALIDADES
-- =============================================================================

DROP PROCEDURE IF EXISTS sp_crear_empleado //
CREATE PROCEDURE sp_crear_empleado(
    IN p_DNI VARCHAR(8),
    IN p_nombre_completo VARCHAR(200),
    IN p_email VARCHAR(350),
    IN p_password_hash VARCHAR(255),
    IN p_telefono VARCHAR(15),
    IN p_id_cargo INT,
    IN p_id_especialidad INT
)
BEGIN
    INSERT INTO EMPLEADO (DNI, nombre_completo, email, password_hash, telefono, id_cargo, id_especialidad, estado)
    VALUES (p_DNI, p_nombre_completo, p_email, p_password_hash, p_telefono, p_id_cargo, p_id_especialidad, 'Activo');

    SELECT id_empleado, DNI, nombre_completo, email, telefono, id_cargo, id_especialidad, estado
    FROM EMPLEADO WHERE id_empleado = LAST_INSERT_ID();
END //

DROP PROCEDURE IF EXISTS sp_listar_empleados_activos //
CREATE PROCEDURE sp_listar_empleados_activos()
BEGIN
    SELECT e.id_empleado, e.DNI, e.nombre_completo, e.email, e.telefono, 
           c.nombre_cargo, esp.nombre_especialidad, e.estado
    FROM EMPLEADO e
    INNER JOIN CARGO c ON e.id_cargo = c.id_cargo
    INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
    WHERE e.estado = 'Activo'
    ORDER BY e.nombre_completo;
END //

DROP PROCEDURE IF EXISTS sp_obtener_empleado_por_id //
CREATE PROCEDURE sp_obtener_empleado_por_id(
    IN p_id_empleado INT
)
BEGIN
    SELECT id_empleado, DNI, nombre_completo, email, telefono, id_cargo, id_especialidad, estado
    FROM EMPLEADO
    WHERE id_empleado = p_id_empleado AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_obtener_empleado_login //
CREATE PROCEDURE sp_obtener_empleado_login(
    IN p_email VARCHAR(350)
)
BEGIN
    SELECT e.id_empleado, e.DNI, e.nombre_completo, e.email, e.password_hash, 
           e.id_cargo, c.nombre_cargo, e.estado
    FROM EMPLEADO e
    INNER JOIN CARGO c ON e.id_cargo = c.id_cargo
    WHERE e.email = p_email AND e.estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_actualizar_empleado //
CREATE PROCEDURE sp_actualizar_empleado(
    IN p_id_empleado INT,
    IN p_DNI VARCHAR(8),
    IN p_nombre_completo VARCHAR(200),
    IN p_email VARCHAR(350),
    IN p_telefono VARCHAR(15),
    IN p_id_cargo INT,
    IN p_id_especialidad INT
)
BEGIN
    UPDATE EMPLEADO
    SET DNI = p_DNI,
        nombre_completo = p_nombre_completo,
        email = p_email,
        telefono = p_telefono,
        id_cargo = p_id_cargo,
        id_especialidad = p_id_especialidad
    WHERE id_empleado = p_id_empleado AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_actualizar_password_empleado //
CREATE PROCEDURE sp_actualizar_password_empleado(
    IN p_id_empleado INT,
    IN p_nuevo_password_hash VARCHAR(255)
)
BEGIN
    UPDATE EMPLEADO
    SET password_hash = p_nuevo_password_hash
    WHERE id_empleado = p_id_empleado AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_eliminar_empleado //
CREATE PROCEDURE sp_eliminar_empleado(
    IN p_id_empleado INT
)
BEGIN
    UPDATE EMPLEADO SET estado = 'Inactivo' WHERE id_empleado = p_id_empleado;
END //

-- Catálogos Cargo y Especialidad
DROP PROCEDURE IF EXISTS sp_listar_cargos_activos //
CREATE PROCEDURE sp_listar_cargos_activos()
BEGIN
    SELECT id_cargo, nombre_cargo, descripcion, estado
    FROM CARGO WHERE estado = 'Activo' ORDER BY nombre_cargo;
END //

DROP PROCEDURE IF EXISTS sp_crear_cargo //
CREATE PROCEDURE sp_crear_cargo(IN p_nombre VARCHAR(30), IN p_descripcion VARCHAR(350))
BEGIN
    INSERT INTO CARGO (nombre_cargo, descripcion) VALUES (p_nombre, p_descripcion);
    SELECT LAST_INSERT_ID() AS id_cargo;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_cargo //
CREATE PROCEDURE sp_actualizar_cargo(IN p_id_cargo INT, IN p_nombre VARCHAR(30), IN p_descripcion VARCHAR(350))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM CARGO WHERE id_cargo = p_id_cargo AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cargo no existe o ya no está activo.';
    END IF;
    UPDATE CARGO SET nombre_cargo = p_nombre, descripcion = p_descripcion WHERE id_cargo = p_id_cargo AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_desactivar_cargo //
CREATE PROCEDURE sp_desactivar_cargo(IN p_id_cargo INT)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM CARGO WHERE id_cargo = p_id_cargo AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El cargo no existe o ya está inactivo.';
    END IF;
    UPDATE CARGO SET estado = 'Inactivo' WHERE id_cargo = p_id_cargo AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_listar_especialidades_activas //
CREATE PROCEDURE sp_listar_especialidades_activas()
BEGIN
    SELECT id_especialidad, nombre_especialidad, descripcion, area_conocimiento, certificacion_requerida, estado
    FROM ESPECIALIDAD WHERE estado = 'Activo' ORDER BY nombre_especialidad;
END //

DROP PROCEDURE IF EXISTS sp_crear_especialidad //
CREATE PROCEDURE sp_crear_especialidad(
    IN p_nombre VARCHAR(40),
    IN p_descripcion VARCHAR(350),
    IN p_area VARCHAR(40),
    IN p_certificacion VARCHAR(40)
)
BEGIN
    INSERT INTO ESPECIALIDAD (nombre_especialidad, descripcion, area_conocimiento, certificacion_requerida)
    VALUES (p_nombre, p_descripcion, p_area, p_certificacion);
    SELECT LAST_INSERT_ID() AS id_especialidad;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_especialidad //
CREATE PROCEDURE sp_actualizar_especialidad(
    IN p_id_especialidad INT,
    IN p_nombre VARCHAR(40),
    IN p_descripcion VARCHAR(350),
    IN p_area VARCHAR(40),
    IN p_certificacion VARCHAR(40)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ESPECIALIDAD WHERE id_especialidad = p_id_especialidad AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La especialidad no existe o ya no está activa.';
    END IF;
    UPDATE ESPECIALIDAD
    SET nombre_especialidad = p_nombre,
        descripcion = p_descripcion,
        area_conocimiento = p_area,
        certificacion_requerida = p_certificacion
    WHERE id_especialidad = p_id_especialidad AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_desactivar_especialidad //
CREATE PROCEDURE sp_desactivar_especialidad(IN p_id_especialidad INT)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ESPECIALIDAD WHERE id_especialidad = p_id_especialidad AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La especialidad no existe o ya está inactiva.';
    END IF;
    UPDATE ESPECIALIDAD SET estado = 'Inactivo' WHERE id_especialidad = p_id_especialidad AND estado = 'Activo';
END //


-- =============================================================================
-- SECCIÓN 4: PROCEDIMIENTOS ALMACENADOS - PRODUCTO_SERVICIO Y CATÁLOGOS
-- =============================================================================

DROP PROCEDURE IF EXISTS sp_crear_producto_servicio //
CREATE PROCEDURE sp_crear_producto_servicio(
    IN p_descripcion VARCHAR(350),
    IN p_id_unidad INT,
    IN p_id_tipo INT,
    IN p_precio_referencial DECIMAL(10,2)
)
BEGIN
    INSERT INTO PRODUCTO_SERVICIO (cod_pro_ser, Descripcion, id_unidad, id_tipo, Precio_referencial, estado)
    VALUES (NULL, p_descripcion, p_id_unidad, p_id_tipo, p_precio_referencial, 'Activo');
    
    SELECT * FROM PRODUCTO_SERVICIO WHERE cod_pro_ser = @ultimo_cod_pro_ser;
END //

DROP PROCEDURE IF EXISTS sp_registrar_item_completo //
CREATE PROCEDURE sp_registrar_item_completo(
    IN p_descripcion VARCHAR(350),
    IN p_id_unidad INT,
    IN p_id_tipo INT,
    IN p_precio DECIMAL(10,2),
    IN p_marca VARCHAR(50),
    IN p_modelo VARCHAR(50),
    IN p_anio YEAR,
    IN p_nmr_parte VARCHAR(50)
)
BEGIN
    DECLARE v_nombre_tipo VARCHAR(50);

    SELECT nombre_tipo INTO v_nombre_tipo
    FROM TIPO_PRODUCTO WHERE id_tipo = p_id_tipo AND estado = 'Activo';

    IF v_nombre_tipo IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo seleccionado no existe o está inactivo.';
    END IF;

    INSERT INTO PRODUCTO_SERVICIO (cod_pro_ser, Descripcion, id_unidad, id_tipo, Precio_referencial, estado)
    VALUES (NULL, p_descripcion, p_id_unidad, p_id_tipo, p_precio, 'Activo');

    IF LOWER(TRIM(v_nombre_tipo)) IN ('equipo', 'material') THEN
        INSERT INTO PRODUCTO (cod_pro_ser, marca, modelo, `año`, nmr_parte)
        VALUES (@ultimo_cod_pro_ser, p_marca, p_modelo, p_anio, p_nmr_parte);
    ELSEIF LOWER(TRIM(v_nombre_tipo)) = 'servicio' THEN
        INSERT INTO SERVICIO (cod_pro_ser) VALUES (@ultimo_cod_pro_ser);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tipo no soportado. Use Equipo, Material o Servicio.';
    END IF;

    SELECT @ultimo_cod_pro_ser AS cod_pro_ser;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_item_completo //
CREATE PROCEDURE sp_actualizar_item_completo(
    IN p_codigo VARCHAR(8),
    IN p_descripcion VARCHAR(350),
    IN p_id_unidad INT,
    IN p_id_tipo INT,
    IN p_precio DECIMAL(10,2),
    IN p_marca VARCHAR(50),
    IN p_modelo VARCHAR(50),
    IN p_anio YEAR,
    IN p_nmr_parte VARCHAR(50)
)
BEGIN
    DECLARE v_id_tipo_actual INT;
    DECLARE v_nombre_tipo VARCHAR(50);

    SELECT ps.id_tipo, tp.nombre_tipo
    INTO v_id_tipo_actual, v_nombre_tipo
    FROM PRODUCTO_SERVICIO ps
    INNER JOIN TIPO_PRODUCTO tp ON tp.id_tipo = ps.id_tipo
    WHERE ps.cod_pro_ser = p_codigo AND ps.estado = 'Activo';

    IF v_id_tipo_actual IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto o servicio no existe o está inactivo.';
    END IF;

    IF v_id_tipo_actual <> p_id_tipo THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se permite cambiar el tipo de un registro existente.';
    END IF;

    UPDATE PRODUCTO_SERVICIO
    SET Descripcion = p_descripcion,
        id_unidad = p_id_unidad,
        Precio_referencial = p_precio
    WHERE cod_pro_ser = p_codigo AND estado = 'Activo';

    IF LOWER(TRIM(v_nombre_tipo)) IN ('equipo', 'material') THEN
        UPDATE PRODUCTO
        SET marca = p_marca,
            modelo = p_modelo,
            `año` = p_anio,
            nmr_parte = p_nmr_parte
        WHERE cod_pro_ser = p_codigo;
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_listar_catalogo_activo //
CREATE PROCEDURE sp_listar_catalogo_activo()
BEGIN
    SELECT
        ps.cod_pro_ser,
        ps.Descripcion AS descripcion,
        ps.id_unidad,
        ps.id_tipo,
        um.nombre_unidad,
        um.abreviatura,
        tp.nombre_tipo,
        ps.Precio_referencial AS precio_referencial,
        ps.estado,
        p.marca,
        p.modelo,
        p.`año` AS anio,
        p.nmr_parte,
        CASE WHEN sv.cod_pro_ser IS NOT NULL THEN 'Servicio' ELSE 'Producto' END AS clasificacion
    FROM PRODUCTO_SERVICIO ps
    INNER JOIN UNIDAD_MEDIDA um ON um.id_unidad = ps.id_unidad
    INNER JOIN TIPO_PRODUCTO tp ON tp.id_tipo = ps.id_tipo
    LEFT JOIN PRODUCTO p ON p.cod_pro_ser = ps.cod_pro_ser
    LEFT JOIN SERVICIO sv ON sv.cod_pro_ser = ps.cod_pro_ser
    WHERE ps.estado = 'Activo'
    ORDER BY ps.cod_pro_ser;
END //

DROP PROCEDURE IF EXISTS sp_obtener_producto_por_codigo //
CREATE PROCEDURE sp_obtener_producto_por_codigo(IN p_codigo VARCHAR(8))
BEGIN
    SELECT
        ps.cod_pro_ser,
        ps.Descripcion AS descripcion,
        ps.id_unidad,
        ps.id_tipo,
        ps.Precio_referencial AS precio_referencial,
        ps.estado,
        p.marca,
        p.modelo,
        p.`año` AS anio,
        p.nmr_parte,
        sv.cod_pro_ser AS codigo_servicio
    FROM PRODUCTO_SERVICIO ps
    LEFT JOIN PRODUCTO p ON p.cod_pro_ser = ps.cod_pro_ser
    LEFT JOIN SERVICIO sv ON sv.cod_pro_ser = ps.cod_pro_ser
    WHERE ps.cod_pro_ser = p_codigo AND ps.estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_actualizar_precio_catalogo //
CREATE PROCEDURE sp_actualizar_precio_catalogo(
    IN p_cod_pro_ser VARCHAR(8),
    IN p_nuevo_precio DECIMAL(10,2)
)
BEGIN
    UPDATE PRODUCTO_SERVICIO
    SET Precio_referencial = p_nuevo_precio
    WHERE cod_pro_ser = p_cod_pro_ser AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_eliminar_producto_servicio //
CREATE PROCEDURE sp_eliminar_producto_servicio(
    IN p_cod_pro_ser VARCHAR(8)
)
BEGIN
    UPDATE PRODUCTO_SERVICIO SET estado = 'Inactivo' WHERE cod_pro_ser = p_cod_pro_ser;
END //

-- Unidades y Tipos de Producto
DROP PROCEDURE IF EXISTS sp_listar_unidades_activas //
CREATE PROCEDURE sp_listar_unidades_activas()
BEGIN
    SELECT id_unidad, nombre_unidad, abreviatura, estado
    FROM UNIDAD_MEDIDA WHERE estado = 'Activo' ORDER BY nombre_unidad;
END //

DROP PROCEDURE IF EXISTS sp_crear_unidad //
CREATE PROCEDURE sp_crear_unidad(IN p_nombre VARCHAR(50), IN p_abreviatura VARCHAR(5))
BEGIN
    INSERT INTO UNIDAD_MEDIDA (nombre_unidad, abreviatura) VALUES (p_nombre, p_abreviatura);
    SELECT LAST_INSERT_ID() AS id_unidad;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_unidad //
CREATE PROCEDURE sp_actualizar_unidad(IN p_id_unidad INT, IN p_nombre VARCHAR(50), IN p_abreviatura VARCHAR(5))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM UNIDAD_MEDIDA WHERE id_unidad = p_id_unidad AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La unidad no existe o está inactiva.';
    END IF;
    UPDATE UNIDAD_MEDIDA SET nombre_unidad = p_nombre, abreviatura = p_abreviatura WHERE id_unidad = p_id_unidad AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_desactivar_unidad //
CREATE PROCEDURE sp_desactivar_unidad(IN p_id_unidad INT)
BEGIN
    IF EXISTS (SELECT 1 FROM PRODUCTO_SERVICIO WHERE id_unidad = p_id_unidad AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede desactivar esta unidad porque está siendo utilizada por productos o servicios activos.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM UNIDAD_MEDIDA WHERE id_unidad = p_id_unidad AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La unidad no existe o ya está inactiva.';
    END IF;
    UPDATE UNIDAD_MEDIDA SET estado = 'Inactivo' WHERE id_unidad = p_id_unidad AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_listar_tipos_producto //
CREATE PROCEDURE sp_listar_tipos_producto()
BEGIN
    SELECT id_tipo, nombre_tipo, descripcion, estado
    FROM TIPO_PRODUCTO WHERE estado = 'Activo' ORDER BY id_tipo;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_tipo_producto //
CREATE PROCEDURE sp_actualizar_tipo_producto(IN p_id_tipo INT, IN p_nombre VARCHAR(50), IN p_descripcion VARCHAR(150))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM TIPO_PRODUCTO WHERE id_tipo = p_id_tipo AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo no existe o está inactivo.';
    END IF;
    UPDATE TIPO_PRODUCTO SET nombre_tipo = p_nombre, descripcion = p_descripcion WHERE id_tipo = p_id_tipo AND estado = 'Activo';
END //


-- =============================================================================
-- SECCIÓN 5: PROCEDIMIENTOS ALMACENADOS - COTIZACIONES Y PARÁMETROS
-- =============================================================================

DROP PROCEDURE IF EXISTS sp_crear_cotizacion //
CREATE PROCEDURE sp_crear_cotizacion(
    IN p_fecha_emision DATE,
    IN p_id_tipo_cotizacion INT,
    IN p_id_origen INT,
    IN p_id_moneda INT,
    IN p_impuesto VARCHAR(20),
    IN p_porcentaje_igv DECIMAL(5,2),
    IN p_id_forma_pago INT,
    IN p_id_garantia INT,
    IN p_tiempo_ejecucion VARCHAR(30),
    IN p_tiempo_entrega VARCHAR(30),
    IN p_vigencia_dias INT,
    IN p_exclusiones VARCHAR(250),
    IN p_observaciones VARCHAR(250),
    IN p_cod_interno_cliente VARCHAR(10),
    IN p_id_contacto INT,
    IN p_id_empleado INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM CLIENTE WHERE cod_interno = p_cod_interno_cliente AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El cliente no existe o se encuentra Inactivo.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM EMPLEADO WHERE id_empleado = p_id_empleado AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El empleado responsable no existe o se encuentra Inactivo.';
    END IF;

    IF p_id_contacto IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM CONTACTO_CLIENTE 
        WHERE id_contacto = p_id_contacto AND cod_interno = p_cod_interno_cliente AND estado = 'Activo'
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El contacto no pertenece al cliente o está Inactivo.';
    END IF;

    INSERT INTO COTIZACION (
        nmr_cotizacion, fecha_emision, id_tipo_cotizacion, id_origen, id_moneda,
        impuesto, porcentaje_igv, id_forma_pago, id_estado, id_garantia,
        tiempo_ejecucion, tiempo_entrega, vigencia_dias, exclusiones, observaciones,
        cod_interno_cliente, id_contacto, id_empleado
    ) VALUES (
        NULL, p_fecha_emision, p_id_tipo_cotizacion, p_id_origen, p_id_moneda,
        p_impuesto, COALESCE(p_porcentaje_igv, 18.00), p_id_forma_pago, 1, p_id_garantia,
        p_tiempo_ejecucion, p_tiempo_entrega, p_vigencia_dias, p_exclusiones, p_observaciones,
        p_cod_interno_cliente, p_id_contacto, p_id_empleado
    );
    
    SELECT * FROM COTIZACION WHERE nmr_cotizacion = @ultimo_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_cotizacion //
CREATE PROCEDURE sp_actualizar_cotizacion(
    IN p_nmr_cotizacion VARCHAR(15),
    IN p_fecha_emision DATE,
    IN p_id_tipo_cotizacion INT,
    IN p_id_origen INT,
    IN p_id_moneda INT,
    IN p_impuesto VARCHAR(20),
    IN p_porcentaje_igv DECIMAL(5,2),
    IN p_id_forma_pago INT,
    IN p_id_garantia INT,
    IN p_tiempo_ejecucion VARCHAR(30),
    IN p_tiempo_entrega VARCHAR(30),
    IN p_vigencia_dias INT,
    IN p_exclusiones VARCHAR(250),
    IN p_observaciones VARCHAR(250),
    IN p_cod_interno_cliente VARCHAR(10),
    IN p_id_contacto INT,
    IN p_id_empleado INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM COTIZACION WHERE nmr_cotizacion = p_nmr_cotizacion) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cotización seleccionada no existe.';
    END IF;

    UPDATE COTIZACION
    SET fecha_emision = p_fecha_emision,
        id_tipo_cotizacion = p_id_tipo_cotizacion,
        id_origen = p_id_origen,
        id_moneda = p_id_moneda,
        impuesto = p_impuesto,
        porcentaje_igv = COALESCE(p_porcentaje_igv, 18.00),
        id_forma_pago = p_id_forma_pago,
        id_garantia = p_id_garantia,
        tiempo_ejecucion = p_tiempo_ejecucion,
        tiempo_entrega = p_tiempo_entrega,
        vigencia_dias = p_vigencia_dias,
        exclusiones = p_exclusiones,
        observaciones = p_observaciones,
        cod_interno_cliente = p_cod_interno_cliente,
        id_contacto = p_id_contacto,
        id_empleado = p_id_empleado
    WHERE nmr_cotizacion = p_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_eliminar_detalles_cotizacion //
CREATE PROCEDURE sp_eliminar_detalles_cotizacion(
    IN p_nmr_cotizacion VARCHAR(15)
)
BEGIN
    DELETE FROM DETALLE_COTIZACION WHERE nmr_cotizacion = p_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_agregar_detalle_cotizacion //
CREATE PROCEDURE sp_agregar_detalle_cotizacion(
    IN p_nmr_cotizacion VARCHAR(15),
    IN p_cod_pro_ser VARCHAR(8),
    IN p_cantidad INT,
    IN p_precio_unitario DECIMAL(10,2),
    IN p_alcance_tecnico VARCHAR(300)
)
BEGIN
    DECLARE v_siguiente_item INT DEFAULT 1;

    IF NOT EXISTS (SELECT 1 FROM PRODUCTO_SERVICIO WHERE cod_pro_ser = p_cod_pro_ser AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El producto/servicio no existe o está Inactivo.';
    END IF;

    SELECT COALESCE(MAX(item), 0) + 1
    INTO v_siguiente_item
    FROM DETALLE_COTIZACION
    WHERE nmr_cotizacion = p_nmr_cotizacion;

    INSERT INTO DETALLE_COTIZACION (nmr_cotizacion, cod_pro_ser, item, cantidad, precio_unitario, alcance_tecnico)
    VALUES (p_nmr_cotizacion, p_cod_pro_ser, v_siguiente_item, p_cantidad, p_precio_unitario, p_alcance_tecnico);

    SELECT * FROM DETALLE_COTIZACION WHERE id_detalle = LAST_INSERT_ID();
END //

DROP PROCEDURE IF EXISTS sp_actualizar_estado_cotizacion //
CREATE PROCEDURE sp_actualizar_estado_cotizacion(
    IN p_nmr_cotizacion VARCHAR(15),
    IN p_nuevo_id_estado INT
)
BEGIN
    UPDATE COTIZACION
    SET id_estado = p_nuevo_id_estado
    WHERE nmr_cotizacion = p_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_anular_cotizacion //
CREATE PROCEDURE sp_anular_cotizacion(
    IN p_nmr_cotizacion VARCHAR(15),
    IN p_motivo_anulacion VARCHAR(250)
)
BEGIN
    UPDATE COTIZACION
    SET id_estado = 6,
        observaciones = CONCAT(COALESCE(observaciones, ''), ' | ANULADA: ', p_motivo_anulacion)
    WHERE nmr_cotizacion = p_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_listar_cotizaciones //
CREATE PROCEDURE sp_listar_cotizaciones(
    IN p_filtro VARCHAR(150)
)
BEGIN
    DECLARE v_patron VARCHAR(160);
    SET v_patron = CONCAT('%', TRIM(COALESCE(p_filtro, '')), '%');

    SELECT c.nmr_cotizacion, c.fecha_emision, cl.razon_social,
           ec.descripcion AS estado, m.codigo_iso AS moneda,
           c.vigencia_dias,
           DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY) AS fecha_vencimiento,
           COALESCE(d.subtotal, 0.00) AS subtotal
    FROM COTIZACION c
    INNER JOIN CLIENTE cl ON cl.cod_interno = c.cod_interno_cliente
    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado
    INNER JOIN MONEDA m ON m.id_moneda = c.id_moneda
    LEFT JOIN (
        SELECT nmr_cotizacion, SUM(cantidad * precio_unitario) AS subtotal
        FROM DETALLE_COTIZACION GROUP BY nmr_cotizacion
    ) d ON d.nmr_cotizacion = c.nmr_cotizacion
    WHERE c.nmr_cotizacion LIKE v_patron
       OR cl.razon_social LIKE v_patron
       OR ec.descripcion LIKE v_patron
    ORDER BY c.fecha_emision DESC, c.nmr_cotizacion DESC;
END //

DROP PROCEDURE IF EXISTS sp_obtener_cotizacion_encabezado //
CREATE PROCEDURE sp_obtener_cotizacion_encabezado(
    IN p_nmr_cotizacion VARCHAR(15)
)
BEGIN
    SELECT c.*, cl.ruc, cl.razon_social, cl.direccion_via,
           di.nombre_distrito, pr.nombre_provincia, de.nombre_departamento,
           cc.nombre_contacto, cc.telefono_contacto, cc.email_contacto,
           e.DNI, e.nombre_completo AS responsable,
           tc.descripcion AS tipo_cotizacion,
           os.descripcion AS origen_solicitud,
           m.nombre AS moneda_nombre, m.simbolo AS moneda_simbolo, m.codigo_iso,
           fp.descripcion AS forma_pago,
           ec.descripcion AS estado_descripcion,
           g.tiempo_garantia, g.unidad_garantia
    FROM COTIZACION c
    INNER JOIN CLIENTE cl ON cl.cod_interno = c.cod_interno_cliente
    INNER JOIN DISTRITO di ON di.id_distrito = cl.id_distrito
    INNER JOIN PROVINCIA pr ON pr.id_provincia = di.id_provincia
    INNER JOIN DEPARTAMENTO de ON de.id_departamento = pr.id_departamento
    LEFT JOIN CONTACTO_CLIENTE cc ON cc.id_contacto = c.id_contacto
    INNER JOIN EMPLEADO e ON e.id_empleado = c.id_empleado
    INNER JOIN TIPO_COTIZACION tc ON tc.id_tipo_cotizacion = c.id_tipo_cotizacion
    INNER JOIN ORIGEN_SOLICITUD os ON os.id_origen = c.id_origen
    INNER JOIN MONEDA m ON m.id_moneda = c.id_moneda
    INNER JOIN FORMA_PAGO fp ON fp.id_forma_pago = c.id_forma_pago
    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado
    INNER JOIN GARANTIA g ON g.id_garantia = c.id_garantia
    WHERE c.nmr_cotizacion = p_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_obtener_cotizacion_detalles //
CREATE PROCEDURE sp_obtener_cotizacion_detalles(
    IN p_nmr_cotizacion VARCHAR(15)
)
BEGIN
    SELECT d.id_detalle, d.item, d.cod_pro_ser,
           ps.Descripcion AS descripcion, um.abreviatura AS unidad,
           d.cantidad, d.precio_unitario, d.alcance_tecnico
    FROM DETALLE_COTIZACION d
    INNER JOIN PRODUCTO_SERVICIO ps ON ps.cod_pro_ser = d.cod_pro_ser
    INNER JOIN UNIDAD_MEDIDA um ON um.id_unidad = ps.id_unidad
    WHERE d.nmr_cotizacion = p_nmr_cotizacion
    ORDER BY d.item;
END //

DROP PROCEDURE IF EXISTS sp_obtener_resumen_dashboard //
CREATE PROCEDURE sp_obtener_resumen_dashboard()
BEGIN
    SELECT
        COUNT(DISTINCT c.nmr_cotizacion) AS total_cotizaciones,
        SUM(CASE WHEN ec.descripcion IN ('En revision','En revisión','Enviada','En negociacion','En negociación') THEN 1 ELSE 0 END) AS pendientes,
        SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN 1 ELSE 0 END) AS aprobadas,
        (SELECT COUNT(*) FROM CLIENTE WHERE estado = 'Activo') AS clientes
    FROM COTIZACION c
    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado;
END //

DROP PROCEDURE IF EXISTS sp_listar_cotizaciones_recientes //
CREATE PROCEDURE sp_listar_cotizaciones_recientes(IN p_limite INT)
BEGIN
    DECLARE v_lim INT;
    SET v_lim = GREATEST(1, LEAST(COALESCE(p_limite, 8), 50));

    SELECT c.nmr_cotizacion, c.fecha_emision, cl.razon_social,
           e.nombre_completo AS responsable, ec.descripcion AS estado
    FROM COTIZACION c
    INNER JOIN CLIENTE cl ON cl.cod_interno = c.cod_interno_cliente
    INNER JOIN EMPLEADO e ON e.id_empleado = c.id_empleado
    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado
    ORDER BY c.fecha_emision DESC, c.nmr_cotizacion DESC
    LIMIT v_lim;
END //

-- =============================================================================
-- SECCIÓN 6: PROCEDIMIENTOS PARA PARÁMETROS GENERALES
-- =============================================================================

DROP PROCEDURE IF EXISTS sp_listar_parametros //
CREATE PROCEDURE sp_listar_parametros(IN p_catalogo VARCHAR(40))
BEGIN
    IF p_catalogo = 'tipo_cotizacion' THEN
        SELECT id_tipo_cotizacion, descripcion, estado FROM TIPO_COTIZACION WHERE estado = 'Activo' ORDER BY descripcion;
    ELSEIF p_catalogo = 'origen_solicitud' THEN
        SELECT id_origen, descripcion, estado FROM ORIGEN_SOLICITUD WHERE estado = 'Activo' ORDER BY descripcion;
    ELSEIF p_catalogo = 'moneda' THEN
        SELECT id_moneda, nombre, simbolo, codigo_iso, estado FROM MONEDA WHERE estado = 'Activo' ORDER BY nombre;
    ELSEIF p_catalogo = 'forma_pago' THEN
        SELECT id_forma_pago, descripcion, dias_credito, estado FROM FORMA_PAGO WHERE estado = 'Activo' ORDER BY dias_credito, descripcion;
    ELSEIF p_catalogo = 'estado_cotizacion' THEN
        SELECT id_estado, descripcion, estado FROM ESTADO_COTIZACION WHERE estado = 'Activo' ORDER BY id_estado;
    ELSEIF p_catalogo = 'garantia' THEN
        SELECT id_garantia, tiempo_garantia, unidad_garantia, estado FROM GARANTIA WHERE estado = 'Activo' ORDER BY tiempo_garantia;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El catálogo solicitado no es válido.';
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_insertar_parametro //
CREATE PROCEDURE sp_insertar_parametro(
    IN p_catalogo VARCHAR(40),
    IN p_val1 VARCHAR(150),
    IN p_val2 VARCHAR(50),
    IN p_val3 VARCHAR(20)
)
BEGIN
    IF p_catalogo = 'tipo_cotizacion' THEN
        INSERT INTO TIPO_COTIZACION (descripcion) VALUES (p_val1);
    ELSEIF p_catalogo = 'origen_solicitud' THEN
        INSERT INTO ORIGEN_SOLICITUD (descripcion) VALUES (p_val1);
    ELSEIF p_catalogo = 'moneda' THEN
        INSERT INTO MONEDA (nombre, simbolo, codigo_iso) VALUES (p_val1, p_val2, p_val3);
    ELSEIF p_catalogo = 'forma_pago' THEN
        INSERT INTO FORMA_PAGO (descripcion, dias_credito) VALUES (p_val1, CAST(p_val2 AS SIGNED));
    ELSEIF p_catalogo = 'estado_cotizacion' THEN
        INSERT INTO ESTADO_COTIZACION (descripcion) VALUES (p_val1);
    ELSEIF p_catalogo = 'garantia' THEN
        INSERT INTO GARANTIA (tiempo_garantia, unidad_garantia) VALUES (CAST(p_val1 AS SIGNED), p_val2);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El catálogo solicitado no es válido.';
    END IF;
    SELECT LAST_INSERT_ID() AS nuevo_id;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_parametro //
CREATE PROCEDURE sp_actualizar_parametro(
    IN p_catalogo VARCHAR(40),
    IN p_id INT,
    IN p_val1 VARCHAR(150),
    IN p_val2 VARCHAR(50),
    IN p_val3 VARCHAR(20)
)
BEGIN
    IF p_catalogo = 'tipo_cotizacion' THEN
        UPDATE TIPO_COTIZACION SET descripcion = p_val1 WHERE id_tipo_cotizacion = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'origen_solicitud' THEN
        UPDATE ORIGEN_SOLICITUD SET descripcion = p_val1 WHERE id_origen = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'moneda' THEN
        UPDATE MONEDA SET nombre = p_val1, simbolo = p_val2, codigo_iso = p_val3 WHERE id_moneda = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'forma_pago' THEN
        UPDATE FORMA_PAGO SET descripcion = p_val1, dias_credito = CAST(p_val2 AS SIGNED) WHERE id_forma_pago = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'estado_cotizacion' THEN
        UPDATE ESTADO_COTIZACION SET descripcion = p_val1 WHERE id_estado = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'garantia' THEN
        UPDATE GARANTIA SET tiempo_garantia = CAST(p_val1 AS SIGNED), unidad_garantia = p_val2 WHERE id_garantia = p_id AND estado = 'Activo';
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El catálogo solicitado no es válido.';
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_desactivar_parametro //
CREATE PROCEDURE sp_desactivar_parametro(
    IN p_catalogo VARCHAR(40),
    IN p_id INT
)
BEGIN
    DECLARE v_uso INT DEFAULT 0;

    IF p_catalogo = 'tipo_cotizacion' THEN
        SELECT COUNT(*) INTO v_uso FROM COTIZACION WHERE id_tipo_cotizacion = p_id;
        IF v_uso > 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede desactivar: parámetro en uso.'; END IF;
        UPDATE TIPO_COTIZACION SET estado = 'Inactivo' WHERE id_tipo_cotizacion = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'origen_solicitud' THEN
        SELECT COUNT(*) INTO v_uso FROM COTIZACION WHERE id_origen = p_id;
        IF v_uso > 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede desactivar: parámetro en uso.'; END IF;
        UPDATE ORIGEN_SOLICITUD SET estado = 'Inactivo' WHERE id_origen = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'moneda' THEN
        SELECT COUNT(*) INTO v_uso FROM COTIZACION WHERE id_moneda = p_id;
        IF v_uso > 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede desactivar: parámetro en uso.'; END IF;
        UPDATE MONEDA SET estado = 'Inactivo' WHERE id_moneda = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'forma_pago' THEN
        SELECT COUNT(*) INTO v_uso FROM COTIZACION WHERE id_forma_pago = p_id;
        IF v_uso > 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede desactivar: parámetro en uso.'; END IF;
        UPDATE FORMA_PAGO SET estado = 'Inactivo' WHERE id_forma_pago = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'estado_cotizacion' THEN
        SELECT COUNT(*) INTO v_uso FROM COTIZACION WHERE id_estado = p_id;
        IF v_uso > 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede desactivar: parámetro en uso.'; END IF;
        UPDATE ESTADO_COTIZACION SET estado = 'Inactivo' WHERE id_estado = p_id AND estado = 'Activo';
    ELSEIF p_catalogo = 'garantia' THEN
        SELECT COUNT(*) INTO v_uso FROM COTIZACION WHERE id_garantia = p_id;
        IF v_uso > 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede desactivar: parámetro en uso.'; END IF;
        UPDATE GARANTIA SET estado = 'Inactivo' WHERE id_garantia = p_id AND estado = 'Activo';
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El catálogo solicitado no es válido.';
    END IF;
END //

DELIMITER ;