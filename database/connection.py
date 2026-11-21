"""Gestión de conexión MySQL y configuración local de COTIZEP.

La contraseña se solicita en cada sesión y nunca se persiste en disco.
"""
from __future__ import annotations

import configparser
import os
import sys
from pathlib import Path



def resource_path(*parts: str) -> Path:
    """Resuelve recursos tanto en desarrollo como dentro del ejecutable PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base.joinpath(*parts)


def _config_directory() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    path = root / "COTIZEP"
    path.mkdir(parents=True, exist_ok=True)
    return path


class DatabaseConnection:
    """Administrador MySQL compatible con los repositorios e instalador del proyecto."""

    def __init__(self, config: dict | None = None):
        self.config_path = _config_directory() / "database.ini"
        self.config = {
            "host": "127.0.0.1",
            "port": 3306,
            "database": "cotizacion",
            "user": "root",
        }
        if config:
            self.config.update(config)
        self._load_config()

    @property
    def database_name(self) -> str:
        return str(self.config["database"]).strip()

    def _load_config(self) -> None:
        parser = configparser.ConfigParser()
        if self.config_path.exists():
            parser.read(self.config_path, encoding="utf-8")
            if parser.has_section("mysql"):
                for key in self.config:
                    if parser.has_option("mysql", key):
                        self.config[key] = parser.get("mysql", key)
                try:
                    self.config["port"] = int(self.config["port"])
                except (TypeError, ValueError):
                    self.config["port"] = 3306

    def save_config(self, host: str, port: str | int, database: str, user: str) -> None:
        host, database, user = host.strip(), database.strip(), user.strip()
        if not host or not database or not user:
            raise ValueError("Host, base de datos y usuario MySQL son obligatorios.")
        try:
            port_number = int(port)
        except (TypeError, ValueError) as exc:
            raise ValueError("El puerto MySQL debe ser un número entero.") from exc
        if not 1 <= port_number <= 65535:
            raise ValueError("El puerto debe estar entre 1 y 65535.")
        if not database.replace("_", "").isalnum():
            raise ValueError("El nombre de la base de datos solo admite letras, números y guion bajo.")
        self.config.update(host=host, port=port_number, database=database, user=user)
        parser = configparser.ConfigParser()
        parser["mysql"] = {
            "host": host,
            "port": str(port_number),
            "database": database,
            "user": user,
        }
        with self.config_path.open("w", encoding="utf-8") as stream:
            parser.write(stream)

    def _connect(self, password: str, include_database: bool):
        params = {
            "host": self.config["host"],
            "port": int(self.config["port"]),
            "user": self.config["user"],
            "password": password or "",
            "charset": "utf8mb4",
            "connection_timeout": 8,
            "autocommit": False,
        }
        if include_database:
            params["database"] = self.database_name
        try:
            import mysql.connector
            from mysql.connector import Error
            return mysql.connector.connect(**params)
        except ImportError as error:
            raise RuntimeError(
                "Falta mysql-connector-python. Instala las dependencias con: "
                "python -m pip install -r requirements.txt"
            ) from error
        except Exception as error:
            # Conserva el mensaje original del conector para diagnosticar el servidor.
            raise ConnectionError(f"No se pudo conectar con MySQL: {error}") from error

    def connect(self, password: str = ""):
        """Conecta a la base configurada."""
        return self._connect(password, include_database=True)

    def connect_server(self, password: str = ""):
        """Conecta al servidor sin seleccionar una base, para inicializarla."""
        return self._connect(password, include_database=False)
