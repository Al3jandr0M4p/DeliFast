from dotenv import load_dotenv
import os

load_dotenv()

class Config:

    # configuracion de las variables de la db
    HOST_NAME_APP = os.getenv("HOST_NAME_APP")
    USER_NAME_APP = os.getenv("USER_NAME_APP")
    PASSWD_APP = os.getenv("PASSWD_APP")
    DB_APP = os.getenv("DB_APP")
    PORT_APP = os.getenv("PORT_APP")

    # configuracion de la secret session key
    SECRET_SESSION_KEY = os.getenv("SECRET_SESSION_KEY")

    # configuracion del id client de google
    CLIENT_ID_GOOGLE = os.getenv("CLIENT_ID_GOOGLE")
