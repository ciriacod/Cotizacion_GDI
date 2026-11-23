-- =============================================================================
-- 3. SCRIPT DE INSERCIÓN DE DATOS INICIALES Y PRUEBAS ROBUSTAS (SEED DATA)
-- Empresa: J.P. Ingeniería y Servicios S.R.L.
-- Módulo: Gestión de Cotizaciones Comerciales (HVAC)
-- Gestor: MySQL 8.0+
-- =============================================================================

USE cotizacion;

SET FOREIGN_KEY_CHECKS = 0;

-- Limpiar tablas y reiniciar contadores AUTO_INCREMENT a 1
TRUNCATE TABLE DETALLE_COTIZACION;
TRUNCATE TABLE COTIZACION;
TRUNCATE TABLE CONTACTO_CLIENTE;
TRUNCATE TABLE CLIENTE;
TRUNCATE TABLE DISTRITO;
TRUNCATE TABLE PROVINCIA;
TRUNCATE TABLE DEPARTAMENTO;
TRUNCATE TABLE PRODUCTO;
TRUNCATE TABLE SERVICIO;
TRUNCATE TABLE PRODUCTO_SERVICIO;
TRUNCATE TABLE EMPLEADO;
TRUNCATE TABLE CARGO;
TRUNCATE TABLE ESPECIALIDAD;
TRUNCATE TABLE TIPO_COTIZACION;
TRUNCATE TABLE ORIGEN_SOLICITUD;
TRUNCATE TABLE MONEDA;
TRUNCATE TABLE FORMA_PAGO;
TRUNCATE TABLE ESTADO_COTIZACION;
TRUNCATE TABLE GARANTIA;
TRUNCATE TABLE UNIDAD_MEDIDA;
TRUNCATE TABLE TIPO_PRODUCTO;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. UBICACIÓN GEOGRÁFICA (IDs Autoincrementales + Código UBIGEO Oficial)
-- -----------------------------------------------------------------------------

INSERT INTO DEPARTAMENTO (cod_ubigeo, nombre_departamento) VALUES 
('04', 'Arequipa'),    -- ID 1
('15', 'Lima'),        -- ID 2
('18', 'Moquegua'),    -- ID 3
('08', 'Cusco'),       -- ID 4
('23', 'Tacna'),       -- ID 5
('21', 'Puno');        -- ID 6

INSERT INTO PROVINCIA (cod_ubigeo, nombre_provincia, id_departamento) VALUES 
('0401', 'Arequipa', 1),       -- ID 1
('0407', 'Islay', 1),          -- ID 2
('0405', 'Caylloma', 1),       -- ID 3
('1501', 'Lima', 2),           -- ID 4
('1801', 'Mariscal Nieto', 3), -- ID 5
('1803', 'Ilo', 3),            -- ID 6
('0801', 'Cusco', 4),          -- ID 7
('2301', 'Tacna', 5);          -- ID 8

INSERT INTO DISTRITO (cod_ubigeo, nombre_distrito, id_provincia) VALUES 
('040101', 'Arequipa', 1),                       -- ID 1
('040103', 'Cerro Colorado', 1),                 -- ID 2
('040109', 'José Luis Bustamante y Rivero', 1),  -- ID 3
('040129', 'Yanahuara', 1),                      -- ID 4
('040126', 'Uchumayo', 1),                       -- ID 5
('040701', 'Mollendo', 2),                       -- ID 6
('150101', 'Lima', 4),                           -- ID 7
('150131', 'San Isidro', 4),                     -- ID 8
('150122', 'Miraflores', 4),                     -- ID 9
('180101', 'Moquegua', 5),                       -- ID 10
('180301', 'Ilo', 6),                            -- ID 11
('230101', 'Tacna', 8);                          -- ID 12

-- -----------------------------------------------------------------------------
-- 2. CARGOS, ESPECIALIDADES Y EMPLEADOS (Con password_hash para login)
-- -----------------------------------------------------------------------------

INSERT INTO CARGO (nombre_cargo, descripcion) VALUES 
('Asistente Comercial', 'Encargada de la recepción de requerimientos y emisión de cotizaciones.'), -- ID 1
('Jefe de Proyectos', 'Supervisión técnica, ingeniería de detalle y ejecución HVAC.'),            -- ID 2
('Gerente General', 'Dirección ejecutiva y aprobación final de licitaciones.'),                  -- ID 3
('Ingeniero de Ventas', 'Levantamiento técnico en campo, metrados y asesoría comercial.'),       -- ID 4
('Supervisor Técnico', 'Control de calidad, mantenimiento preventivo y puesta en marcha.');      -- ID 5

INSERT INTO ESPECIALIDAD (nombre_especialidad, descripcion, area_conocimiento, certificacion_requerida) VALUES 
('Climatización HVAC', 'Sistemas de calefacción, ventilación y aire acondicionado industrial.', 'HVAC', 'HVAC-ENG'),                 -- ID 1
('Electromecánica Industrial', 'Tableros de fuerza, variadores y sistemas electromecánicos.', 'Electromecánica', 'NFE-IND'),       -- ID 2
('Refrigeración Industrial', 'Cámaras frigoríficas, chillers y cadena de frío.', 'Refrigeración', 'ASHRAE-01'),                    -- ID 3
('Automatización y Control BMS', 'Controladores electrónicos, sensores y telemetría.', 'Control Industrial', 'BMS-PRO');            -- ID 4

