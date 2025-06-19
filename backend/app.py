# backend/app

from flask import Flask
from flask_cors import CORS

from .config.config import Config
from .routes.auth.api_auth import ApiAuth

class DeliFast:

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        self.app.secret_key = self.app.config['SECRET_SESSION_KEY']
        CORS(self.app)

        # BluePrints
        self.app.register_blueprint(ApiAuth().auth)

    def run(self):
        self.app.run(debug=True, host='0.0.0.0')
