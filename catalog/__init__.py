from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


DB_URL = 'postgresql:///catalog' + ('_test' if environ['ENV'] == 'test' else '')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)