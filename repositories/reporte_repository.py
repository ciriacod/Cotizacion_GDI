"""Consultas de negocio basadas en los diez reportes definidos para JP."""


class ReporteRepository:
    REPORTES = {
        "periodo": {
            "titulo": "Cotizaciones emitidas por periodo",
            "sql": """SELECT c.nmr_cotizacion AS 'N° Cotizacion', c.fecha_emision AS 'Fecha',
                        cl.razon_social AS 'Cliente', m.codigo_iso AS 'Moneda',
                        COALESCE(SUM(d.cantidad*d.precio_unitario),0.00) AS 'Subtotal',
                        CASE WHEN c.impuesto='CON IGV'
                             THEN ROUND(COALESCE(SUM(d.cantidad*d.precio_unitario),0)*(c.porcentaje_igv/100),2)
                             ELSE 0.00 END AS 'IGV',
                        CASE WHEN c.impuesto='CON IGV'
                             THEN ROUND(COALESCE(SUM(d.cantidad*d.precio_unitario),0)*(1+c.porcentaje_igv/100),2)
                             ELSE COALESCE(SUM(d.cantidad*d.precio_unitario),0.00) END AS 'Total',
                        ec.descripcion AS 'Estado'
                    FROM COTIZACION c
                    INNER JOIN CLIENTE cl ON cl.cod_interno=c.cod_interno_cliente
                    INNER JOIN MONEDA m ON m.id_moneda=c.id_moneda
                    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    LEFT JOIN DETALLE_COTIZACION d ON d.nmr_cotizacion=c.nmr_cotizacion
                    WHERE c.fecha_emision BETWEEN %s AND %s
                    GROUP BY c.nmr_cotizacion,c.fecha_emision,cl.razon_social,m.codigo_iso,
                             c.impuesto,c.porcentaje_igv,ec.descripcion
                    ORDER BY c.fecha_emision DESC,c.nmr_cotizacion DESC""",
            "parametros": "periodo",
        },
        "estados": {
            "titulo": "Cotizaciones por estado",
            "sql": """SELECT ec.descripcion AS 'Estado', COUNT(c.nmr_cotizacion) AS 'Cantidad',
                        CONCAT(ROUND(COUNT(c.nmr_cotizacion)*100.0/
                            NULLIF((SELECT COUNT(*) FROM COTIZACION),0),1),'%') AS 'Participacion'
                    FROM ESTADO_COTIZACION ec
                    LEFT JOIN COTIZACION c ON c.id_estado=ec.id_estado
                    WHERE ec.estado='Activo'
                    GROUP BY ec.id_estado,ec.descripcion ORDER BY ec.id_estado""",
        },
        "clientes": {
            "titulo": "Clientes con mayor cantidad de cotizaciones",
            "sql": """SELECT cl.cod_interno AS 'Codigo',cl.ruc AS 'RUC',cl.razon_social AS 'Razon social',
                        COUNT(c.nmr_cotizacion) AS 'Cotizaciones',
                        SUM(CASE WHEN ec.descripcion='Aprobada' THEN 1 ELSE 0 END) AS 'Aprobadas',
                        CONCAT(ROUND(SUM(CASE WHEN ec.descripcion='Aprobada' THEN 1 ELSE 0 END)*100.0/
                            NULLIF(COUNT(c.nmr_cotizacion),0),1),'%') AS 'Tasa de aprobacion'
                    FROM CLIENTE cl
                    LEFT JOIN COTIZACION c ON c.cod_interno_cliente=cl.cod_interno
                    LEFT JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    WHERE cl.estado='Activo'
                    GROUP BY cl.cod_interno,cl.ruc,cl.razon_social
                    ORDER BY COUNT(c.nmr_cotizacion) DESC,cl.razon_social""",
        },
        "productos": {
            "titulo": "Productos y servicios mas cotizados",
            "sql": """SELECT ps.cod_pro_ser AS 'Codigo',ps.Descripcion AS 'Descripcion',
                        tp.nombre_tipo AS 'Categoria',um.abreviatura AS 'Unidad',
                        COUNT(DISTINCT d.nmr_cotizacion) AS 'Veces cotizado',
                        SUM(d.cantidad) AS 'Cantidad total',
                        SUM(d.cantidad*d.precio_unitario) AS 'Monto acumulado'
                    FROM DETALLE_COTIZACION d
                    INNER JOIN PRODUCTO_SERVICIO ps ON ps.cod_pro_ser=d.cod_pro_ser
                    INNER JOIN TIPO_PRODUCTO tp ON tp.id_tipo=ps.id_tipo
                    INNER JOIN UNIDAD_MEDIDA um ON um.id_unidad=ps.id_unidad
                    GROUP BY ps.cod_pro_ser,ps.Descripcion,tp.nombre_tipo,um.abreviatura
                    ORDER BY COUNT(DISTINCT d.nmr_cotizacion) DESC,SUM(d.cantidad) DESC""",
        },
        "por_vencer": {
            "titulo": "Cotizaciones enviadas proximas a vencer",
            "sql": """SELECT c.nmr_cotizacion AS 'N° Cotizacion',cl.razon_social AS 'Cliente',
                        COALESCE(cc.nombre_contacto,'Sin contacto asignado') AS 'Contacto',
                        c.fecha_emision AS 'Emision',c.vigencia_dias AS 'Vigencia (dias)',
                        DATE_ADD(c.fecha_emision,INTERVAL c.vigencia_dias DAY) AS 'Vencimiento',
                        DATEDIFF(DATE_ADD(c.fecha_emision,INTERVAL c.vigencia_dias DAY),CURDATE()) AS 'Dias restantes',
                        e.nombre_completo AS 'Responsable'
                    FROM COTIZACION c
                    INNER JOIN CLIENTE cl ON cl.cod_interno=c.cod_interno_cliente
                    LEFT JOIN CONTACTO_CLIENTE cc ON cc.id_contacto=c.id_contacto
                    INNER JOIN EMPLEADO e ON e.id_empleado=c.id_empleado
                    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    WHERE ec.descripcion='Enviada'
                      AND DATE_ADD(c.fecha_emision,INTERVAL c.vigencia_dias DAY)>=CURDATE()
                    ORDER BY DATEDIFF(DATE_ADD(c.fecha_emision,INTERVAL c.vigencia_dias DAY),CURDATE())""",
        },
        "pendientes": {
            "titulo": "Cotizaciones pendientes de respuesta",
            "sql": """SELECT c.nmr_cotizacion AS 'N° Cotizacion',c.fecha_emision AS 'Emision',
                        cl.razon_social AS 'Cliente',COALESCE(cc.nombre_contacto,'No especificado') AS 'Contacto',
                        COALESCE(cc.telefono_contacto,'-') AS 'Telefono',COALESCE(cc.email_contacto,'-') AS 'Correo',
                        e.nombre_completo AS 'Responsable',ec.descripcion AS 'Estado'
                    FROM COTIZACION c
                    INNER JOIN CLIENTE cl ON cl.cod_interno=c.cod_interno_cliente
                    LEFT JOIN CONTACTO_CLIENTE cc ON cc.id_contacto=c.id_contacto
                    INNER JOIN EMPLEADO e ON e.id_empleado=c.id_empleado
                    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    WHERE ec.descripcion IN ('En revision','En revisión','Enviada')
                    ORDER BY c.fecha_emision""",
        },
        "mensual": {
            "titulo": "Montos cotizados por mes y moneda",
            "sql": """SELECT DATE_FORMAT(c.fecha_emision,'%Y-%m') AS 'Periodo',m.codigo_iso AS 'Moneda',
                        COUNT(DISTINCT c.nmr_cotizacion) AS 'Cotizaciones',
                        SUM(d.cantidad*d.precio_unitario) AS 'Subtotal cotizado',
                        SUM(CASE WHEN ec.descripcion='Aprobada' THEN d.cantidad*d.precio_unitario ELSE 0.00 END) AS 'Subtotal aprobado'
                    FROM COTIZACION c
                    INNER JOIN MONEDA m ON m.id_moneda=c.id_moneda
                    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    INNER JOIN DETALLE_COTIZACION d ON d.nmr_cotizacion=c.nmr_cotizacion
                    GROUP BY DATE_FORMAT(c.fecha_emision,'%Y-%m'),m.codigo_iso
                    ORDER BY DATE_FORMAT(c.fecha_emision,'%Y-%m') DESC,m.codigo_iso""",
        },
        "responsables": {
            "titulo": "Cotizaciones por responsable comercial",
            "sql": """SELECT e.DNI AS 'DNI',e.nombre_completo AS 'Responsable',
                        ca.nombre_cargo AS 'Cargo',es.nombre_especialidad AS 'Especialidad',
                        COUNT(c.nmr_cotizacion) AS 'Cotizaciones',
                        SUM(CASE WHEN ec.descripcion='Aprobada' THEN 1 ELSE 0 END) AS 'Aprobadas',
                        CONCAT(ROUND(SUM(CASE WHEN ec.descripcion='Aprobada' THEN 1 ELSE 0 END)*100.0/
                            NULLIF(COUNT(c.nmr_cotizacion),0),1),'%') AS 'Tasa de exito'
                    FROM EMPLEADO e
                    INNER JOIN CARGO ca ON ca.id_cargo=e.id_cargo
                    INNER JOIN ESPECIALIDAD es ON es.id_especialidad=e.id_especialidad
                    LEFT JOIN COTIZACION c ON c.id_empleado=e.id_empleado
                    LEFT JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    WHERE e.estado='Activo'
                    GROUP BY e.id_empleado,e.DNI,e.nombre_completo,ca.nombre_cargo,es.nombre_especialidad
                    ORDER BY COUNT(c.nmr_cotizacion) DESC""",
        },
        "aprobadas_cliente": {
            "titulo": "Cotizaciones aprobadas por cliente y moneda",
            "sql": """SELECT cl.ruc AS 'RUC',cl.razon_social AS 'Cliente',m.codigo_iso AS 'Moneda',
                        COUNT(DISTINCT c.nmr_cotizacion) AS 'Cotizaciones aprobadas',
                        SUM(d.cantidad*d.precio_unitario) AS 'Subtotal aprobado',
                        SUM(CASE WHEN c.impuesto='CON IGV'
                            THEN ROUND(d.cantidad*d.precio_unitario*(1+c.porcentaje_igv/100),2)
                            ELSE d.cantidad*d.precio_unitario END) AS 'Total facturable'
                    FROM CLIENTE cl
                    INNER JOIN COTIZACION c ON c.cod_interno_cliente=cl.cod_interno
                    INNER JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    INNER JOIN MONEDA m ON m.id_moneda=c.id_moneda
                    INNER JOIN DETALLE_COTIZACION d ON d.nmr_cotizacion=c.nmr_cotizacion
                    WHERE ec.descripcion='Aprobada'
                    GROUP BY cl.ruc,cl.razon_social,m.codigo_iso
                    ORDER BY cl.razon_social,m.codigo_iso""",
        },
        "tipos": {
            "titulo": "Cotizaciones por tipo de trabajo",
            "sql": """SELECT tc.id_tipo_cotizacion AS 'ID',tc.descripcion AS 'Tipo',
                        COUNT(DISTINCT c.nmr_cotizacion) AS 'Cotizaciones',
                        SUM(CASE WHEN ec.descripcion='Aprobada' THEN 1 ELSE 0 END) AS 'Aprobadas',
                        CONCAT(ROUND(COUNT(DISTINCT c.nmr_cotizacion)*100.0/
                            NULLIF((SELECT COUNT(*) FROM COTIZACION),0),1),'%') AS 'Participacion'
                    FROM TIPO_COTIZACION tc
                    LEFT JOIN COTIZACION c ON c.id_tipo_cotizacion=tc.id_tipo_cotizacion
                    LEFT JOIN ESTADO_COTIZACION ec ON ec.id_estado=c.id_estado
                    WHERE tc.estado='Activo'
                    GROUP BY tc.id_tipo_cotizacion,tc.descripcion
                    ORDER BY COUNT(DISTINCT c.nmr_cotizacion) DESC""",
        },
    }

    def __init__(self, database):
        self.database = database

    @classmethod
    def listar_reportes(cls):
        return [(key, value["titulo"]) for key, value in cls.REPORTES.items()]

    def ejecutar(self, password, codigo, fecha_inicio=None, fecha_fin=None):
        if codigo not in self.REPORTES:
            raise ValueError("El reporte solicitado no existe.")
        connection = self.database.connect(password)
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            config = self.REPORTES[codigo]
            if config.get("parametros") == "periodo":
                cursor.execute(config["sql"], (fecha_inicio, fecha_fin))
            else:
                cursor.execute(config["sql"])
            return cursor.fetchall()
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
