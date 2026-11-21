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
