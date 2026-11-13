import tkinter as tk
from tkinter import messagebox
from config.database import DatabaseConnection

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("J.P. Ingeniería y Servicios S.R.L. - Sistema de Cotizaciones")
        self.root.geometry("420x300")
        self.root.resizable(False, False)
        self.db = DatabaseConnection()

        # Título
        tk.Label(root, text="SISTEMA DE COTIZACIONES HVAC", font=("Arial", 12, "bold")).pack(pady=15)

        # Formulario Login
        tk.Label(root, text="Correo Corporativo:").pack()
        self.entry_email = tk.Entry(root, width=35)
        self.entry_email.insert(0, "noelia.gonzales@jpingenieria.pe")  # Credencial de prueba
        self.entry_email.pack(pady=5)

        tk.Label(root, text="Contraseña:").pack()
        self.entry_pass = tk.Entry(root, width=35, show="*")
        self.entry_pass.insert(0, "123456")
        self.entry_pass.pack(pady=5)

        # Botones
        tk.Button(root, text="Ingresar al Sistema", width=25, bg="#1f6aa5", fg="white", command=self.login).pack(pady=10)
        tk.Button(root, text="Probar Conexión a BD", width=25, command=self.check_db).pack(pady=5)

    def check_db(self):
        ok, msg = self.db.test_connection()
        if ok:
            messagebox.showinfo("Prueba de Conexión", msg)
        else:
            messagebox.showerror("Error de Conexión", msg)

    def login(self):
        email = self.entry_email.get().strip()
        clave = self.entry_pass.get().strip()

        conn = self.db.get_connection()
        if not conn:
            messagebox.showerror("Error", "Sin conexión a la base de datos.")
            return

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("sp_login_empleado", [email, clave])
            usuario = None
            for result in cursor.stored_results():
                usuario = result.fetchone()

            if usuario:
                messagebox.showinfo("Bienvenido", f"Acceso concedido:\n{usuario['nombre_completo']} ({usuario['nombre_cargo']})")
                # Aquí abriremos el Menú Principal (Clientes, Productos, Cotizaciones, Reportes)
            else:
                messagebox.showwarning("Acceso Denegado", "Credenciales incorrectas o usuario inactivo.")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()