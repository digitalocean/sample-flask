from flask import Flask, jsonify, request
from app import app, spec
from ..models.influx import get_buckets, get_bucket_schema, get_measurements_schema, get_measurements_value, get_ids
from influxdb_client import InfluxDBClient
from app.client_influx import client
from typing import Literal
import requests
import json

url = client['url']
token = client['token']
org =client['org']

# Rota para obter os buckets disponíveis
@app.route('/buckets', methods=['GET'])
def buckets():
    """
    Get the available buckets.

    Returns:
        List[str]: A list of bucket names.
    """
    # Crie a instância do InfluxDBClient
    cliente = InfluxDBClient(url=url, token=token, org=org)

    # Obtenha os buckets disponíveis
    buckets = get_buckets(cliente)

    # Retorne a lista de buckets em formato JSON
    return jsonify(buckets)


@app.route('/buckets/<bucket>/schema/<schema>', methods=['GET'])
def bucket_schema(bucket, schema: Literal['fieldKeys','tagKeys', 'measurements']):
    """
    Rota que obtém o esquema (fieldKeys, tagKeys ou measurements) de um bucket específico.

    Parâmetros:
        bucket (str): O nome do bucket do qual se deseja obter o esquema.
        schema (str): O tipo de esquema desejado, que pode ser 'fieldKeys', 'tagKeys' ou 'measurements'.

    Retorno:
        json: O esquema solicitado do bucket em formato JSON.
    """

    # Crie a instância do InfluxDBClient
    cliente = InfluxDBClient(url=url, token=token, org=org)

    # Obtenha o esquema do bucket específico
    bucket_schema = get_bucket_schema(bucket, schema, org, cliente)

    # Retorne o esquema em formato JSON
    return jsonify(bucket_schema)


@app.route('/buckets/<bucket>/measurements/<measurements>/schema/<schema>', methods=['GET'])
def measurements_schema(bucket, measurements, schema: Literal['Tag','Field']):
    """
    Rota que obtém o esquema de medições (Tag ou Field) de um bucket e medição específicos.

    Parâmetros:
        bucket (str): O nome do bucket ao qual a medição pertence.
        measurements (str): O nome da medição da qual se deseja obter o esquema.
        schema (str): O tipo de esquema desejado, que pode ser 'Tag' ou 'Field'.

    Retorno:
        json: O esquema solicitado da medição em formato JSON.
    """

    # Crie a instância do InfluxDBClient
    cliente = InfluxDBClient(url=url, token=token, org=org)

    # Obtenha o esquema de medições do bucket específico
    measurements_schema = get_measurements_schema(bucket, measurements, schema, org, cliente)

    # Retorne o esquema de medições em formato JSON
    return jsonify(measurements_schema)


@app.route('/buckets/<bucket>/measurements/<measurements>/tags/<tag>', methods=['GET'])
def measurements_value(bucket, measurements, tag):
    """
    Rota que obtém os valores das tags de medições de um bucket, medição e tag específicos.

    Parâmetros:
        bucket (str): O nome do bucket ao qual a medição pertence.
        measurements (str): O nome da medição da qual se deseja obter os valores da tag.
        tag (str): O nome da tag da qual se deseja obter os valores.

    Retorno:
        json: Os valores da tag de medição solicitada em formato JSON.
    """

    # Crie a instância do InfluxDBClient
    cliente = InfluxDBClient(url=url, token=token, org=org)

    # Obtenha os valores das tags de medições do bucket específico
    measurements_value = get_measurements_value(bucket, measurements, tag, org, cliente)

    # Retorne os valores das tags em formato JSON
    return jsonify(measurements_value)


# Rota para obter os IDs únicos de um bucket e medição (measurement) específicos
@app.route('/buckets/<bucket>/measurements/<measurements>/ids', methods=['GET'])
def unique_ids(bucket, measurements):
    """
    Rota que obtém os IDs únicos de um bucket e medição específicos.

    Parâmetros:
        bucket (str): O nome do bucket ao qual a medição pertence.
        measurements (str): O nome da medição da qual se deseja obter os IDs únicos.

    Retorno:
        json: Os IDs únicos da medição solicitada em formato JSON.
    """

    # Crie a instância do InfluxDBClient
    cliente = InfluxDBClient(url=url, token=token, org=org)

    # Obtenha os IDs únicos do bucket e medição específicos
    ids = get_ids(bucket, measurements, org, cliente)

    # Retorne os IDs únicos em formato JSON
    return jsonify(ids)

'''# Rota para criar um novo ponto de dados (measurement)
@app.route('/measurements', methods=['POST'])
def create_measurement_route():
    # Obtenha os dados do ponto de dados a ser criado a partir do corpo da solicitação
    data = request.get_json()
    bucket = data['bucket']
    measurement = data['measurement']
    fields = data['fields']
    tags = data['tags']

    # Crie a instância do InfluxDBClient
    cliente = InfluxDBClient(url=url, token=token, org=org)

    # Crie o novo ponto de dados (measurement)
    create_measurement(bucket, measurement, fields, tags, org, cliente)

    # Retorne uma resposta de sucesso
    return jsonify({'message': 'Measurement created successfully'})'''


'''@app.route('/buckets', methods=['POST'])
def create_bucket(name):
    headers = {
    "Authorization": f"Token {token}",
    "Content-type": "application/json"
    }
    data = {
    "orgID": {org},
    "name": f"{name}",
    "retentionRules": [
            {
                "type": "expire",
                "everySeconds": 0,
                "shardGroupDurationSeconds": 0
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))'''