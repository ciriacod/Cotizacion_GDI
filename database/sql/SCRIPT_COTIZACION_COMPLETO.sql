-- =============================================================================
-- SCRIPT UNIFICADO DE LA BASE DE DATOS "cotizacion"
-- Empresa: J.P. Ingeniería y Servicios S.R.L.
-- Módulo: Gestión de Cotizaciones Comerciales (HVAC)
-- Gestor: MySQL 8.0+
--
-- Contenido (orden de ejecución):
--   PARTE 1. Esquema: base de datos y tablas      (01_esquema.sql)
--   PARTE 2. Triggers y procedimientos            (02_triggers_procedimientos.sql)
--   PARTE 3. Catálogos iniciales                  (03_catalogos_iniciales.sql)
--   PARTE 4. Procedimientos de reportes (10)      (04_procedimientos_reportes.sql)
--   PARTE 5. Usuario de la aplicación (opcional)  (06_usuario_aplicacion_TEMPLATE.sql)
--
-- ADVERTENCIA: la Parte 1 ejecuta DROP DATABASE IF EXISTS cotizacion;
-- eliminará la base existente y la creará de nuevo desde cero.
-- Ejecutar completo, de una sola vez, con un usuario administrador de MySQL.
-- =============================================================================

-- #############################################################################
-- PARTE 1. ESQUEMA
-- #############################################################################
-- ===================================================
-- 1. CREACIÓN DE BASE DE DATOS Y TABLAS NORMALIZADAS
-- Empresa: J.P. Ingeniería y Servicios S.R.L.
-- Módulo: Gestión de Cotizaciones Comerciales (HVAC)
-- Gestor: MySQL 8.0+
-- ===================================================

DROP DATABASE IF EXISTS cotizacion;
CREATE DATABASE cotizacion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cotizacion;

-- ---------------------------------------------------
-- UBICACIÓN GEOGRÁFICA (Estándar UBIGEO como UNIQUE)
-- ---------------------------------------------------

