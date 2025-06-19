# auth/api_auth

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests as google_request


from ...controllers.auth.auth_controller import AuthController
from ...config.config import Config


class ApiAuth:

    def __init__(self):
        self.auth = Blueprint("api_auth", __name__)
        self.auth_controllers = AuthController()
        self.auth_routes()

    def auth_routes(self):

        # register_api
        @self.auth.route("/api/register", methods=["POST"])
        def register_api():
            data = request.get_json()

            email = data.get("email")
            username = data.get("username")
            password = data.get("password")
            rol = data.get("tipoCuenta")

            # verificar que los campos no esten vacios o no se manden un null a la db
            if not all([email, username, password]):
                return jsonify({"message": "Todos los campos son requeridos"}), 400

            # buscar si ya existe el email
            user_exists = self.auth_controllers.find_user_by_email(email)
            if user_exists:
                return jsonify({"message": "El correo ya esta registrado"}), 409

            # buscar si ya existe el username
            username_exists = self.auth_controllers.find_user_by_username(username)
            if username_exists:
                return jsonify({"message": "El nombre de usuario ya esta en uso"}), 409

            # crear al usuario
            self.auth_controllers.insert_user(
                email, username, password, rol, auth_method="local"
            )

            return (
                jsonify(
                    {
                        "message": "usuario creado exitosamente",
                        "redirect": "/",
                        "username": username,
                    }
                ),
                201,
            )

        # login_api
        @self.auth.route("/api/login", methods=["POST"])
        def login_api():
            data = request.get_json()

            username = data.get("username")
            password = data.get("password")

            if not all([username, password]):
                return jsonify({"message": "Todos los campos son requeridos"}), 400

            user = self.auth_controllers.find_user_by_username(username)

            if not user:
                return jsonify({"message": "Usuario no registrado correctamente"}), 404

            if user["auth_method"] != "local":
                return (
                    jsonify(
                        {"message": "Este usuario debe iniciar session con Google"}
                    ),
                    403,
                )

            # validar la password
            if not check_password_hash(user["password"], password):
                return jsonify({"message": "Contraseña incorrecta"}), 401

            # redireccionar segun el rol
            if user["rol"] == "admin":
                return (
                    jsonify(
                        {
                            "message": f"Bienvenido {user['username']}",
                            "redirect": "/dashboard/admin",
                        }
                    ),
                    200,
                )
            elif user["rol"] == "vendedor":
                return (
                    jsonify(
                        {
                            "message": f"Bienvenido {user['username']}",
                            "redirect": "/dashboard/vendor",
                        }
                    ),
                    200,
                )
            elif user["rol"] == "delivery":
                return (
                    jsonify(
                        {
                            "message": f"Bienvenido {user['username']}",
                            "redirect": "/dashboard/delivery",
                        }
                    ),
                    200,
                )
            elif user["rol"] == "client":
                return (
                    jsonify(
                        {
                            "message": f"Bienvenido {user['username']}",
                            "redirect": "/user",
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"message": "Usuario no tiene un rol existente"}), 400

        @self.auth.route("/api/google-login", methods=["POST"])
        def google_login():
            data = request.get_json()
            token = data.get("token")

            try:
                idinfo = id_token.verify_oauth2_token(
                    token, google_request.Request(), Config.CLIENT_ID_GOOGLE
                )

                email = idinfo["email"]

                user = self.auth_controllers.find_user_by_email(email)
                if user:
                    if user["auth_method"] != "google":
                        return (
                            jsonify(
                                {
                                    "message": "Este usuario debe iniciar session con usuario y contraseña"
                                }
                            ),
                            403,
                        )

                    return (
                        jsonify(
                            {
                                "message": f"Bienvenido {user['username']}",
                                "redirect": "/user",
                                "user": {
                                    "username": user["username"]
                                }
                            }
                        ),
                        200,
                    )

                else:
                    return jsonify({"newUser": True}), 200

            except Exception as e:
                print(f"ERROR verificando token {str(e)}")
                return jsonify({"message": "Token invalido"}), 400

        @self.auth.route("/api/google-register", methods=["POST"])
        def google_register():
            data = request.get_json()
            token = data.get("token")
            rol = data.get("rol")

            if rol not in ["client", "vendedor", "delivery"]:
                return jsonify({"message": "Rol no valido"}), 400

            try:
                idinfo = id_token.verify_oauth2_token(
                    token, google_request.Request(), Config.CLIENT_ID_GOOGLE
                )
                email = idinfo["email"]
                name = idinfo.get("name", "Usuario")

                user = self.auth_controllers.find_user_by_email(email)
                if user:
                    return jsonify({"message": "Este usuario ya existe"}), 409

                # Crear usuario con método google
                self.auth_controllers.insert_user(
                    email=email,
                    username=name,
                    password="GOOGLE_AUTH",
                    rol=rol,
                    auth_method="google",
                )

                redirects_paths = {
                    "client": "/user",
                    "vendedor": "/dashboard/vendor",
                    "delivery": "/dashboard/delivery",
                }

                user = self.auth_controllers.find_user_by_email(email)

                return (
                    jsonify(
                        {
                            "message": f"Bienvenido {user["username"]}",
                            "redirect": redirects_paths.get(user["rol"], "/"),
                            "user": {
                                "username": user["username"]
                            }
                        }
                    ),
                    201,
                )

            except Exception as e:
                print(f"ERROR verificando token {str(e)}")
                return jsonify({"message": "Token inválido"}), 400
