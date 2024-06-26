import mysql.connector


class Usuarios:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.cursor.execute(f"USE {database}")
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                password_hash VARCHAR(200) NOT NULL
            )
        ''')
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
        
    #----------------------------------------------------------------
    def registrar_usuario(self, username, email, password_hash):
        sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        valores = (username, email, password_hash)

        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return self.cursor.lastrowid

    #----------------------------------------------------------------
    def consultar_existencia_email(self, email):  # retorna veces que encontró ese email
        self.cursor.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE email='{email}') AS 'exists'")
        return self.cursor.fetchone()["exists"]
    
    def consultar_existencia_nombre(self, username): # retorna veces que encontró ese username
        self.cursor.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE username='{username}') AS 'exists'")
        return self.cursor.fetchone()["exists"]
    
    def consultar_usuario(self, username):
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        return self.cursor.fetchone()
    
    #----------------------------------------------------------------
    def modificar_contrasenia(self, username, email, old_password_hash, new_password_hash):
        sql = "UPDATE users SET password_hash = %s WHERE username=%s AND email=%s AND password_hash=%s "
        valores = (new_password_hash, username, email, old_password_hash)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    #----------------------------------------------------------------
    def eliminar_usuario(self, username, email, password_hash):
        # Eliminamos un producto de la tabla a partir de su código
        sql = "DELETE FROM users WHERE username=%s, email=%s, password_hash=%s"  # pasamos todos los valores para estar bien seguros de qué estamos eliminando
        valores = (username, email, password_hash)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0
