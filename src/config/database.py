import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self):
        self.host = "localhost"
        self.port = 3306
        self.database = "cotizacion"
        self.user = "root"
        self.password = "root"

    def get_connection(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if conn.is_connected():
                return conn
        except Error as e:
            print(f"[Error MySQL] No se pudo conectar: {e}")
            return None

    def test_connection(self):
        conn = self.get_connection()
        if conn:
            info = conn.get_server_info()
            conn.close()
            return True, f"Conexión exitosa a MySQL Server v{info} (BD: {self.database})"
        return False, "Error al conectar con la base de datos 'cotizacion'"