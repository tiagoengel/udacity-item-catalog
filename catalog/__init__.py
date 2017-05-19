from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


DB_URL = 'postgresql:///catalog' + ('_test' if environ.get('ENV') == 'test' else '')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

if environ.get('ENV') != 'test':
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)
else:
    app.jinja_env.globals['csrf_token'] = lambda: 'test'