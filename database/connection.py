"""Conexiones MySQL para JP Cotiza. La contraseña solo vive en memoria."""
from __future__ import annotations
import configparser
import os
import sys
from pathlib import Path

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None
    MySQLError = Exception
else:
    mysql = mysql.connector


def resource_path(*parts: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return root.joinpath(*parts)


class DatabaseConnection:
    def __init__(self, config_path: str | Path | None = None):
        self.project_root = Path(__file__).resolve().parent.parent
        if config_path is None:
            if os.name == "nt":
                user_config = Path(os.getenv("APPDATA", Path.home())) / "JP_Cotiza" / "database.ini"
            else:
                user_config = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "jp_cotiza" / "database.ini"
            self.config_path = user_config
        else:
            self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        parser = configparser.ConfigParser()
        if self.config_path.exists():
            parser.read(self.config_path, encoding="utf-8")
        section = parser["mysql"] if parser.has_section("mysql") else {}
        return {
            "host": os.getenv("JP_DB_HOST", section.get("host", "127.0.0.1")).strip(),
            "port": int(os.getenv("JP_DB_PORT", section.get("port", "3306"))),
            "database": os.getenv("JP_DB_NAME", section.get("database", "cotizacion")).strip(),
            "user": os.getenv("JP_DB_USER", section.get("user", "root")).strip(),
        }

    def save_config(self, host, port, database, user):
        port = int(port)
        if not host.strip() or not user.strip() or not database.strip() or not 1 <= port <= 65535:
            raise ValueError("Completa host, puerto válido, base de datos y usuario MySQL.")
        self.config = {"host": host.strip(), "port": port, "database": database.strip(), "user": user.strip()}
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        parser = configparser.ConfigParser()
        parser["mysql"] = {k: str(v) for k, v in self.config.items()}
        with self.config_path.open("w", encoding="utf-8") as f:
            parser.write(f)

    @property
    def database_name(self):
        return self.config["database"]

    def connect_server(self, password: str):
        if mysql is None:
            raise RuntimeError("Falta mysql-connector-python. Reinstala la aplicación o sus dependencias.")
        try:
            conn = mysql.connect(host=self.config["host"], port=self.config["port"], user=self.config["user"],
                                 password=password, connection_timeout=8, charset="utf8mb4", autocommit=True)
            if not conn.is_connected():
                raise ConnectionError("MySQL no confirmó la conexión.")
            return conn
        except MySQLError as exc:
            raise ConnectionError(f"No se pudo conectar al servidor MySQL: {exc}") from exc

    def connect(self, password: str):
        if password is None:
            raise ValueError("La conexión fue cancelada.")
        if mysql is None:
            raise RuntimeError("No está instalado mysql-connector-python.")
        try:
            conn = mysql.connect(**self.config, password=password, connection_timeout=8,
                                 charset="utf8mb4", collation="utf8mb4_unicode_ci", autocommit=False)
            if not conn.is_connected():
                raise ConnectionError("MySQL no confirmó la conexión.")
            return conn
        except MySQLError as exc:
            raise ConnectionError(f"No se pudo conectar con la base '{self.database_name}': {exc}") from exc

    def test_connection(self, password: str):
        conn = self.connect(password)
        try:
            cur = conn.cursor()
            cur.execute("SELECT DATABASE(), VERSION()")
            db, version = cur.fetchone()
            cur.close()
            if int(str(version).split('.', 1)[0]) < 8:
                raise RuntimeError(f"Se requiere MySQL 8.0 o superior; servidor: {version}.")
            return {"connected": True, "database": db, "version": version}
        finally:
            conn.close()
