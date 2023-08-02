from flask import request, jsonify
from app import app, db
from ..models.sensor import Sensor, SensorSchema


sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)


@app.route('/sensor', methods=['POST'])
def add_sensor():
    """
    Rota que adiciona um novo sensor.

    Parâmetros:
        None (os dados do sensor são enviados pelo corpo da requisição como JSON).

    Retorno:
        json: Os dados do sensor adicionado.
    """

    # Obtém os dados do sensor enviados pelo corpo da requisição como JSON
    id_influx_sensor = request.json['id_influx_sensor']
    friendly_name = request.json.get('friendly_name')
    model_number = request.json.get('model_number')
    manufacturer = request.json.get('manufacturer')
    installation_date = request.json.get('installation_date')
    measurement_type = request.json.get('measurement_type')
    measurement_unit = request.json.get('measurement_unit')
    measurement_unit_abbreviation = request.json.get('measurement_unit_abbreviation')
    description = request.json.get('description')
    precision = request.json.get('precision')
    max = request.json.get('max')
    min = request.json.get('min')
    equipment_idequipment = request.json.get('equipment_idequipment')

    # Cria uma nova instância do sensor usando os dados recebidos
    new_sensor = Sensor(
        id_influx_sensor=id_influx_sensor, 
        friendly_name=friendly_name, 
        model_number=model_number, 
        manufacturer=manufacturer, 
        installation_date=installation_date, 
        measurement_type=measurement_type, 
        measurement_unit=measurement_unit, 
        measurement_unit_abbreviation=measurement_unit_abbreviation, 
        description=description, 
        precision=precision, 
        max=max, 
        min=min, 
        equipment_idequipment=equipment_idequipment)

    # Adiciona o novo sensor ao banco de dados
    db.session.add(new_sensor)
    db.session.commit()

    # Retorna os dados do sensor adicionado como resposta com código de status 201 (Created)
    return jsonify(sensor_schema.dump(new_sensor)), 201


@app.route('/sensor/<int:id>', methods=['GET'])
def get_sensor(id):
    """
    Rota que busca um sensor pelo ID.

    Parâmetros:
        id (int): O ID do sensor a ser buscado.

    Retorno:
        json: Os dados do sensor encontrado ou uma mensagem de erro caso o sensor não seja encontrado.
    """

    # Busca o sensor no banco de dados pelo ID fornecido
    sensor = Sensor.query.get(id)

    # Verifica se o sensor foi encontrado
    if sensor is not None:
        # Retorna os dados do sensor encontrado como resposta
        return jsonify(sensor_schema.dump(sensor))
    else:
        # Caso o sensor não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'sensor not found'}), 404


@app.route('/sensor/<int:id>', methods=['PUT'])
def update_sensor(id):
    """
    Rota que atualiza os dados de um sensor pelo ID.

    Parâmetros:
        id (int): O ID do sensor a ser atualizado.

    Retorno:
        json: Os dados do sensor atualizado ou uma mensagem de erro caso o sensor não seja encontrado.
    """

    # Busca o sensor no banco de dados pelo ID fornecido
    sensor = Sensor.query.get(id)

    # Verifica se o sensor foi encontrado
    if sensor is not None:
        # Atualiza os dados do sensor com os novos dados enviados pelo corpo da requisição como JSON
        sensor.id_influx_sensor = request.json['id_influx_sensor']
        sensor.friendly_name = request.json.get('friendly_name')
        sensor.model_number = request.json.get('model_number')
        sensor.manufacturer = request.json.get('manufacturer')
        sensor.installation_date = request.json.get('installation_date')
        sensor.measurement_type = request.json.get('measurement_type')
        sensor.measurement_unit = request.json.get('measurement_unit')
        sensor.measurement_unit_abbreviation = request.json.get('measurement_unit_abbreviation')
        sensor.description = request.json.get('description')
        sensor.precision = request.json.get('precision')
        sensor.max = request.json.get('max')
        sensor.min = request.json.get('min')
        sensor.equipment_idequipment = request.json.get('equipment_idequipment')

        # Realiza a atualização no banco de dados
        db.session.commit()

        # Retorna os dados do sensor atualizado como resposta
        return jsonify(sensor_schema.dump(sensor))
    else:
        # Caso o sensor não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'sensor not found'}), 404


@app.route('/sensor/<int:id>', methods=['DELETE'])
def delete_sensor(id):
    """
    Rota que exclui um sensor pelo ID.

    Parâmetros:
        id (int): O ID do sensor a ser excluído.

    Retorno:
        json: Os dados do sensor excluído ou uma mensagem de erro caso o sensor não seja encontrado.
    """

    # Busca o sensor no banco de dados pelo ID fornecido
    sensor = Sensor.query.get(id)

    # Verifica se o sensor foi encontrado
    if sensor is not None:
        # Remove o sensor do banco de dados
        db.session.delete(sensor)
        db.session.commit()

        # Retorna os dados do sensor excluído como resposta
        return jsonify(sensor_schema.dump(sensor))
    else:
        # Caso o sensor não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'sensor not found'}), 404


@app.route('/sensor', methods=['GET'])
def get_sensors():
    """
    Rota que busca todos os sensores.

    Parâmetros:
        None.

    Retorno:
        json: Uma lista contendo os dados de todos os sensores no banco de dados.
    """

    # Busca todos os sensores no banco de dados
    all_sensors = Sensor.query.all()

    # Serializa os dados de todos os sensores usando o esquema "SensorSchema"
    return jsonify(sensors_schema.dump(all_sensors))


@app.route('/sensor_by_id_influx/<string:id_influx_sensor>', methods=['GET'])
def get_sensor_by_influx_id(id_influx_sensor):
    """
    Rota que busca um sensor pelo ID do Influx.

    Parâmetros:
        id_influx_sensor (str): O ID do sensor no Influx a ser buscado.

    Retorno:
        json: Os dados do sensor encontrado ou uma mensagem de erro caso o sensor não seja encontrado.
    """

    # Busca o sensor no banco de dados pelo ID do Influx fornecido
    sensor = Sensor.query.filter_by(id_influx_sensor=id_influx_sensor).first()

    # Verifica se o sensor foi encontrado
    if sensor is not None:
        # Retorna os dados do sensor encontrado como resposta
        return jsonify(sensor_schema.dump(sensor))
    else:
        # Caso o sensor não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'sensor not found'}), 404


