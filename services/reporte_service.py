"""Validacion y ejecucion de los reportes comerciales."""

from datetime import date
from repositories.reporte_repository import ReporteRepository


class ReporteService:
    def __init__(self, database):
        self.repository = ReporteRepository(database)

    def listar_reportes(self):
        return self.repository.listar_reportes()

    def ejecutar(self, password, codigo, fecha_inicio=None, fecha_fin=None):
        if codigo == "periodo":
            try:
                inicio = date.fromisoformat(str(fecha_inicio))
                fin = date.fromisoformat(str(fecha_fin))
            except (TypeError, ValueError) as error:
                raise ValueError("Ingresa las fechas en formato AAAA-MM-DD.") from error
            if inicio > fin:
                raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")
            return self.repository.ejecutar(password, codigo, inicio, fin)
        return self.repository.ejecutar(password, codigo)
