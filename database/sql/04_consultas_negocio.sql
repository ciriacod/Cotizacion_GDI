-- =============================================================================
-- 4. SCRIPT DE CONSULTAS DE NEGOCIO (DQL) - 10 REPORTES GERENCIALES
-- Empresa: J.P. Ingeniería y Servicios S.R.L.
-- Módulo: Gestión de Cotizaciones Comerciales (HVAC)
-- Gestor: MySQL 8.0+
-- =============================================================================

USE cotizacion;

-- Cambia estas fechas antes de ejecutar la consulta 01.
SET @fecha_inicio = DATE_FORMAT(CURDATE(), '%Y-%m-01');
SET @fecha_fin = LAST_DAY(CURDATE());

-- -----------------------------------------------------------------------------
-- Consulta 01. Cotizaciones emitidas en un periodo (ej. Noviembre 2026)
-- Incluye cálculo discriminado de Subtotal, IGV y Total General según condición
-- -----------------------------------------------------------------------------
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
WHERE c.fecha_emision BETWEEN @fecha_inicio AND @fecha_fin
GROUP BY c.nmr_cotizacion, c.fecha_emision, cl.razon_social, m.codigo_iso, c.impuesto, c.porcentaje_igv, ec.descripcion
ORDER BY c.fecha_emision DESC, c.nmr_cotizacion DESC;


-- -----------------------------------------------------------------------------
-- Consulta 02. Embudo comercial: Cotizaciones según su estado y participación %
-- -----------------------------------------------------------------------------
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


-- -----------------------------------------------------------------------------
-- Consulta 03. Ranking de clientes con más cotizaciones y tasa de aprobación
-- -----------------------------------------------------------------------------
SELECT 
    cl.cod_interno AS 'Código',
    cl.ruc AS 'RUC',
    cl.razon_social AS 'Razón Social',
    COUNT(c.nmr_cotizacion) AS 'Total Solicitadas',
    SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN 1 ELSE 0 END) AS 'Aprobadas',
    CONCAT(
        ROUND(SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(c.nmr_cotizacion), 0), 1),
        '%'
    ) AS 'Efectividad Cierre'
FROM CLIENTE cl
LEFT JOIN COTIZACION c ON cl.cod_interno = c.cod_interno_cliente
LEFT JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado
WHERE cl.estado = 'Activo'
GROUP BY cl.cod_interno, cl.ruc, cl.razon_social
ORDER BY COUNT(c.nmr_cotizacion) DESC, SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN 1 ELSE 0 END) DESC;


-- -----------------------------------------------------------------------------
-- Consulta 04. Top productos y servicios más cotizados (Demanda de catálogo)
-- -----------------------------------------------------------------------------
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


-- -----------------------------------------------------------------------------
-- Consulta 05. Alerta comercial: Cotizaciones enviadas próximas a vencer
-- Usa directamente vigencia_dias sin manipular cadenas de texto
-- -----------------------------------------------------------------------------
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
INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado
WHERE ec.descripcion = 'Enviada' 
  AND DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY) >= CURDATE()
ORDER BY DATEDIFF(DATE_ADD(c.fecha_emision, INTERVAL c.vigencia_dias DAY), CURDATE()) ASC;


-- -----------------------------------------------------------------------------
-- Consulta 06. Seguimiento: Cotizaciones pendientes de respuesta (En revisión o Enviada)
-- Vincula exactamente el contacto asignado en la cotización (sin filas duplicadas)
-- -----------------------------------------------------------------------------
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
WHERE ec.descripcion IN ('En revisión', 'En revision', 'Enviada')
ORDER BY c.fecha_emision ASC;


-- -----------------------------------------------------------------------------
-- Consulta 07. Evolución financiera: Montos cotizados y aprobados por mes y moneda
-- Corrige conteo usando COUNT(DISTINCT) para evitar inflación por ítems de detalle
-- -----------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(c.fecha_emision, '%Y-%m') AS 'Periodo (Año-Mes)',
    m.codigo_iso AS 'Moneda',
    COUNT(DISTINCT c.nmr_cotizacion) AS 'Total Cotizaciones',
    SUM(dt.cantidad * dt.precio_unitario) AS 'Subtotal Cotizado',
    SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN dt.cantidad * dt.precio_unitario ELSE 0.00 END) AS 'Subtotal Aprobado'
