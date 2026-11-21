-- =============================================================================
-- 2. SCRIPT DE PROGRAMACIÓN EN EL SGBD: TRIGGERS Y PROCEDIMIENTOS (CRUD)
-- Empresa: J.P. Ingeniería y Servicios S.R.L.
-- Módulo: Gestión de Cotizaciones Comerciales (HVAC)
-- Gestor: MySQL 8.0+
-- =============================================================================

USE cotizacion;

DELIMITER //

-- =============================================================================
-- SECCIÓN 1: DISPARADORES (TRIGGERS) PARA GENERACIÓN AUTOMÁTICA DE CÓDIGOS
-- =============================================================================

-- 1.1 Trigger para autogenerar código de CLIENTE (Formato: CLI001, CLI002...)
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

-- 1.2 Trigger para autogenerar codigo de PRODUCTO_SERVICIO.
-- La clasificacion se resuelve por nombre de catalogo, no por IDs autoincrementales.
DROP TRIGGER IF EXISTS trg_generar_cod_pro_ser //
CREATE TRIGGER trg_generar_cod_pro_ser
BEFORE INSERT ON PRODUCTO_SERVICIO
FOR EACH ROW
BEGIN
    DECLARE v_ultimo_num INT DEFAULT 0;
    DECLARE v_nombre_tipo VARCHAR(50);

    SELECT nombre_tipo INTO v_nombre_tipo
      FROM TIPO_PRODUCTO
     WHERE id_tipo = NEW.id_tipo AND estado = 'Activo'
     LIMIT 1;

    IF v_nombre_tipo IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo de producto no existe o esta inactivo.';
    END IF;

    IF NEW.cod_pro_ser IS NULL OR TRIM(NEW.cod_pro_ser) = '' THEN
        IF LOWER(TRIM(v_nombre_tipo)) = 'equipo' THEN
            SELECT COALESCE(MAX(CAST(SUBSTRING(cod_pro_ser, 4) AS UNSIGNED)), 8600)
              INTO v_ultimo_num FROM PRODUCTO_SERVICIO WHERE cod_pro_ser LIKE 'EQU%';
            SET NEW.cod_pro_ser = CONCAT('EQU', LPAD(v_ultimo_num + 1, 5, '0'));
        ELSEIF LOWER(TRIM(v_nombre_tipo)) = 'material' THEN
            SELECT COALESCE(MAX(CAST(SUBSTRING(cod_pro_ser, 4) AS UNSIGNED)), 1900)
              INTO v_ultimo_num FROM PRODUCTO_SERVICIO WHERE cod_pro_ser LIKE 'MAT%';
            SET NEW.cod_pro_ser = CONCAT('MAT', LPAD(v_ultimo_num + 1, 4, '0'));
        ELSEIF LOWER(TRIM(v_nombre_tipo)) = 'servicio' THEN
            SELECT COALESCE(MAX(CAST(SUBSTRING(cod_pro_ser, 4) AS UNSIGNED)), 0)
              INTO v_ultimo_num FROM PRODUCTO_SERVICIO WHERE cod_pro_ser LIKE 'SER%';
            SET NEW.cod_pro_ser = CONCAT('SER', LPAD(v_ultimo_num + 1, 4, '0'));
        ELSE
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se admiten tipos Equipo, Material o Servicio.';
        END IF;
    END IF;
    SET @ultimo_cod_pro_ser = NEW.cod_pro_ser;
END //

-- 1.3 Trigger para autogenerar N° de COTIZACION (Formato: JP.AAMM00001)
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
        WHERE nmr_cotizacion LIKE CONCAT(v_prefijo, '%');
        
        SET NEW.nmr_cotizacion = CONCAT(v_prefijo, LPAD(v_ultimo_correlativo + 1, 5, '0'));
    END IF;
    SET @ultimo_nmr_cotizacion = NEW.nmr_cotizacion;
END //


-- =============================================================================
-- SECCIÓN 2: PROCEDIMIENTOS ALMACENADOS (CRUD CON BORRADO LÓGICO)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 2.1 CRUD ENTIDAD: CLIENTE Y CONTACTO_CLIENTE
-- -----------------------------------------------------------------------------

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

DROP PROCEDURE IF EXISTS sp_actualizar_cliente //
CREATE PROCEDURE sp_actualizar_cliente(
    IN p_cod_interno VARCHAR(10),
    IN p_razon_social VARCHAR(150),
    IN p_direccion_via VARCHAR(200),
    IN p_id_distrito INT
)
BEGIN
    UPDATE CLIENTE
    SET razon_social = p_razon_social,
        direccion_via = p_direccion_via,
        id_distrito = p_id_distrito
    WHERE cod_interno = p_cod_interno AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_eliminar_cliente //
