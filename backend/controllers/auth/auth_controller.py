# auth/auth_controller

from werkzeug.security import generate_password_hash

from ...db import get_connection_db

class AuthController:

    def __init__(self):
        self.conn = get_connection_db()
    
    def find_user_by_email(self, email):
        with self.conn.cursor(dictionary=True) as cursor:
            query = """
            select * from users where email = %s
            """
            cursor.execute(query, (email,))
            return cursor.fetchone()

    def find_user_by_username(self, username):
        with self.conn.cursor(dictionary=True) as cursor:
            query = """
            select * from users where username = %s
            """
            cursor.execute(query, (username,))
            return cursor.fetchone()

    def insert_user(self, email, username, password, rol, auth_method='local'):
        password_hash = generate_password_hash(password) if auth_method == 'local' else None

        with self.conn.cursor(dictionary=True) as cursor:
            query = """
            insert into users (email, username, password, rol, auth_method)
            values (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (email, username, password_hash, rol, auth_method))
            self.conn.commit()
