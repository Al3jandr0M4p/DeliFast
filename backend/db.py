from mysql.connector import Error, connect

from .config.config import Config

def get_connection_db():
    try:

        conn = connect(
            host=Config.HOST_NAME_APP,
            user=Config.USER_NAME_APP,
            password=Config.PASSWD_APP,
            database=Config.DB_APP
        )
        return conn

    except Error as e:
        print(f"[!] ERROR con la conexion de la db {str(e)}")
        return None