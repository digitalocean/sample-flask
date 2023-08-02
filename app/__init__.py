from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_pydantic_spec import FlaskPydanticSpec

# Inicializa o aplicativo Flask e carrega as configurações a partir do objeto Config
app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o banco de dados SQLAlchemy com base na configuração do aplicativo
db = SQLAlchemy(app)

# Inicializa a especificação Pydantic para documentação da API com título "Atlas"
spec = FlaskPydanticSpec('flask', title='Atlas')

# Registra a especificação Pydantic no aplicativo Flask
spec.register(app)

# Importa os módulos de rotas da sua aplicação
from .routes import system_routes, subsystem_routes, equipments_routes, sensor_routes, group_routes, group_sensor_routes, influx_routes

# Importa o módulo que contém o controlador (funções de manipulação dos dados da API)
from .control import controlador