import mysql.connector
from mysql.connector import Error


class DatabaseConnection:

    def __init__(self, config):
        self.config = config

    def connect(self):

        try:
            connection = mysql.connector.connect(
                host=self.config["host"],
                port=int(self.config["port"]),
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                charset="utf8mb4",
                connection_timeout=5
            )

            return connection

        except Error as error:
            raise ConnectionError(
                f"No se pudo conectar con MySQL: {error}"
            ) from error