CREATE PROCEDURE sp_eliminar_cliente(
    IN p_cod_interno VARCHAR(10)
)
BEGIN
    UPDATE CLIENTE SET estado = 'Inactivo' WHERE cod_interno = p_cod_interno;
    UPDATE CONTACTO_CLIENTE SET estado = 'Inactivo' WHERE cod_interno = p_cod_interno;
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


-- -----------------------------------------------------------------------------
-- 2.2 CRUD ENTIDAD: EMPLEADO (sin cuentas de acceso al aplicativo)
-- -----------------------------------------------------------------------------

DROP PROCEDURE IF EXISTS sp_crear_empleado //
CREATE PROCEDURE sp_crear_empleado(
    IN p_DNI VARCHAR(8),
    IN p_nombre_completo VARCHAR(200),
    IN p_email VARCHAR(350),
    IN p_hash_tecnico VARCHAR(255),
    IN p_telefono VARCHAR(15),
    IN p_id_cargo INT,
    IN p_id_especialidad INT
)
BEGIN
    INSERT INTO EMPLEADO (DNI, nombre_completo, email, password_hash, telefono, id_cargo, id_especialidad, estado)
    VALUES (p_DNI, p_nombre_completo, p_email, p_hash_tecnico, p_telefono, p_id_cargo, p_id_especialidad, 'Activo');

    SELECT id_empleado, DNI, nombre_completo, email, telefono, id_cargo, id_especialidad, estado
    FROM EMPLEADO WHERE id_empleado = LAST_INSERT_ID();
END //

-- El hash tecnico solo satisface la columna NOT NULL del esquema; no implementa login.
DROP PROCEDURE IF EXISTS sp_listar_empleados_activos //
CREATE PROCEDURE sp_listar_empleados_activos()
BEGIN
    SELECT e.id_empleado, e.DNI, e.nombre_completo, e.email, e.telefono, 
           c.nombre_cargo, esp.nombre_especialidad, e.estado
    FROM EMPLEADO e
    INNER JOIN CARGO c ON e.id_cargo = c.id_cargo
    INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
    WHERE e.estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_actualizar_empleado //
CREATE PROCEDURE sp_actualizar_empleado(
    IN p_id_empleado INT,
    IN p_email VARCHAR(350),
    IN p_telefono VARCHAR(15),
    IN p_id_cargo INT,
    IN p_id_especialidad INT
)
BEGIN
    UPDATE EMPLEADO
    SET email = p_email,
        telefono = p_telefono,
        id_cargo = p_id_cargo,
        id_especialidad = p_id_especialidad
    WHERE id_empleado = p_id_empleado AND estado = 'Activo';
END //

DROP PROCEDURE IF EXISTS sp_eliminar_empleado //
CREATE PROCEDURE sp_eliminar_empleado(
    IN p_id_empleado INT
)
BEGIN
    UPDATE EMPLEADO SET estado = 'Inactivo' WHERE id_empleado = p_id_empleado;
END //


-- -----------------------------------------------------------------------------
-- 2.3 CRUD ENTIDAD: PRODUCTO_SERVICIO
-- -----------------------------------------------------------------------------

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

DROP PROCEDURE IF EXISTS sp_eliminar_producto_servicio //
CREATE PROCEDURE sp_eliminar_producto_servicio(
    IN p_cod_pro_ser VARCHAR(8)
)
BEGIN
    UPDATE PRODUCTO_SERVICIO SET estado = 'Inactivo' WHERE cod_pro_ser = p_cod_pro_ser;
END //