FROM COTIZACION c
INNER JOIN MONEDA m ON c.id_moneda = m.id_moneda
INNER JOIN ESTADO_COTIZACION ec ON c.id_estado = ec.id_estado
INNER JOIN DETALLE_COTIZACION dt ON c.nmr_cotizacion = dt.nmr_cotizacion
GROUP BY DATE_FORMAT(c.fecha_emision, '%Y-%m'), m.codigo_iso
ORDER BY DATE_FORMAT(c.fecha_emision, '%Y-%m') DESC, m.codigo_iso ASC;


-- -----------------------------------------------------------------------------
-- Consulta 08. Desempeño comercial: Cotizaciones y cierres por empleado
-- -----------------------------------------------------------------------------
SELECT 
    e.DNI AS 'DNI',
    e.nombre_completo AS 'Responsable Comercial',
    car.nombre_cargo AS 'Cargo',
    esp.nombre_especialidad AS 'Especialidad',
    COUNT(c.nmr_cotizacion) AS 'Cotizaciones Elaboradas',
    SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN 1 ELSE 0 END) AS 'Cotizaciones Aprobadas',
    CONCAT(
        ROUND(SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(c.nmr_cotizacion), 0), 1),
        '%'
    ) AS 'Tasa de Éxito'
FROM EMPLEADO e
INNER JOIN CARGO car ON e.id_cargo = car.id_cargo
INNER JOIN ESPECIALIDAD esp ON e.id_especialidad = esp.id_especialidad
LEFT JOIN COTIZACION c ON e.id_empleado = c.id_empleado
LEFT JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado
WHERE e.estado = 'Activo'
GROUP BY e.id_empleado, e.DNI, e.nombre_completo, car.nombre_cargo, esp.nombre_especialidad
ORDER BY COUNT(c.nmr_cotizacion) DESC;


-- -----------------------------------------------------------------------------
-- Consulta 09. Ventas cerradas: Cotizaciones aprobadas por cliente y moneda
-- Separa PEN y USD para evitar sumar divisas distintas en una misma cifra
-- -----------------------------------------------------------------------------
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
INNER JOIN ESTADO_COTIZACION ec ON c.id_estado = ec.id_estado
WHERE ec.descripcion = 'Aprobada'
GROUP BY cl.ruc, cl.razon_social, m.codigo_iso
ORDER BY cl.razon_social ASC, m.codigo_iso ASC;


-- -----------------------------------------------------------------------------
-- Consulta 10. Demanda por línea de negocio: Cotizaciones por tipo de trabajo
-- -----------------------------------------------------------------------------
SELECT 
    tc.id_tipo_cotizacion AS 'ID',
    tc.descripcion AS 'Tipo de Cotización / Servicio',
    COUNT(DISTINCT c.nmr_cotizacion) AS 'Cantidad Cotizaciones',
    SUM(CASE WHEN ec.descripcion = 'Aprobada' THEN 1 ELSE 0 END) AS 'Aprobadas',
    CONCAT(
        ROUND(COUNT(DISTINCT c.nmr_cotizacion) * 100.0 / NULLIF((SELECT COUNT(*) FROM COTIZACION), 0), 1),
        '%'
    ) AS 'Participación %'
FROM TIPO_COTIZACION tc
LEFT JOIN COTIZACION c ON tc.id_tipo_cotizacion = c.id_tipo_cotizacion
LEFT JOIN ESTADO_COTIZACION ec ON ec.id_estado = c.id_estado
WHERE tc.estado = 'Activo'
GROUP BY tc.id_tipo_cotizacion, tc.descripcion
ORDER BY COUNT(DISTINCT c.nmr_cotizacion) DESC;