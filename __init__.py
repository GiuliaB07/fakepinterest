from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_bcrypt import Bcrypt

import os
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comunidade.db"
app.config["SECRET_KEY"] = "e0defa1c100947e2874e850f6db82914"
app.config["UPLOAD_FOLDER"] = "static/fotos_posts"
app.config['CHAVE_ACESSO'] = os.getenv('VÉSPERA', 'chave_padrao_segura') 
database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "homepage"




from fakepinterest import routes