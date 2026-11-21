"""Consultas de negocio ejecutadas mediante Procedimientos Almacenados."""


class ReporteRepository:
    REPORTES = {
        "periodo": {
            "titulo": "Cotizaciones emitidas por periodo",
            "sp": "sp_reporte_01_cotizaciones_periodo",
            "parametros": "periodo",
        },
        "estados": {
            "titulo": "Cotizaciones por estado",
            "sp": "sp_reporte_02_embudo_comercial",
        },
        "clientes": {
            "titulo": "Clientes con mayor cantidad de cotizaciones",
            "sp": "sp_reporte_03_ranking_clientes",
        },
        "productos": {
            "titulo": "Productos y servicios mas cotizados",
            "sp": "sp_reporte_04_top_productos_servicios",
        },
        "por_vencer": {
            "titulo": "Cotizaciones enviadas proximas a vencer",
            "sp": "sp_reporte_05_cotizaciones_por_vencer",
        },
        "pendientes": {
            "titulo": "Cotizaciones pendientes de respuesta",
            "sp": "sp_reporte_06_cotizaciones_pendientes",
        },
        "mensual": {
            "titulo": "Montos cotizados por mes y moneda",
            "sp": "sp_reporte_07_evolucion_financiera_mensual",
        },
        "responsables": {
            "titulo": "Cotizaciones por responsable comercial",
            "sp": "sp_reporte_08_desempeno_empleados",
        },
        "aprobadas_cliente": {
            "titulo": "Cotizaciones aprobadas por cliente y moneda",
            "sp": "sp_reporte_09_ventas_cerradas_cliente",
        },
        "tipos": {
            "titulo": "Cotizaciones por tipo de trabajo",
            "sp": "sp_reporte_10_demanda_tipo_trabajo",
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
            sp_name = config["sp"]
            if config.get("parametros") == "periodo":
                cursor.execute(f"CALL {sp_name}(%s, %s)", (fecha_inicio, fecha_fin))
            else:
                cursor.execute(f"CALL {sp_name}()")

            resultados = cursor.fetchall() if cursor.with_rows else []
            while cursor.nextset():
                if cursor.with_rows:
                    cursor.fetchall()
            return resultados
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()