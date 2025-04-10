from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

jwt = JWTManager()
db = SQLAlchemy()

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///banco_local.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False