-- -----------------------------------------------------------------------------
-- 2.4 CRUD ENTIDAD: COTIZACION Y DETALLE_COTIZACION
-- -----------------------------------------------------------------------------

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
    DECLARE v_id_estado_borrador INT DEFAULT NULL;

    -- Validar cliente activo
    IF NOT EXISTS (SELECT 1 FROM CLIENTE WHERE cod_interno = p_cod_interno_cliente AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El cliente no existe o se encuentra Inactivo.';
    END IF;

    -- Validar empleado activo
    IF NOT EXISTS (SELECT 1 FROM EMPLEADO WHERE id_empleado = p_id_empleado AND estado = 'Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El empleado responsable no existe o se encuentra Inactivo.';
    END IF;

    -- Validar que el contacto (si se envía) pertenezca al cliente y esté activo
    IF p_id_contacto IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM CONTACTO_CLIENTE 
        WHERE id_contacto = p_id_contacto AND cod_interno = p_cod_interno_cliente AND estado = 'Activo'
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El contacto no pertenece al cliente o está Inactivo.';
    END IF;

    -- Resolver el estado por descripción para no depender del valor AUTO_INCREMENT.
    SELECT id_estado
      INTO v_id_estado_borrador
      FROM ESTADO_COTIZACION
     WHERE descripcion = 'Borrador'
       AND estado = 'Activo'
     LIMIT 1;

    IF v_id_estado_borrador IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No existe un estado activo Borrador en ESTADO_COTIZACION.';
    END IF;

    INSERT INTO COTIZACION (
        nmr_cotizacion, fecha_emision, id_tipo_cotizacion, id_origen, id_moneda,
        impuesto, porcentaje_igv, id_forma_pago, id_estado, id_garantia,
        tiempo_ejecucion, tiempo_entrega, vigencia_dias, exclusiones, observaciones,
        cod_interno_cliente, id_contacto, id_empleado
    ) VALUES (
        NULL, p_fecha_emision, p_id_tipo_cotizacion, p_id_origen, p_id_moneda,
        p_impuesto, COALESCE(p_porcentaje_igv, 18.00), p_id_forma_pago, v_id_estado_borrador, p_id_garantia,
        p_tiempo_ejecucion, p_tiempo_entrega, p_vigencia_dias, p_exclusiones, p_observaciones,
        p_cod_interno_cliente, p_id_contacto, p_id_empleado
    );
    
    SELECT * FROM COTIZACION WHERE nmr_cotizacion = @ultimo_nmr_cotizacion;
END //

-- Agregar ítem al detalle autogenerando el correlativo (item 1, 2, 3...)
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


-- Actualizacion controlada de la cabecera. Los detalles se gestionan mediante su propio SP.
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
    IF NOT EXISTS (SELECT 1 FROM COTIZACION WHERE nmr_cotizacion=p_nmr_cotizacion) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='La cotizacion indicada no existe.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM CLIENTE WHERE cod_interno=p_cod_interno_cliente AND estado='Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El cliente no existe o esta inactivo.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM EMPLEADO WHERE id_empleado=p_id_empleado AND estado='Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El responsable no existe o esta inactivo.';
    END IF;
    IF p_id_contacto IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM CONTACTO_CLIENTE WHERE id_contacto=p_id_contacto
        AND cod_interno=p_cod_interno_cliente AND estado='Activo'
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El contacto no pertenece al cliente o esta inactivo.';
    END IF;
    UPDATE COTIZACION SET fecha_emision=p_fecha_emision, id_tipo_cotizacion=p_id_tipo_cotizacion,
        id_origen=p_id_origen, id_moneda=p_id_moneda, impuesto=p_impuesto,
        porcentaje_igv=p_porcentaje_igv, id_forma_pago=p_id_forma_pago, id_garantia=p_id_garantia,
        tiempo_ejecucion=p_tiempo_ejecucion, tiempo_entrega=p_tiempo_entrega,
        vigencia_dias=p_vigencia_dias, exclusiones=p_exclusiones, observaciones=p_observaciones,
        cod_interno_cliente=p_cod_interno_cliente, id_contacto=p_id_contacto, id_empleado=p_id_empleado
    WHERE nmr_cotizacion=p_nmr_cotizacion;
    SELECT nmr_cotizacion FROM COTIZACION WHERE nmr_cotizacion=p_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_eliminar_detalles_cotizacion //
CREATE PROCEDURE sp_eliminar_detalles_cotizacion(IN p_nmr_cotizacion VARCHAR(15))
BEGIN
    DELETE FROM DETALLE_COTIZACION WHERE nmr_cotizacion=p_nmr_cotizacion;
END //

DROP PROCEDURE IF EXISTS sp_actualizar_estado_cotizacion //
CREATE PROCEDURE sp_actualizar_estado_cotizacion(
    IN p_nmr_cotizacion VARCHAR(15), IN p_id_estado INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM COTIZACION WHERE nmr_cotizacion=p_nmr_cotizacion) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='La cotizacion no existe.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM ESTADO_COTIZACION WHERE id_estado=p_id_estado AND estado='Activo') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El estado seleccionado no existe o esta inactivo.';
    END IF;
    UPDATE COTIZACION SET id_estado=p_id_estado WHERE nmr_cotizacion=p_nmr_cotizacion;
END //

DELIMITER ;