CREATE TABLE DEPARTAMENTO (
    id_departamento      INT AUTO_INCREMENT NOT NULL,
    cod_ubigeo           VARCHAR(2) NOT NULL,
    nombre_departamento  VARCHAR(50) NOT NULL,
    estado               VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_departamento PRIMARY KEY (id_departamento),
    CONSTRAINT uk_departamento_ubigeo UNIQUE (cod_ubigeo),
    CONSTRAINT uk_departamento_nombre UNIQUE (nombre_departamento),
    CONSTRAINT chk_departamento_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE PROVINCIA (
    id_provincia       INT AUTO_INCREMENT NOT NULL,
    cod_ubigeo         VARCHAR(4) NOT NULL,
    nombre_provincia   VARCHAR(50) NOT NULL,
    id_departamento    INT NOT NULL,
    estado             VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_provincia PRIMARY KEY (id_provincia),
    CONSTRAINT uk_provincia_ubigeo UNIQUE (cod_ubigeo),
    CONSTRAINT uq_provincia_nombre UNIQUE (id_departamento, nombre_provincia),
    CONSTRAINT chk_provincia_estado CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT fk_provincia_departamento FOREIGN KEY (id_departamento)
        REFERENCES DEPARTAMENTO(id_departamento)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE DISTRITO (
    id_distrito       INT AUTO_INCREMENT NOT NULL,
    cod_ubigeo        VARCHAR(6) NOT NULL,
    nombre_distrito   VARCHAR(50) NOT NULL,
    id_provincia      INT NOT NULL,
    estado            VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_distrito PRIMARY KEY (id_distrito),
    CONSTRAINT uk_distrito_ubigeo UNIQUE (cod_ubigeo),
    CONSTRAINT uq_distrito_nombre UNIQUE (id_provincia, nombre_distrito),
    CONSTRAINT chk_distrito_estado CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT fk_distrito_provincia FOREIGN KEY (id_provincia)
        REFERENCES PROVINCIA(id_provincia)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------
-- EMPLEADOS, CARGOS Y ESPECIALIDADES
-- ---------------------------------------------------

CREATE TABLE CARGO (
    id_cargo     INT AUTO_INCREMENT NOT NULL,
    nombre_cargo VARCHAR(30) NOT NULL,
    descripcion  VARCHAR(350) NULL,
    estado       VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_cargo PRIMARY KEY (id_cargo),
    CONSTRAINT uk_cargo_nombre UNIQUE (nombre_cargo),
    CONSTRAINT chk_cargo_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ESPECIALIDAD (
    id_especialidad          INT AUTO_INCREMENT NOT NULL,
    nombre_especialidad      VARCHAR(40) NOT NULL,
    descripcion              VARCHAR(350) NULL,
    area_conocimiento        VARCHAR(40) NOT NULL,
    certificacion_requerida  VARCHAR(40) NULL,
    estado                   VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_especialidad PRIMARY KEY (id_especialidad),
    CONSTRAINT uk_especialidad_nombre UNIQUE (nombre_especialidad),
    CONSTRAINT chk_especialidad_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE EMPLEADO (
    id_empleado      INT AUTO_INCREMENT NOT NULL,
    DNI              VARCHAR(8) NOT NULL,
    nombre_completo  VARCHAR(200) NOT NULL,
    email            VARCHAR(350) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    telefono         VARCHAR(15) NULL,
    id_cargo         INT NOT NULL,
    id_especialidad  INT NOT NULL,
    estado           VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_empleado PRIMARY KEY (id_empleado),
    CONSTRAINT uk_empleado_dni UNIQUE (DNI),
    CONSTRAINT uk_empleado_email UNIQUE (email),
    CONSTRAINT chk_empleado_dni CHECK (CHAR_LENGTH(DNI) = 8),
    CONSTRAINT chk_empleado_estado CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT fk_empleado_cargo FOREIGN KEY (id_cargo)
        REFERENCES CARGO(id_cargo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_empleado_especialidad FOREIGN KEY (id_especialidad)
        REFERENCES ESPECIALIDAD(id_especialidad) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------
-- CLIENTES Y CONTACTOS
-- ---------------------------------------------------

CREATE TABLE CLIENTE (
    cod_interno     VARCHAR(10) NOT NULL, -- Autogenerado por Trigger (CLI001...)
    ruc             VARCHAR(11) NOT NULL,
    razon_social    VARCHAR(150) NOT NULL,
    direccion_via   VARCHAR(200) NOT NULL,
    id_distrito     INT NOT NULL,
    estado          VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_cliente PRIMARY KEY (cod_interno),
    CONSTRAINT uk_cliente_ruc UNIQUE (ruc),
    CONSTRAINT uk_cliente_razon UNIQUE (razon_social),
    CONSTRAINT chk_cliente_ruc CHECK (CHAR_LENGTH(ruc) = 11),
    CONSTRAINT chk_cliente_estado CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT fk_cliente_distrito FOREIGN KEY (id_distrito)
        REFERENCES DISTRITO(id_distrito) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE CONTACTO_CLIENTE (
    id_contacto         INT AUTO_INCREMENT NOT NULL,
    cod_interno         VARCHAR(10) NOT NULL,
    nombre_contacto     VARCHAR(100) NOT NULL,
    telefono_contacto   VARCHAR(15) NULL,
    email_contacto      VARCHAR(100) NULL,
    estado              VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_contacto_cliente PRIMARY KEY (id_contacto),
    CONSTRAINT uk_contacto_email UNIQUE (email_contacto),
    CONSTRAINT chk_contacto_estado CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT fk_contacto_cliente FOREIGN KEY (cod_interno)
        REFERENCES CLIENTE(cod_interno) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------
-- CATÁLOGOS DE PRODUCTOS Y SERVICIOS
-- ---------------------------------------------------

CREATE TABLE UNIDAD_MEDIDA (
    id_unidad       INT AUTO_INCREMENT NOT NULL,
    nombre_unidad   VARCHAR(50) NOT NULL,
    abreviatura     VARCHAR(5) NOT NULL,
    estado          VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_unidad_medida PRIMARY KEY (id_unidad),
    CONSTRAINT uq_unidad_abreviatura UNIQUE (abreviatura),
    CONSTRAINT chk_unidad_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE TIPO_PRODUCTO (
    id_tipo         INT AUTO_INCREMENT NOT NULL,
    nombre_tipo     VARCHAR(50) NOT NULL,
    descripcion     VARCHAR(150) NULL,
    estado          VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_tipo_producto PRIMARY KEY (id_tipo),
    CONSTRAINT uk_tipo_producto_nombre UNIQUE (nombre_tipo),
    CONSTRAINT chk_tipo_producto_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE PRODUCTO_SERVICIO (
    cod_pro_ser         VARCHAR(8) NOT NULL, -- Autogenerado por Trigger (EQU/MAT/SER...)
    Descripcion         VARCHAR(350) NOT NULL,
    id_unidad           INT NOT NULL,
    id_tipo             INT NOT NULL,
    Precio_referencial  DECIMAL(10,2) NOT NULL,
    estado              VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_producto_servicio PRIMARY KEY (cod_pro_ser),
    CONSTRAINT chk_precio_referencial CHECK (Precio_referencial >= 0),
    CONSTRAINT chk_proser_estado CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT fk_proser_unidad FOREIGN KEY (id_unidad)
        REFERENCES UNIDAD_MEDIDA(id_unidad) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_proser_tipo FOREIGN KEY (id_tipo)
        REFERENCES TIPO_PRODUCTO(id_tipo) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE PRODUCTO (
    cod_pro_ser VARCHAR(8) NOT NULL, -- Subtipo 1:1 de PRODUCTO_SERVICIO
    marca       VARCHAR(50) NOT NULL,
    modelo      VARCHAR(50) NOT NULL,
    año         YEAR NULL,
    nmr_parte   VARCHAR(50) NOT NULL,
    CONSTRAINT pk_producto PRIMARY KEY (cod_pro_ser),
    CONSTRAINT uk_producto_parte UNIQUE (nmr_parte),
    CONSTRAINT fk_producto_proser FOREIGN KEY (cod_pro_ser)
        REFERENCES PRODUCTO_SERVICIO(cod_pro_ser) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE SERVICIO (
    cod_pro_ser VARCHAR(8) NOT NULL, -- Subtipo 1:1 de PRODUCTO_SERVICIO
    CONSTRAINT pk_servicio PRIMARY KEY (cod_pro_ser),
    CONSTRAINT fk_servicio_proser FOREIGN KEY (cod_pro_ser)
        REFERENCES PRODUCTO_SERVICIO(cod_pro_ser) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------
-- PARÁMETROS Y CATÁLOGOS DE COTIZACIÓN
-- ---------------------------------------------------

CREATE TABLE TIPO_COTIZACION (
    id_tipo_cotizacion  INT AUTO_INCREMENT NOT NULL,
    descripcion         VARCHAR(150) NOT NULL,
    estado              VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_tipo_cotizacion PRIMARY KEY (id_tipo_cotizacion),
    CONSTRAINT uk_tipo_cotizacion_desc UNIQUE (descripcion),
    CONSTRAINT chk_tipo_cotiz_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ORIGEN_SOLICITUD (
    id_origen    INT AUTO_INCREMENT NOT NULL,
    descripcion  VARCHAR(150) NOT NULL,
    estado       VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_origen_solicitud PRIMARY KEY (id_origen),
    CONSTRAINT uk_origen_desc UNIQUE (descripcion),
    CONSTRAINT chk_origen_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE MONEDA (
    id_moneda    INT AUTO_INCREMENT NOT NULL,
    nombre       VARCHAR(30) NOT NULL,
    simbolo      VARCHAR(5) NOT NULL,
    codigo_iso   VARCHAR(3) NOT NULL,
    estado       VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_moneda PRIMARY KEY (id_moneda),
    CONSTRAINT uk_moneda_nombre UNIQUE (nombre),
    CONSTRAINT uk_moneda_simbolo UNIQUE (simbolo),
    CONSTRAINT uk_moneda_iso UNIQUE (codigo_iso),
    CONSTRAINT chk_moneda_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE FORMA_PAGO (
    id_forma_pago  INT AUTO_INCREMENT NOT NULL,
    descripcion    VARCHAR(100) NOT NULL,
    dias_credito   INT NOT NULL,
    estado         VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_forma_pago PRIMARY KEY (id_forma_pago),
    CONSTRAINT uk_forma_pago_desc UNIQUE (descripcion),
    CONSTRAINT ck_forma_pago_dias CHECK (dias_credito >= 0),
    CONSTRAINT chk_forma_pago_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ESTADO_COTIZACION (
    id_estado    INT AUTO_INCREMENT NOT NULL,
    descripcion  VARCHAR(50) NOT NULL,
    estado       VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_estado_cotizacion PRIMARY KEY (id_estado),
    CONSTRAINT uk_estado_cotizacion_desc UNIQUE (descripcion),
    CONSTRAINT chk_estado_cotiz_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE GARANTIA (
    id_garantia     INT AUTO_INCREMENT NOT NULL,
    tiempo_garantia INT NOT NULL,
    unidad_garantia VARCHAR(20) NOT NULL,
    estado          VARCHAR(10) NOT NULL DEFAULT 'Activo',
    CONSTRAINT pk_garantia PRIMARY KEY (id_garantia),
    CONSTRAINT ck_garantia_tiempo CHECK (tiempo_garantia > 0),
    CONSTRAINT chk_garantia_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------
-- TABLAS TRANSACCIONALES: COTIZACION Y DETALLE
-- ---------------------------------------------------

CREATE TABLE COTIZACION (
    nmr_cotizacion      VARCHAR(15) NOT NULL, -- Autogenerado por Trigger (JP.AAMM00001)
    fecha_emision       DATE NOT NULL,
    id_tipo_cotizacion  INT NOT NULL,
    id_origen           INT NOT NULL,
    id_moneda           INT NOT NULL,
    impuesto            VARCHAR(20) NOT NULL,
    porcentaje_igv      DECIMAL(5,2) NOT NULL DEFAULT 18.00,
    id_forma_pago       INT NOT NULL,
    id_estado           INT NOT NULL,
    id_garantia         INT NOT NULL,
    tiempo_ejecucion    VARCHAR(30) NOT NULL,
    tiempo_entrega      VARCHAR(30) NULL,
    vigencia_dias       INT NOT NULL,
    exclusiones         VARCHAR(250) NULL,
    observaciones       VARCHAR(250) NULL,
    cod_interno_cliente VARCHAR(10) NOT NULL,
    id_contacto         INT NULL,
    id_empleado         INT NOT NULL,

    CONSTRAINT pk_cotizacion PRIMARY KEY (nmr_cotizacion),
    CONSTRAINT ck_cotizacion_impuesto CHECK (impuesto IN ('SIN IGV', 'CON IGV')),
    CONSTRAINT ck_cotizacion_igv CHECK (porcentaje_igv >= 0),
    CONSTRAINT ck_cotizacion_vigencia CHECK (vigencia_dias > 0),
    CONSTRAINT fk_cotiz_tipo FOREIGN KEY (id_tipo_cotizacion) REFERENCES TIPO_COTIZACION (id_tipo_cotizacion),
    CONSTRAINT fk_cotiz_origen FOREIGN KEY (id_origen) REFERENCES ORIGEN_SOLICITUD (id_origen),
    CONSTRAINT fk_cotiz_moneda FOREIGN KEY (id_moneda) REFERENCES MONEDA (id_moneda),
    CONSTRAINT fk_cotiz_forma_pago FOREIGN KEY (id_forma_pago) REFERENCES FORMA_PAGO (id_forma_pago),
    CONSTRAINT fk_cotiz_estado FOREIGN KEY (id_estado) REFERENCES ESTADO_COTIZACION (id_estado),
    CONSTRAINT fk_cotiz_garantia FOREIGN KEY (id_garantia) REFERENCES GARANTIA (id_garantia),
    CONSTRAINT fk_cotiz_cliente FOREIGN KEY (cod_interno_cliente) REFERENCES CLIENTE (cod_interno) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cotiz_contacto FOREIGN KEY (id_contacto) REFERENCES CONTACTO_CLIENTE (id_contacto) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cotiz_empleado FOREIGN KEY (id_empleado) REFERENCES EMPLEADO (id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE DETALLE_COTIZACION (
    id_detalle        INT AUTO_INCREMENT NOT NULL,
    nmr_cotizacion    VARCHAR(15) NOT NULL,
    cod_pro_ser       VARCHAR(8) NOT NULL,
    item              INT NOT NULL,
    cantidad          INT NOT NULL,
    precio_unitario   DECIMAL(10,2) NOT NULL,
    alcance_tecnico   VARCHAR(300) NULL,
    CONSTRAINT pk_detalle_cotizacion PRIMARY KEY (id_detalle),
    CONSTRAINT uq_detalle_cotiz_item UNIQUE (nmr_cotizacion, item),
    CONSTRAINT chk_detalle_item CHECK (item > 0),
    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_precio CHECK (precio_unitario >= 0),
    CONSTRAINT fk_detalle_cotizacion FOREIGN KEY (nmr_cotizacion) REFERENCES COTIZACION(nmr_cotizacion) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto_servicio FOREIGN KEY (cod_pro_ser) REFERENCES PRODUCTO_SERVICIO(cod_pro_ser) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- #############################################################################
-- PARTE 2. TRIGGERS Y PROCEDIMIENTOS ALMACENADOS
-- #############################################################################
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

-- #############################################################################
-- PARTE 3. CATÁLOGOS INICIALES
-- #############################################################################
-- Catalogos iniciales necesarios para operar la aplicacion.
-- Script NO destructivo: usa INSERT IGNORE y no elimina ni trunca registros.
-- Ejecutar despues de 01_esquema.sql y 02_triggers_procedimientos.sql.
USE cotizacion;

-- Ubicacion geografica de referencia (UBIGEO).
INSERT IGNORE INTO DEPARTAMENTO (cod_ubigeo, nombre_departamento) VALUES
('04', 'Arequipa'), ('15', 'Lima'), ('18', 'Moquegua'),
('08', 'Cusco'), ('23', 'Tacna'), ('21', 'Puno');

INSERT IGNORE INTO PROVINCIA (cod_ubigeo, nombre_provincia, id_departamento)
SELECT v.cod_ubigeo, v.nombre, d.id_departamento
FROM (SELECT '0401' cod_ubigeo, 'Arequipa' nombre, '04' dep UNION ALL
      SELECT '0407', 'Islay', '04' UNION ALL
      SELECT '0405', 'Caylloma', '04' UNION ALL
      SELECT '1501', 'Lima', '15' UNION ALL
      SELECT '1801', 'Mariscal Nieto', '18' UNION ALL
      SELECT '1803', 'Ilo', '18' UNION ALL
      SELECT '0801', 'Cusco', '08' UNION ALL
      SELECT '2301', 'Tacna', '23') v
INNER JOIN DEPARTAMENTO d ON d.cod_ubigeo = v.dep;

INSERT IGNORE INTO DISTRITO (cod_ubigeo, nombre_distrito, id_provincia)
SELECT v.cod_ubigeo, v.nombre, p.id_provincia
FROM (SELECT '040101' cod_ubigeo, 'Arequipa' nombre, '0401' prov UNION ALL
      SELECT '040103', 'Cerro Colorado', '0401' UNION ALL
      SELECT '040109', 'Jose Luis Bustamante y Rivero', '0401' UNION ALL
      SELECT '040129', 'Yanahuara', '0401' UNION ALL
      SELECT '040126', 'Uchumayo', '0401' UNION ALL
      SELECT '040701', 'Mollendo', '0407' UNION ALL
      SELECT '150101', 'Lima', '1501' UNION ALL
      SELECT '150131', 'San Isidro', '1501' UNION ALL
      SELECT '150122', 'Miraflores', '1501' UNION ALL
      SELECT '180101', 'Moquegua', '1801' UNION ALL
      SELECT '180301', 'Ilo', '1803' UNION ALL
      SELECT '230101', 'Tacna', '2301') v
INNER JOIN PROVINCIA p ON p.cod_ubigeo = v.prov;

-- Catalogos de personal.
INSERT IGNORE INTO CARGO (nombre_cargo, descripcion) VALUES
('Asistente Comercial', 'Recepcion de requerimientos y emision de cotizaciones.'),
('Jefe de Proyectos', 'Supervision tecnica e ingenieria de detalle.'),
('Gerente General', 'Direccion ejecutiva.'),
('Ingeniero de Ventas', 'Levantamiento tecnico, metrados y asesoria comercial.'),
('Supervisor Tecnico', 'Control de calidad y supervision HVAC.');

INSERT IGNORE INTO ESPECIALIDAD (nombre_especialidad, descripcion, area_conocimiento, certificacion_requerida) VALUES
('Climatizacion HVAC', 'Sistemas de calefaccion, ventilacion y aire acondicionado industrial.', 'HVAC', 'HVAC-ENG'),
('Electromecanica Industrial', 'Tableros de fuerza y sistemas electromecanicos.', 'Electromecanica', 'NFE-IND'),
('Refrigeracion Industrial', 'Camaras frigorificas, chillers y cadena de frio.', 'Refrigeracion', 'ASHRAE-01'),
('Automatizacion y Control BMS', 'Controladores, sensores y telemetria.', 'Control Industrial', 'BMS-PRO');

-- Catalogos generales.
INSERT IGNORE INTO UNIDAD_MEDIDA (nombre_unidad, abreviatura) VALUES
('Unidad', 'UND'), ('Servicio', 'SERV'), ('Galon', 'GLN'),
('Pieza', 'PZA'), ('Metro Lineal', 'MTR'), ('Juego / Kit', 'JGO');

INSERT IGNORE INTO TIPO_PRODUCTO (nombre_tipo, descripcion) VALUES
('Equipo', 'Equipos y maquinaria de climatizacion y refrigeracion.'),
('Material', 'Insumos, tuberias, gases refrigerantes, cables y repuestos.'),
('Servicio', 'Servicios especializados de ingenieria, montaje y mantenimiento.');

INSERT IGNORE INTO TIPO_COTIZACION (descripcion) VALUES
('Suministro'), ('Servicio'), ('Suministro + instalacion'),
('Mantenimiento preventivo'), ('Mantenimiento correctivo'),
('Emergencia / urgente'), ('Proyecto / licitacion'),
('Directa / requerimiento'), ('Por visita tecnica');

INSERT IGNORE INTO ORIGEN_SOLICITUD (descripcion) VALUES
('Solicitud directa'), ('RFQ (Request for Quotation)'),
('Concurso o Licitacion'), ('Contrato marco'), ('Renovacion de servicio');

INSERT IGNORE INTO MONEDA (nombre, simbolo, codigo_iso) VALUES
('Dolares Americanos', '$', 'USD'), ('Soles Peruanos', 'S/.', 'PEN');

INSERT IGNORE INTO FORMA_PAGO (descripcion, dias_credito) VALUES
('Al contado', 0), ('Factura a 15 dias', 15), ('Factura a 30 dias', 30),
('Factura a 60 dias', 60), ('50% adelanto / 50% conformidad', 0);

INSERT IGNORE INTO ESTADO_COTIZACION (descripcion) VALUES
('Borrador'), ('En revision'), ('Enviada'), ('En negociacion'),
('Aprobada'), ('Rechazada'), ('Vencida');

INSERT INTO GARANTIA (tiempo_garantia, unidad_garantia)
SELECT v.tiempo, v.unidad
FROM (
    SELECT 3 AS tiempo, 'meses' AS unidad UNION ALL
    SELECT 6, 'meses' UNION ALL
    SELECT 12, 'meses' UNION ALL
    SELECT 24, 'meses'
) AS v
WHERE NOT EXISTS (
    SELECT 1 FROM GARANTIA g
    WHERE g.tiempo_garantia = v.tiempo
      AND LOWER(g.unidad_garantia) = LOWER(v.unidad)
);

-- Verificacion minima de catalogos fundamentales.
SELECT 'TIPO_PRODUCTO' tabla, COUNT(*) registros FROM TIPO_PRODUCTO
UNION ALL SELECT 'ESTADO_COTIZACION', COUNT(*) FROM ESTADO_COTIZACION
UNION ALL SELECT 'MONEDA', COUNT(*) FROM MONEDA
UNION ALL SELECT 'DISTRITO', COUNT(*) FROM DISTRITO;


-- #############################################################################
-- PARTE 4. PROCEDIMIENTOS DE REPORTES GERENCIALES
-- #############################################################################
-- =============================================================================
-- 4. PROCEDIMIENTOS ALMACENADOS DE CONSULTAS Y REPORTES GERENCIALES (10 REPORTES)
-- Empresa: J.P. Ingeniería y Servicios S.R.L.
-- Módulo: Gestión de Cotizaciones Comerciales (HVAC)
-- Gestor: MySQL 8.0+
-- =============================================================================

USE cotizacion;

DELIMITER //

-- -----------------------------------------------------------------------------
-- Reporte 01. Cotizaciones emitidas en un periodo (con cálculo Subtotal, IGV, Total)
-- Ejemplo de llamada: CALL sp_reporte_01_cotizaciones_periodo('2026-11-01', '2026-11-30');
-- Si se envía NULL, NULL lista todo el historial.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_01_cotizaciones_periodo //
CREATE PROCEDURE sp_reporte_01_cotizaciones_periodo(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    SELECT 
        c.nmr_cotizacion AS 'N° Cotización',
        c.fecha_emision AS 'Fecha Emisión',
        cl.razon_social AS 'Cliente',
        m.codigo_iso AS 'Moneda',
        COALESCE(SUM(dt.cantidad * dt.precio_unitario), 0.00) AS 'Subtotal',
        CASE 
            WHEN c.impuesto = 'CON IGV' 
            THEN ROUND(COALESCE(SUM(dt.cantidad * dt.precio_unitario), 0) * (c.porcentaje_igv / 100), 2)
            ELSE 0.00 
        END AS 'IGV',
        CASE 
            WHEN c.impuesto = 'CON IGV' 
            THEN ROUND(COALESCE(SUM(dt.cantidad * dt.precio_unitario), 0) * (1 + (c.porcentaje_igv / 100)), 2)
            ELSE COALESCE(SUM(dt.cantidad * dt.precio_unitario), 0.00)
        END AS 'Importe Total',
        ec.descripcion AS 'Estado'
    FROM COTIZACION c
    INNER JOIN CLIENTE cl ON c.cod_interno_cliente = cl.cod_interno
    INNER JOIN MONEDA m ON c.id_moneda = m.id_moneda
    INNER JOIN ESTADO_COTIZACION ec ON c.id_estado = ec.id_estado
    LEFT JOIN DETALLE_COTIZACION dt ON c.nmr_cotizacion = dt.nmr_cotizacion
    WHERE (p_fecha_inicio IS NULL OR c.fecha_emision >= p_fecha_inicio)
      AND (p_fecha_fin IS NULL OR c.fecha_emision <= p_fecha_fin)
    GROUP BY c.nmr_cotizacion, c.fecha_emision, cl.razon_social, m.codigo_iso, c.impuesto, c.porcentaje_igv, ec.descripcion
    ORDER BY c.fecha_emision DESC, c.nmr_cotizacion DESC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 02. Embudo comercial: Cotizaciones según su estado y participación %
-- Ejemplo de llamada: CALL sp_reporte_02_embudo_comercial();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_02_embudo_comercial //
CREATE PROCEDURE sp_reporte_02_embudo_comercial()
BEGIN
    SELECT 
        ec.descripcion AS 'Estado de Cotización',
        COUNT(c.nmr_cotizacion) AS 'Total Cotizaciones',
        CONCAT(
            ROUND(COUNT(c.nmr_cotizacion) * 100.0 / NULLIF((SELECT COUNT(*) FROM COTIZACION), 0), 1),
            '%'
        ) AS 'Participación'
    FROM ESTADO_COTIZACION ec
    LEFT JOIN COTIZACION c ON ec.id_estado = c.id_estado
    WHERE ec.estado = 'Activo'
    GROUP BY ec.id_estado, ec.descripcion
    ORDER BY ec.id_estado ASC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 03. Ranking de clientes con más cotizaciones y tasa de aprobación
-- Ejemplo de llamada: CALL sp_reporte_03_ranking_clientes();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_03_ranking_clientes //
CREATE PROCEDURE sp_reporte_03_ranking_clientes()
BEGIN
    SELECT 
        cl.cod_interno AS 'Código',
        cl.ruc AS 'RUC',
        cl.razon_social AS 'Razón Social',
        COUNT(c.nmr_cotizacion) AS 'Total Solicitadas',
        SUM(CASE WHEN c.id_estado = 5 THEN 1 ELSE 0 END) AS 'Aprobadas',
        CONCAT(
            ROUND(SUM(CASE WHEN c.id_estado = 5 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(c.nmr_cotizacion), 0), 1),
            '%'
        ) AS 'Efectividad Cierre'
    FROM CLIENTE cl
    LEFT JOIN COTIZACION c ON cl.cod_interno = c.cod_interno_cliente
    WHERE cl.estado = 'Activo'
    GROUP BY cl.cod_interno, cl.ruc, cl.razon_social
    ORDER BY COUNT(c.nmr_cotizacion) DESC, SUM(CASE WHEN c.id_estado = 5 THEN 1 ELSE 0 END) DESC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 04. Top productos y servicios más cotizados (Demanda de catálogo)
-- Ejemplo de llamada: CALL sp_reporte_04_top_productos_servicios();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_04_top_productos_servicios //
CREATE PROCEDURE sp_reporte_04_top_productos_servicios()
BEGIN
    SELECT 
        ps.cod_pro_ser AS 'Código',
        ps.Descripcion AS 'Descripción del Ítem',
        tp.nombre_tipo AS 'Categoría',
        um.abreviatura AS 'Unidad',
        COUNT(DISTINCT dt.nmr_cotizacion) AS 'Veces Cotizado',
        SUM(dt.cantidad) AS 'Cantidad Total',
        SUM(dt.cantidad * dt.precio_unitario) AS 'Monto Acumulado (Ref.)'
    FROM DETALLE_COTIZACION dt
    INNER JOIN PRODUCTO_SERVICIO ps ON dt.cod_pro_ser = ps.cod_pro_ser
    INNER JOIN TIPO_PRODUCTO tp ON ps.id_tipo = tp.id_tipo
    INNER JOIN UNIDAD_MEDIDA um ON ps.id_unidad = um.id_unidad
    GROUP BY ps.cod_pro_ser, ps.Descripcion, tp.nombre_tipo, um.abreviatura
    ORDER BY COUNT(DISTINCT dt.nmr_cotizacion) DESC, SUM(dt.cantidad) DESC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 05. Alerta comercial: Cotizaciones enviadas próximas a vencer
-- Ejemplo de llamada: CALL sp_reporte_05_cotizaciones_por_vencer();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_05_cotizaciones_por_vencer //
CREATE PROCEDURE sp_reporte_05_cotizaciones_por_vencer()
BEGIN
    SELECT 
        c.nmr_cotizacion AS 'N° Cotización',
        cl.razon_social AS 'Cliente',
        COALESCE(cc.nombre_contacto, 'Sin contacto asignado') AS 'Contacto',
        c.fecha_emision AS 'Fecha Emisión',
        c.vigencia_dias AS 'Vigencia (Días)',
        DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY) AS 'Fecha Vencimiento',
        DATEDIFF(DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY), CURDATE()) AS 'Días Restantes',
        e.nombre_completo AS 'Ejecutivo Responsable'
    FROM COTIZACION c
    INNER JOIN CLIENTE cl ON c.cod_interno_cliente = cl.cod_interno
    LEFT JOIN CONTACTO_CLIENTE cc ON c.id_contacto = cc.id_contacto
    INNER JOIN EMPLEADO e ON c.id_empleado = e.id_empleado
    WHERE c.id_estado = 3 -- Estado: Enviada
      AND DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY) >= CURDATE()
    ORDER BY DATEDIFF(DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY), CURDATE()) ASC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 06. Seguimiento: Cotizaciones pendientes de respuesta (En revisión / Enviada)
-- Ejemplo de llamada: CALL sp_reporte_06_cotizaciones_pendientes();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_06_cotizaciones_pendientes //
CREATE PROCEDURE sp_reporte_06_cotizaciones_pendientes()
BEGIN
    SELECT 
        c.nmr_cotizacion AS 'N° Cotización',
        c.fecha_emision AS 'Fecha Emisión',
        cl.razon_social AS 'Cliente',
        COALESCE(cc.nombre_contacto, 'No especificado') AS 'Contacto Directo',
        COALESCE(cc.telefono_contacto, '-') AS 'Teléfono Contacto',
        COALESCE(cc.email_contacto, '-') AS 'Correo Contacto',
        e.nombre_completo AS 'Responsable Interno',
        ec.descripcion AS 'Estado Actual'
    FROM COTIZACION c
    INNER JOIN CLIENTE cl ON c.cod_interno_cliente = cl.cod_interno
    LEFT JOIN CONTACTO_CLIENTE cc ON c.id_contacto = cc.id_contacto
    INNER JOIN EMPLEADO e ON c.id_empleado = e.id_empleado
    INNER JOIN ESTADO_COTIZACION ec ON c.id_estado = ec.id_estado
    WHERE c.id_estado IN (2, 3) -- 2: En revisión, 3: Enviada
    ORDER BY c.fecha_emision ASC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 07. Evolución financiera: Montos cotizados y aprobados por mes y moneda
-- Ejemplo de llamada: CALL sp_reporte_07_evolucion_financiera_mensual();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_07_evolucion_financiera_mensual //
CREATE PROCEDURE sp_reporte_07_evolucion_financiera_mensual()
BEGIN
    SELECT 
        DATE_FORMAT(c.fecha_emision, '%Y-%m') AS 'Periodo (Año-Mes)',
        m.codigo_iso AS 'Moneda',
        COUNT(DISTINCT c.nmr_cotizacion) AS 'Total Cotizaciones',
        SUM(dt.cantidad * dt.precio_unitario) AS 'Subtotal Cotizado',
        SUM(CASE WHEN c.id_estado = 5 THEN dt.cantidad * dt.precio_unitario ELSE 0.00 END) AS 'Subtotal Aprobado'
    FROM COTIZACION c
    INNER JOIN MONEDA m ON c.id_moneda = m.id_moneda
    INNER JOIN DETALLE_COTIZACION dt ON c.nmr_cotizacion = dt.nmr_cotizacion
    GROUP BY DATE_FORMAT(c.fecha_emision, '%Y-%m'), m.codigo_iso
    ORDER BY DATE_FORMAT(c.fecha_emision, '%Y-%m') DESC, m.codigo_iso ASC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 08. Desempeño comercial: Cotizaciones y cierres por empleado
-- Ejemplo de llamada: CALL sp_reporte_08_desempeno_empleados();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_08_desempeno_empleados //
CREATE PROCEDURE sp_reporte_08_desempeno_empleados()
BEGIN
    SELECT 
        e.DNI AS 'DNI',
        e.nombre_completo AS 'Responsable Comercial',
        car.nombre_cargo AS 'Cargo',
        esp.nombre_especialidad AS 'Especialidad',
        COUNT(c.nmr_cotizacion) AS 'Cotizaciones Elaboradas',
        SUM(CASE WHEN c.id_estado = 5 THEN 1 ELSE 0 END) AS 'Cotizaciones Aprobadas',
        CONCAT(
            ROUND(SUM(CASE WHEN c.id_estado = 5 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(c.nmr_cotizacion), 0), 1),
            '%'
        ) AS 'Tasa de Éxito'
    FROM EMPLEADO e
    INNER JOIN CARGO car ON e.id_cargo = car.id_cargo
    INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
    LEFT JOIN COTIZACION c ON e.id_empleado = c.id_empleado
    WHERE e.estado = 'Activo'
    GROUP BY e.id_empleado, e.DNI, e.nombre_completo, car.nombre_cargo, esp.nombre_especialidad
    ORDER BY COUNT(c.nmr_cotizacion) DESC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 09. Ventas cerradas: Cotizaciones aprobadas por cliente y moneda
-- Ejemplo de llamada: CALL sp_reporte_09_ventas_cerradas_cliente();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_09_ventas_cerradas_cliente //
CREATE PROCEDURE sp_reporte_09_ventas_cerradas_cliente()
BEGIN
    SELECT 
        cl.ruc AS 'RUC Cliente',
        cl.razon_social AS 'Razón Social',
        m.codigo_iso AS 'Moneda',
        COUNT(DISTINCT c.nmr_cotizacion) AS 'Cotizaciones Aprobadas',
        SUM(dt.cantidad * dt.precio_unitario) AS 'Subtotal Aprobado',
        SUM(
            CASE 
                WHEN c.impuesto = 'CON IGV' 
                THEN ROUND((dt.cantidad * dt.precio_unitario) * (1 + (c.porcentaje_igv / 100)), 2)
                ELSE (dt.cantidad * dt.precio_unitario)
            END
        ) AS 'Monto Total Facturable'
    FROM CLIENTE cl
    INNER JOIN COTIZACION c ON cl.cod_interno = c.cod_interno_cliente
    INNER JOIN MONEDA m ON c.id_moneda = m.id_moneda
    INNER JOIN DETALLE_COTIZACION dt ON c.nmr_cotizacion = dt.nmr_cotizacion
    WHERE c.id_estado = 5 -- Estado: Aprobada
    GROUP BY cl.ruc, cl.razon_social, m.codigo_iso
    ORDER BY cl.razon_social ASC, m.codigo_iso ASC;
END //


-- -----------------------------------------------------------------------------
-- Reporte 10. Demanda por línea de negocio: Cotizaciones por tipo de trabajo
-- Ejemplo de llamada: CALL sp_reporte_10_demanda_tipo_trabajo();
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_10_demanda_tipo_trabajo //
CREATE PROCEDURE sp_reporte_10_demanda_tipo_trabajo()
BEGIN
    SELECT 
        tc.id_tipo_cotizacion AS 'ID',
        tc.descripcion AS 'Tipo de Cotización / Servicio',
        COUNT(DISTINCT c.nmr_cotizacion) AS 'Cantidad Cotizaciones',
        SUM(CASE WHEN c.id_estado = 5 THEN 1 ELSE 0 END) AS 'Aprobadas',
        CONCAT(
            ROUND(COUNT(DISTINCT c.nmr_cotizacion) * 100.0 / NULLIF((SELECT COUNT(*) FROM COTIZACION), 0), 1),
            '%'
        ) AS 'Participación %'
    FROM TIPO_COTIZACION tc
    LEFT JOIN COTIZACION c ON tc.id_tipo_cotizacion = c.id_tipo_cotizacion
    WHERE tc.estado = 'Activo'
    GROUP BY tc.id_tipo_cotizacion, tc.descripcion
    ORDER BY COUNT(DISTINCT c.nmr_cotizacion) DESC;
END //

DELIMITER ;

-- #############################################################################
-- PARTE 5. USUARIO DE LA APLICACIÓN (OPCIONAL)
-- Descomentar las 3 sentencias y cambiar la contraseña antes de ejecutar.
-- #############################################################################
-- Plantilla opcional para crear un usuario MySQL de aplicacion con privilegios limitados.
-- Sustituye la contrasena de ejemplo antes de ejecutar. No guardes la contrasena en el proyecto.
-- Ejecutar como administrador de MySQL despues de crear esquema, rutinas y catalogos.

-- CREATE USER IF NOT EXISTS 'jp_app'@'127.0.0.1' IDENTIFIED BY 'CAMBIAR_POR_UNA_CONTRASENA_LARGA_Y_UNICA';
-- GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON cotizacion.* TO 'jp_app'@'127.0.0.1';
-- FLUSH PRIVILEGES;

-- La aplicacion usa host 127.0.0.1 por defecto. Ajusta el host de esta cuenta si usas otro
-- nombre/IP en config/database.ini. Para conexion desde otra PC, crea una cuenta
-- restringida a la IP o red exacta que corresponda.
-- Evita usar '%' si no es necesario y nunca expongas MySQL directamente a Internet.