-- Nota: Los hashes corresponden a contraseñas encriptadas (formato bcrypt)
CALL sp_crear_empleado('72345678', 'Noelia Gonzales Huertas', 'noelia.gonzales@jpingenieria.pe', '$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '946328208', 1, 1); -- ID 1
CALL sp_crear_empleado('45123456', 'Juan Pérez Gómez', 'jperez@jpingenieria.pe', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '997114002', 2, 1);         -- ID 2
CALL sp_crear_empleado('40123456', 'Carlos Valdivia Salas', 'cvaldivia@jpingenieria.pe', '$2b$10$TKh8H1.PfQx37YgCzwiKb.KjNyWgaHb9cbcoQgdIVFlYg7B77UdFm', '987123456', 3, 2); -- ID 3
CALL sp_crear_empleado('71889900', 'Lucía Fernanda Torres', 'ltorres@jpingenieria.pe', '$2b$10$CwTycUXWue0Thq9StjUM0uJ8.1m4nO.Z8Q2t5x1v7y9w3e5r7t9y1', '951223344', 4, 3); -- ID 4
CALL sp_crear_empleado('43219876', 'Roberto Mendoza Díaz', 'rmendoza@jpingenieria.pe', '$2b$10$H8s7d6f5g4h3j2k1l0z9x8c7v6b5n4m3q2w1e4r5t6y7u8i9o0p1a', '963852741', 4, 2); -- ID 5
CALL sp_crear_empleado('46781234', 'Diego Armando Paredes', 'dparedes@jpingenieria.pe', '$2b$10$A1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6q7w8e9r0t1y2u3i4o5p6q', '958741236', 5, 4); -- ID 6
CALL sp_crear_empleado('74556677', 'Valeria Chávez Huamán', 'vchavez@jpingenieria.pe', '$2b$10$Z9x8c7v6b5n4m3a2s1d4f5g6h7j8k9l0q1w2e3r4t5y6u7i8o9p0z', '959112233', 1, 4); -- ID 7

-- -----------------------------------------------------------------------------
-- 3. CATÁLOGOS DE PRODUCTOS Y SERVICIOS (22 Ítems: Equipos, Materiales, Servicios)
-- -----------------------------------------------------------------------------

INSERT INTO UNIDAD_MEDIDA (nombre_unidad, abreviatura) VALUES 
('Unidad', 'UND'),        -- ID 1
('Servicio', 'SERV'),     -- ID 2
('Galón', 'GLN'),         -- ID 3
('Pieza', 'PZA'),         -- ID 4
('Metro Lineal', 'MTR'),  -- ID 5
('Juego / Kit', 'JGO');   -- ID 6

INSERT INTO TIPO_PRODUCTO (nombre_tipo, descripcion) VALUES 
('Equipo', 'Equipos y maquinaria mayor de climatización y refrigeración.'),     -- ID 1 -> Prefijo EQU
('Material', 'Insumos, tuberías, gases refrigerantes, cables y repuestos.'),    -- ID 2 -> Prefijo MAT
('Servicio', 'Servicios especializados de ingeniería, montaje y mantenimiento.'); -- ID 3 -> Prefijo SER

-- 10 Equipos (id_tipo = 1 -> EQU08601 a EQU08610)
CALL sp_crear_producto_servicio('COMPRESOR HERMÉTICO SCROLL 5HP R410A', 1, 1, 2500.00);             -- EQU08601
CALL sp_crear_producto_servicio('DISPLAY REMOTO CON 6 TECLAS CX660', 1, 1, 133.00);                 -- EQU08602
CALL sp_crear_producto_servicio('CONTROLADOR ELECTRÓNICO DIXELL XM679K 503 C3', 1, 1, 966.00);      -- EQU08603
CALL sp_crear_producto_servicio('BOBINA SOLENOIDE EMERSON 230VAC 50/60HZ 17VA', 1, 1, 136.00);      -- EQU08604
CALL sp_crear_producto_servicio('VÁLVULA DE EXPANSIÓN ELECTRÓNICA 3/8 X 1/2', 1, 1, 544.00);        -- EQU08605
CALL sp_crear_producto_servicio('SENSOR TUBERÍA DE COBRE PT1000 PMP4-67', 1, 1, 149.60);            -- EQU08606
CALL sp_crear_producto_servicio('UNIDAD EVAPORADORA INDUSTRIAL 10 TR', 1, 1, 4200.00);              -- EQU08607
CALL sp_crear_producto_servicio('CHILLER ENFRIADO POR AIRE 30 TR ALTA EFICIENCIA', 1, 1, 18500.00);  -- EQU08608
CALL sp_crear_producto_servicio('CORTINA DE AIRE INDUSTRIAL 1.50M CON CONTROL', 1, 1, 680.00);      -- EQU08609
CALL sp_crear_producto_servicio('EXTRACTOR CENTRÍFUGO DE AIRE 3HP TRIFÁSICO', 1, 1, 1450.00);        -- EQU08610

-- 7 Materiales (id_tipo = 2 -> MAT1901 a MAT1907)
CALL sp_crear_producto_servicio('CONECTOR ELÉCTRICO P/BOBINA PS-29864-6ASC-N30', 1, 2, 30.60);     -- MAT1901
CALL sp_crear_producto_servicio('SONDA TEMPERATURA NTC P/REGULACIÓN Y DESHIELO', 1, 2, 39.44);      -- MAT1902
CALL sp_crear_producto_servicio('TRANSDUCTOR DE PRESIÓN C/P BE07930200 PPR15 PA-2', 1, 2, 224.40); -- MAT1903
CALL sp_crear_producto_servicio('TUBERÍA DE COBRE RÍGIDA TIPO L 3/4 PULGADA', 5, 2, 45.00);        -- MAT1904
CALL sp_crear_producto_servicio('CILINDRO GAS REFRIGERANTE ECOLÓGICO R410A (11.3 KG)', 1, 2, 480.00);-- MAT1905
CALL sp_crear_producto_servicio('AISLAMIENTO TÉRMICO ELASTOMÉRICO 3/4 X 1/2', 5, 2, 14.50);        -- MAT1906
CALL sp_crear_producto_servicio('KIT FILTROS SECADORES Y MIRILLA LÍQUIDO 1/2', 6, 2, 165.00);       -- MAT1907

-- 5 Servicios (id_tipo = 3 -> SER0001 a SER0005)
CALL sp_crear_producto_servicio('SERVICIO DE MANTENIMIENTO PREVENTIVO SISTEMA HVAC', 2, 3, 350.00); -- SER0001
CALL sp_crear_producto_servicio('SERVICIO DE INSTALACIÓN Y PUESTA EN MARCHA', 2, 3, 1200.00);       -- SER0002
CALL sp_crear_producto_servicio('DIAGNÓSTICO TÉCNICO, VACÍO Y CARGA DE REFRIGERANTE', 2, 3, 280.00);-- SER0003
CALL sp_crear_producto_servicio('FABRICACIÓN Y MONTAJE DE DUCTERÍA GALVANIZADA', 5, 3, 95.00);      -- SER0004
CALL sp_crear_producto_servicio('AUTOMATIZACIÓN E INTEGRACIÓN A SISTEMA BMS', 2, 3, 1850.00);       -- SER0005

-- Especialización Subtipos 1:1
INSERT INTO PRODUCTO (cod_pro_ser, marca, modelo, año, nmr_parte) VALUES 
('EQU08601', 'DANFOSS', 'SCROLL-5HP', '2025', 'DAN-5H-01'),
('EQU08602', 'DIXELL', 'CX660', '2025', 'DX660-6K'),
('EQU08603', 'DIXELL', 'XM679K 503 C3', '2025', 'XM679K-503'),
('EQU08604', 'EMERSON', '230VAC', '2024', 'EM-230V-17'),
('EQU08605', 'ALCO', '3/8 X 1/2', '2025', 'ALC-EEV-38'),
('EQU08606', 'PMP', 'PT 1000', '2024', 'PMP-PT1000'),
('EQU08607', 'CARRIER', '40RU-10TR', '2026', 'CAR-40RU-10'),
('EQU08608', 'TRANE', 'CGAM-030', '2026', 'TRN-CGAM-30'),
('EQU08609', 'SOLER & PALAU', 'COR-1500N', '2025', 'SP-COR1500'),
('EQU08610', 'SODECA', 'CMP-928-2T', '2025', 'SOD-CMP928'),
('MAT1901', 'PS', 'PS-29864', '2024', 'PS-29864-6'),
('MAT1902', 'NTC', 'REGULACION', '2025', 'NTC-REG-01'),
('MAT1903', 'BE', 'BE07930200', '2025', 'BE-PPR15-PA2'),
('MAT1904', 'NACOBRE', 'TIPO-L-34', '2026', 'NAC-CU-34'),
('MAT1905', 'HONEYWELL', 'GENETRON-410A', '2026', 'HON-R410A-11'),
('MAT1906', 'ARMACELL', 'ARMAFLEX-34', '2025', 'ARM-3412-2M'),
('MAT1907', 'SPORLAN', 'C-164-S-HH', '2025', 'SPO-KIT-164');

INSERT INTO SERVICIO (cod_pro_ser) VALUES 
('SER0001'), ('SER0002'), ('SER0003'), ('SER0004'), ('SER0005');

-- -----------------------------------------------------------------------------
-- 4. PARÁMETROS Y CATÁLOGOS DE COTIZACIÓN
-- -----------------------------------------------------------------------------

INSERT INTO TIPO_COTIZACION (descripcion) VALUES 
('Suministro'),               -- ID 1
('Servicio'),                 -- ID 2
('Suministro + instalación'), -- ID 3
('Mantenimiento preventivo'), -- ID 4
('Mantenimiento correctivo'), -- ID 5
('Emergencia / urgente'),     -- ID 6
('Proyecto / licitación'),    -- ID 7
('Directa / requerimiento'),  -- ID 8
('Por visita técnica');       -- ID 9

INSERT INTO ORIGEN_SOLICITUD (descripcion) VALUES 
('Solicitud directa'),           -- ID 1
('RFQ (Request for Quotation)'), -- ID 2
('Concurso o Licitación'),       -- ID 3
('Contrato marco'),              -- ID 4
('Renovación de servicio');      -- ID 5

INSERT INTO MONEDA (nombre, simbolo, codigo_iso) VALUES 
('Dólares Americanos', '$', 'USD'), -- ID 1
('Soles Peruanos', 'S/.', 'PEN');    -- ID 2

INSERT INTO FORMA_PAGO (descripcion, dias_credito) VALUES 
('Al contado', 0),                    -- ID 1
('Factura a 15 días', 15),            -- ID 2
('Factura a 30 días', 30),            -- ID 3
('Factura a 60 días', 60),            -- ID 4
('50% adelanto / 50% conformidad', 0);-- ID 5

INSERT INTO ESTADO_COTIZACION (descripcion) VALUES 
('Borrador'),       -- ID 1
('En revisión'),    -- ID 2
('Enviada'),        -- ID 3
('En negociación'), -- ID 4
('Aprobada'),       -- ID 5
('Rechazada'),      -- ID 6
('Vencida');        -- ID 7

INSERT INTO GARANTIA (tiempo_garantia, unidad_garantia) VALUES 
(3, 'meses'),  -- ID 1
(6, 'meses'),  -- ID 2
(12, 'meses'), -- ID 3
(24, 'meses'); -- ID 4

-- -----------------------------------------------------------------------------
-- 5. CLIENTES (12 Empresas) Y CONTACTOS (16 Personas)
-- -----------------------------------------------------------------------------

CALL sp_crear_cliente('20602039464', 'GRS CONSTRUCTORES SOCIEDAD ANONIMA CERRADA', 'Av. Industrial 125', 3);             -- CLI001
CALL sp_crear_cliente('20498189637', 'EMPRESA MINERA ABC S.A.C.', 'Panamericana Sur Km 6', 1);                             -- CLI002
CALL sp_crear_cliente('20556677889', 'INVERSIONES INDUSTRIALES SUR S.A.C.', 'Calle Los Talleres 450', 2);                -- CLI003
CALL sp_crear_cliente('20112233445', 'CONSTRUCTORA E INMOBILIARIA ANDINA S.A.', 'Av. Javier Prado Este 1200', 8);         -- CLI004
CALL sp_crear_cliente('20455112233', 'SOCIEDAD MINERA CERRO VERDE S.A.A.', 'Carretera Variante Tinajones Km 25', 5);      -- CLI005
CALL sp_crear_cliente('20334455667', 'CORPORACION PESQUERA DEL SUR S.A.', 'Av. Las Industrias 890', 6);                   -- CLI006
CALL sp_crear_cliente('20778899001', 'AGROINDUSTRIAS DEL VALLE S.A.C.', 'Parque Industrial Mz. D Lt. 12', 10);           -- CLI007
CALL sp_crear_cliente('20100190797', 'LECHE GLORIA SOCIEDAD ANONIMA - GLORIA S.A.', 'Av. General Diez Canseco 527', 1);   -- CLI008
CALL sp_crear_cliente('20370146994', 'CORPORACION ACEROS AREQUIPA S.A.', 'Variante de Uchumayo Km 4.5', 5);              -- CLI009
CALL sp_crear_cliente('20454211988', 'CLINICA SAN JUAN DE DIOS AREQUIPA', 'Av. Ejército 1020', 4);                        -- CLI010
CALL sp_crear_cliente('20532710066', 'ANGLO AMERICAN QUELLAVECO S.A.', 'Campamento Minero Quellaveco s/n', 10);          -- CLI011
CALL sp_crear_cliente('20410567891', 'TERMINAL PORTUARIO DEL SUR S.A.C.', 'Zona Industrial Puerto Ilo Lt. 4', 11);        -- CLI012

-- Contactos (IDs autogenerados del 1 al 16)
CALL sp_crear_contacto_cliente('CLI001', 'Esteban Nilo', '987654321', 'esteban.nilo@grsconstructores.com');     -- ID 1
CALL sp_crear_contacto_cliente('CLI001', 'Patricia Ramos', '987112233', 'pramos@grsconstructores.com');          -- ID 2
CALL sp_crear_contacto_cliente('CLI002', 'Carlos Rodríguez', '954123456', 'crodriguez@mineraabc.pe');            -- ID 3
CALL sp_crear_contacto_cliente('CLI002', 'Valeria Gómez', '954998877', 'vgomez@mineraabc.pe');                   -- ID 4
CALL sp_crear_contacto_cliente('CLI003', 'Mariana Paz', '978112233', 'mpaz@iisur.pe');                           -- ID 5
CALL sp_crear_contacto_cliente('CLI004', 'Jorge Quispe', '965443322', 'jquispe@andina.com');                     -- ID 6
CALL sp_crear_contacto_cliente('CLI005', 'Ing. Fernando Salas', '958112244', 'fsalas@cerroverde.pe');            -- ID 7
CALL sp_crear_contacto_cliente('CLI005', 'Ing. Héctor Aguilar', '958776655', 'haguilar@cerroverde.pe');          -- ID 8
CALL sp_crear_contacto_cliente('CLI006', 'Ricardo Paredes', '953667788', 'rparedes@pesquerasur.com');            -- ID 9
CALL sp_crear_contacto_cliente('CLI007', 'Claudia Mamani', '952441100', 'cmamani@agrovalle.pe');                 -- ID 10
CALL sp_crear_contacto_cliente('CLI008', 'Ing. Martín Delgado', '959887766', 'mdelgado@gloria.com.pe');          -- ID 11
CALL sp_crear_contacto_cliente('CLI008', 'Sofía Llerena', '959334455', 'sllerena@gloria.com.pe');                -- ID 12
CALL sp_crear_contacto_cliente('CLI009', 'Gonzalo Benavides', '951998877', 'gbenavides@aasa.com.pe');            -- ID 13
CALL sp_crear_contacto_cliente('CLI010', 'Dra. Carmen Villalobos', '957665544', 'cvillalobos@csjd.pe');          -- ID 14
CALL sp_crear_contacto_cliente('CLI011', 'Ing. Óscar Zegarra', '953112299', 'oscar.zegarra@angloamerican.com');  -- ID 15
CALL sp_crear_contacto_cliente('CLI012', 'Paola Bustamante', '952998811', 'pbustamante@tpsur.pe');               -- ID 16

-- -----------------------------------------------------------------------------
-- 6. COTIZACIONES MÚLTIPLES (26 Cotizaciones entre Junio y Noviembre 2026)
-- -----------------------------------------------------------------------------

-- === JUNIO 2026 ===
CALL sp_crear_cotizacion('2026-06-10', 3, 2, 1, 'CON IGV', 18.00, 3, 3, '20 días', '10 días', 15, 'Obra civil no incluida', 'Climatización sala eléctrica', 'CLI005', 7, 2); -- JP.260600001
CALL sp_actualizar_estado_cotizacion('JP.260600001', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-06-22', 4, 4, 2, 'CON IGV', 18.00, 2, 2, '5 días', '2 días', 15, 'Repuestos mayores aparte', 'Mantenimiento planta leche evaporada', 'CLI008', 11, 4); -- JP.260600002
CALL sp_actualizar_estado_cotizacion('JP.260600002', 5); -- Aprobada

-- === JULIO 2026 ===
CALL sp_crear_cotizacion('2026-07-08', 7, 3, 1, 'CON IGV', 18.00, 5, 4, '35 días', '15 días', 30, 'Andamios a cargo del cliente', 'Licitación cámaras de congelado', 'CLI006', 9, 3); -- JP.260700003
CALL sp_actualizar_estado_cotizacion('JP.260700003', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-07-19', 1, 1, 2, 'SIN IGV', 18.00, 1, 3, '7 días', '3 días', 10, 'Sin instalación', 'Suministro repuestos Dixell', 'CLI009', 13, 1); -- JP.260700004
CALL sp_actualizar_estado_cotizacion('JP.260700004', 7); -- Vencida

CALL sp_crear_cotizacion('2026-07-28', 5, 1, 2, 'CON IGV', 18.00, 2, 2, '4 días', '1 día', 15, 'Ninguna', 'Reparación urgente sala servidores', 'CLI010', 14, 5); -- JP.260700005
CALL sp_actualizar_estado_cotizacion('JP.260700005', 5); -- Aprobada

-- === AGOSTO 2026 ===
CALL sp_crear_cotizacion('2026-08-05', 2, 1, 2, 'SIN IGV', 18.00, 1, 1, '2 días', '1 día', 5, 'Ninguna', 'Cotización de emergencia no respondida', 'CLI002', 3, 1); -- JP.260800006
CALL sp_actualizar_estado_cotizacion('JP.260800006', 7); -- Vencida

CALL sp_crear_cotizacion('2026-08-18', 4, 4, 1, 'CON IGV', 18.00, 3, 3, '7 días', '3 días', 15, 'No incluye repuestos mayores', 'Mantenimiento trimestral concentradora', 'CLI005', 8, 2); -- JP.260800007
CALL sp_actualizar_estado_cotizacion('JP.260800007', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-08-24', 3, 2, 1, 'CON IGV', 18.00, 4, 4, '30 días', '12 días', 20, 'Permisos portuarios a cargo del cliente', 'Sistema extracción almacén graneles', 'CLI012', 16, 4); -- JP.260800008
CALL sp_actualizar_estado_cotizacion('JP.260800008', 6); -- Rechazada

CALL sp_crear_cotizacion('2026-08-29', 3, 2, 2, 'SIN IGV', 18.00, 1, 3, '10 días', '10 días', 7, 'Trabajos eléctricos no incluidos', 'Servicio sujeto a visita técnica', 'CLI001', 1, 1); -- JP.260800009
CALL sp_actualizar_estado_cotizacion('JP.260800009', 5); -- Aprobada

-- === SEPTIEMBRE 2026 ===
CALL sp_crear_cotizacion('2026-09-04', 7, 3, 1, 'CON IGV', 18.00, 5, 4, '45 días', '20 días', 30, 'Subestación eléctrica no incluida', 'Proyecto Chiller 30 TR Campamento', 'CLI011', 15, 3); -- JP.260900010
CALL sp_actualizar_estado_cotizacion('JP.260900010', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-09-10', 1, 1, 1, 'CON IGV', 18.00, 3, 4, '15 días', '5 días', 15, 'Obra civil no incluida', 'Entrega en almacén mina', 'CLI002', 4, 1); -- JP.260900011
CALL sp_actualizar_estado_cotizacion('JP.260900011', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-09-18', 4, 5, 2, 'CON IGV', 18.00, 3, 3, '6 días', '2 días', 15, 'Horarios sujetos a producción', 'Renovación contrato mantenimiento UHT', 'CLI008', 12, 6); -- JP.260900012
CALL sp_actualizar_estado_cotizacion('JP.260900012', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-09-25', 6, 1, 2, 'CON IGV', 18.00, 1, 1, '1 día', 'Inmediata', 5, 'Recargo nocturno aplicado', 'Fuga refrigerante cámara post-cosecha', 'CLI007', 10, 5); -- JP.260900013
CALL sp_actualizar_estado_cotizacion('JP.260900013', 5); -- Aprobada

-- === OCTUBRE 2026 ===
CALL sp_crear_cotizacion('2026-10-05', 3, 2, 1, 'CON IGV', 18.00, 3, 3, '18 días', '10 días', 20, 'Acometida principal por el cliente', 'Climatización quirófanos piso 3', 'CLI010', 14, 2); -- JP.261000014
CALL sp_actualizar_estado_cotizacion('JP.261000014', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-10-12', 1, 2, 1, 'CON IGV', 18.00, 4, 3, '12 días', '7 días', 15, 'Flete mina no incluido', 'Lote compresores y válvulas expansión', 'CLI009', 13, 4); -- JP.261000015
CALL sp_actualizar_estado_cotizacion('JP.261000015', 6); -- Rechazada

CALL sp_crear_cotizacion('2026-10-18', 3, 3, 1, 'CON IGV', 18.00, 4, 3, '20 días', '12 días', 30, 'Permisos municipales a cargo del cliente', 'Proyecto licitación oficinas San Isidro', 'CLI004', 6, 2); -- JP.261000016
CALL sp_actualizar_estado_cotizacion('JP.261000016', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-10-25', 5, 2, 2, 'CON IGV', 18.00, 2, 2, '5 días', '2 días', 15, 'Garantía no cubre fallas eléctricas', 'Cliente solicitó descuento del 5%', 'CLI005', 7, 4); -- JP.261000017
CALL sp_actualizar_estado_cotizacion('JP.261000017', 4); -- En negociación

CALL sp_crear_cotizacion('2026-10-29', 8, 1, 2, 'CON IGV', 18.00, 2, 2, '8 días', '4 días', 15, 'Ninguna', 'Integración tableros BMS planta', 'CLI008', 11, 6); -- JP.261000018
CALL sp_actualizar_estado_cotizacion('JP.261000018', 4); -- En negociación

-- === NOVIEMBRE 2026 (Cotizaciones activas, próximas a vencer y recientes) ===
CALL sp_crear_cotizacion('2026-11-06', 3, 2, 1, 'CON IGV', 18.00, 3, 3, '15 días', '7 días', 15, 'No incluye obra civil', 'Vence pronto - Revisar con compras', 'CLI011', 15, 2); -- JP.261100019
CALL sp_actualizar_estado_cotizacion('JP.261100019', 3); -- Enviada (Vence 21/11/2026)

CALL sp_crear_cotizacion('2026-11-10', 3, 2, 1, 'CON IGV', 18.00, 3, 3, '12 días', '7 días', 15, 'No incluye acometida eléctrica principal', 'Propuesta enviada a gerencia mina', 'CLI005', 7, 1); -- JP.261100020
CALL sp_actualizar_estado_cotizacion('JP.261100020', 3); -- Enviada (Vence 25/11/2026)

CALL sp_crear_cotizacion('2026-11-12', 4, 5, 2, 'CON IGV', 18.00, 2, 2, '4 días', '2 días', 10, 'Repuestos adicionales previa aprobación', 'Renovación anual de mantenimiento', 'CLI003', 5, 5); -- JP.261100021
CALL sp_actualizar_estado_cotizacion('JP.261100021', 3); -- Enviada (Vence 22/11/2026)

CALL sp_crear_cotizacion('2026-11-14', 1, 1, 1, 'CON IGV', 18.00, 3, 3, '10 días', '5 días', 15, 'Flete aéreo no incluido', 'Suministro repuestos originales Dixell', 'CLI007', 10, 7); -- JP.261100022
CALL sp_actualizar_estado_cotizacion('JP.261100022', 3); -- Enviada (Vence 29/11/2026)

CALL sp_crear_cotizacion('2026-11-16', 7, 3, 1, 'CON IGV', 18.00, 5, 4, '30 días', '15 días', 20, 'Grúa telescópica por cuenta del cliente', 'Ampliación sistema Chiller planta Arequipa', 'CLI008', 11, 3); -- JP.261100023
CALL sp_actualizar_estado_cotizacion('JP.261100023', 3); -- Enviada (Vence 06/12/2026)

CALL sp_crear_cotizacion('2026-11-17', 6, 1, 2, 'CON IGV', 18.00, 1, 1, '1 día', 'Inmediata', 7, 'Trabajo nocturno con recargo', 'Falla crítica en cuarto de control', 'CLI002', 3, 1); -- JP.261100024
CALL sp_actualizar_estado_cotizacion('JP.261100024', 2); -- En revisión

CALL sp_crear_cotizacion('2026-11-18', 9, 1, 2, 'CON IGV', 18.00, 1, 2, '3 días', '1 día', 15, 'Ninguna', 'Aprobada inmediatamente tras visita técnica', 'CLI001', 2, 4); -- JP.261100025
CALL sp_actualizar_estado_cotizacion('JP.261100025', 5); -- Aprobada

CALL sp_crear_cotizacion('2026-11-19', 8, 2, 1, 'SIN IGV', 18.00, 2, 3, '8 días', '5 días', 15, 'En evaluación de metrados', 'Borrador inicial en sistema', 'CLI012', 16, 7); -- JP.261100026
-- Queda en estado 1 (Borrador)

-- -----------------------------------------------------------------------------
-- 7. DETALLES DE LAS 26 COTIZACIONES (Usando sp_agregar_detalle_cotizacion)
-- -----------------------------------------------------------------------------

-- Cot 1 (JP.260600001 - USD - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260600001', 'EQU08607', 2, 4200.00, 'Unidades evaporadoras industriales 10 TR');
CALL sp_agregar_detalle_cotizacion('JP.260600001', 'EQU08603', 2, 966.00, 'Controladores electrónicos Dixell');
CALL sp_agregar_detalle_cotizacion('JP.260600001', 'SER0002',  2, 1200.00, 'Instalación integral y puesta en marcha');

-- Cot 2 (JP.260600002 - PEN - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260600002', 'SER0001',  6, 350.00, 'Mantenimiento preventivo 6 unidades manejadoras');
CALL sp_agregar_detalle_cotizacion('JP.260600002', 'MAT1902',  10, 39.44, 'Cambio preventivo sondas NTC');

-- Cot 3 (JP.260700003 - USD - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260700003', 'EQU08601', 4, 2500.00, 'Compresores herméticos Scroll 5HP');
CALL sp_agregar_detalle_cotizacion('JP.260700003', 'EQU08605', 4, 544.00, 'Válvulas de expansión electrónica');
CALL sp_agregar_detalle_cotizacion('JP.260700003', 'MAT1907',  4, 165.00, 'Kits filtros secadores y mirillas');
CALL sp_agregar_detalle_cotizacion('JP.260700003', 'SER0002',  3, 1200.00, 'Montaje y pruebas de estanqueidad con nitrógeno');

-- Cot 4 (JP.260700004 - PEN - Vencida)
CALL sp_agregar_detalle_cotizacion('JP.260700004', 'EQU08603', 3, 966.00, 'Controladores Dixell XM679K');
CALL sp_agregar_detalle_cotizacion('JP.260700004', 'EQU08602', 3, 133.00, 'Displays remotos CX660');

-- Cot 5 (JP.260700005 - PEN - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260700005', 'MAT1905',  2, 480.00, 'Carga completa gas ecológico R410A');
CALL sp_agregar_detalle_cotizacion('JP.260700005', 'SER0003',  2, 280.00, 'Diagnóstico electrónico y vacío profundo');

-- Cot 6 (JP.260800006 - PEN - Vencida)
CALL sp_agregar_detalle_cotizacion('JP.260800006', 'SER0003',  2, 280.00, 'Diagnóstico urgente y recarga gas R410A');

-- Cot 7 (JP.260800007 - USD - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260800007', 'SER0001',  4, 350.00, 'Mantenimiento preventivo 4 chillers industriales');
CALL sp_agregar_detalle_cotizacion('JP.260800007', 'MAT1902',  8, 39.44, 'Reemplazo preventivo de sondas NTC');

-- Cot 8 (JP.260800008 - USD - Rechazada)
CALL sp_agregar_detalle_cotizacion('JP.260800008', 'EQU08610', 3, 1450.00, 'Extractores centrífugos trifásicos 3HP');
CALL sp_agregar_detalle_cotizacion('JP.260800008', 'SER0004',  45, 95.00, 'Ductería galvanizada calibre 22');

-- Cot 9 (JP.260800009 - PEN - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260800009', 'EQU08604', 3, 136.00, 'Bobina solenoide Emerson 230VAC');
CALL sp_agregar_detalle_cotizacion('JP.260800009', 'EQU08603', 3, 966.00, 'Controlador Dixell XM679K');
CALL sp_agregar_detalle_cotizacion('JP.260800009', 'EQU08602', 3, 133.00, 'Display con 6 teclas CX660');
CALL sp_agregar_detalle_cotizacion('JP.260800009', 'MAT1903',  1, 224.40, 'Transductor de presión');

-- Cot 10 (JP.260900010 - USD - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260900010', 'EQU08608', 1, 18500.00, 'Chiller enfriado por aire 30 TR Trane');
CALL sp_agregar_detalle_cotizacion('JP.260900010', 'SER0002',  2, 1200.00, 'Izaje, montaje mecánico y arranque');
CALL sp_agregar_detalle_cotizacion('JP.260900010', 'SER0005',  1, 1850.00, 'Integración Modbus a sala de control');

-- Cot 11 (JP.260900011 - USD - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260900011', 'EQU08601', 2, 2500.00, 'Compresor hermético scroll 5HP');
CALL sp_agregar_detalle_cotizacion('JP.260900011', 'EQU08605', 2, 544.00, 'Válvula expansión electrónica');

-- Cot 12 (JP.260900012 - PEN - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260900012', 'SER0001',  8, 350.00, 'Mantenimiento preventivo líneas de envasado');
CALL sp_agregar_detalle_cotizacion('JP.260900012', 'EQU08609', 2, 680.00, 'Cortinas de aire sanitarias 1.50m');

-- Cot 13 (JP.260900013 - PEN - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.260900013', 'MAT1904',  12, 45.00, 'Reemplazo tramo tubería cobre tipo L');
CALL sp_agregar_detalle_cotizacion('JP.260900013', 'MAT1906',  12, 14.50, 'Aislamiento elastomérico');
CALL sp_agregar_detalle_cotizacion('JP.260900013', 'MAT1905',  1, 480.00, 'Carga de refrigerante R410A');
CALL sp_agregar_detalle_cotizacion('JP.260900013', 'SER0003',  1, 280.00, 'Atención de emergencia y soldadura');

-- Cot 14 (JP.261000014 - USD - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.261000014', 'EQU08607', 2, 4200.00, 'Unidades manejadoras higiénicas 10 TR');
CALL sp_agregar_detalle_cotizacion('JP.261000014', 'SER0004',  30, 95.00, 'Ductería aislada para sala blanca');
CALL sp_agregar_detalle_cotizacion('JP.261000014', 'SER0002',  2, 1200.00, 'Instalación y balanceo de caudales');

-- Cot 15 (JP.261000015 - USD - Rechazada)
CALL sp_agregar_detalle_cotizacion('JP.261000015', 'EQU08601', 3, 2500.00, 'Compresores Scroll 5HP');
CALL sp_agregar_detalle_cotizacion('JP.261000015', 'EQU08605', 3, 544.00, 'Válvulas expansión electrónica');

-- Cot 16 (JP.261000016 - USD - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.261000016', 'EQU08601', 4, 2500.00, 'Compresores Scroll para planta');
CALL sp_agregar_detalle_cotizacion('JP.261000016', 'EQU08603', 4, 966.00, 'Controladores Dixell');
CALL sp_agregar_detalle_cotizacion('JP.261000016', 'SER0002',  2, 1200.00, 'Servicios de instalación especializada');

-- Cot 17 (JP.261000017 - PEN - En negociación)
CALL sp_agregar_detalle_cotizacion('JP.261000017', 'MAT1904',  25, 45.00, 'Tubería de cobre tipo L 3/4');
CALL sp_agregar_detalle_cotizacion('JP.261000017', 'SER0003',  2, 280.00, 'Soldadura con nitrógeno y presurización');

-- Cot 18 (JP.261000018 - PEN - En negociación)
CALL sp_agregar_detalle_cotizacion('JP.261000018', 'SER0005',  2, 1850.00, 'Programación PLC e integración BMS');
CALL sp_agregar_detalle_cotizacion('JP.261000018', 'MAT1903',  4, 224.40, 'Transductores de presión');

-- Cot 19 (JP.261100019 - USD - Enviada vigente)
CALL sp_agregar_detalle_cotizacion('JP.261100019', 'EQU08610', 4, 1450.00, 'Extractores centrífugos sala de baterías');
CALL sp_agregar_detalle_cotizacion('JP.261100019', 'SER0002',  2, 1200.00, 'Montaje electromecánico en altura');

-- Cot 20 (JP.261100020 - USD - Enviada vigente)
CALL sp_agregar_detalle_cotizacion('JP.261100020', 'EQU08607', 2, 4200.00, 'Evaporadora industrial 10 TR Carrier');
CALL sp_agregar_detalle_cotizacion('JP.261100020', 'EQU08603', 2, 966.00, 'Controlador electrónico Dixell');
CALL sp_agregar_detalle_cotizacion('JP.261100020', 'SER0002',  2, 1200.00, 'Montaje mecánico y puesta en marcha');

-- Cot 21 (JP.261100021 - PEN - Enviada vigente)
CALL sp_agregar_detalle_cotizacion('JP.261100021', 'SER0001',  3, 350.00, 'Mantenimiento preventivo equipos Split Ducto');
CALL sp_agregar_detalle_cotizacion('JP.261100021', 'MAT1901',  6, 30.60, 'Conectores eléctricos para bobina');

-- Cot 22 (JP.261100022 - USD - Enviada vigente)
CALL sp_agregar_detalle_cotizacion('JP.261100022', 'EQU08603', 5, 966.00, 'Lote de controladores Dixell XM679K');
CALL sp_agregar_detalle_cotizacion('JP.261100022', 'EQU08602', 5, 133.00, 'Displays CX660 de repuesto');
CALL sp_agregar_detalle_cotizacion('JP.261100022', 'EQU08604', 10, 136.00, 'Bobinas solenoide Emerson');

-- Cot 23 (JP.261100023 - USD - Enviada vigente)
CALL sp_agregar_detalle_cotizacion('JP.261100023', 'EQU08608', 1, 18500.00, 'Chiller 30 TR Trane alta eficiencia');
CALL sp_agregar_detalle_cotizacion('JP.261100023', 'SER0002',  2, 1200.00, 'Instalación hidráulica y eléctrica');
CALL sp_agregar_detalle_cotizacion('JP.261100023', 'SER0005',  1, 1850.00, 'Monitoreo remoto BMS');

-- Cot 24 (JP.261100024 - PEN - En revisión)
CALL sp_agregar_detalle_cotizacion('JP.261100024', 'EQU08606', 4, 149.60, 'Sensor tubería de cobre PT 1000');
CALL sp_agregar_detalle_cotizacion('JP.261100024', 'SER0003',  1, 280.00, 'Atención técnica de emergencia');

-- Cot 25 (JP.261100025 - PEN - Aprobada)
CALL sp_agregar_detalle_cotizacion('JP.261100025', 'SER0001',  2, 350.00, 'Mantenimiento preventivo sala de servidores');
CALL sp_agregar_detalle_cotizacion('JP.261100025', 'MAT1902',  3, 39.44, 'Sondas de temperatura NTC');

-- Cot 26 (JP.261100026 - USD - Borrador)
CALL sp_agregar_detalle_cotizacion('JP.261100026', 'EQU08601', 1, 2500.00, 'Compresor Scroll 5HP de respaldo');
CALL sp_agregar_detalle_cotizacion('JP.261100026', 'MAT1907',  1, 165.00, 'Kit filtro secador');