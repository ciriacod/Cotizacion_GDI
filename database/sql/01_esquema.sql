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