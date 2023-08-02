from flask import request, jsonify
from app import app, db
from ..models.sensor import Sensor, SensorSchema
from ..models.group import Group ,GroupSchema

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)
sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)

@app.route('/group/<int:group_id>/sensor/<int:sensor_id>', methods=['POST'])
def add_sensor_to_group(group_id, sensor_id):
    """
    Rota que adiciona um sensor a um grupo.

    Parâmetros:
        group_id (int): O ID do grupo ao qual o sensor será adicionado.
        sensor_id (int): O ID do sensor a ser adicionado ao grupo.

    Retorno:
        json: Uma mensagem de sucesso se o sensor for adicionado ao grupo com sucesso,
              ou uma mensagem de erro caso o grupo ou sensor não sejam encontrados.
    """

    # Busca o grupo e o sensor no banco de dados pelos IDs fornecidos
    group = Group.query.get(group_id)
    sensor = Sensor.query.get(sensor_id)

    # Verifica se o grupo e o sensor foram encontrados
    if group is not None and sensor is not None:
        # Adiciona o sensor ao grupo
        group.sensors.append(sensor)
        db.session.commit()

        # Retorna uma mensagem de sucesso com código de status 201 (Created)
        return jsonify({'message': 'sensor added to group'}), 201
    else:
        # Caso o grupo ou sensor não sejam encontrados, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'group or sensor not found'}), 404
    

@app.route('/group/<int:group_id>/sensor/<int:sensor_id>', methods=['DELETE'])
def remove_sensor_from_group(group_id, sensor_id):
    """
    Rota que remove um sensor de um grupo.

    Parâmetros:
        group_id (int): O ID do grupo do qual o sensor será removido.
        sensor_id (int): O ID do sensor a ser removido do grupo.

    Retorno:
        json: Uma mensagem de sucesso se o sensor for removido do grupo com sucesso,
              ou uma mensagem de erro caso o grupo ou sensor não sejam encontrados.
    """

    # Busca o grupo e o sensor no banco de dados pelos IDs fornecidos
    group = Group.query.get(group_id)
    sensor = Sensor.query.get(sensor_id)

    # Verifica se o grupo e o sensor foram encontrados
    if group is not None and sensor is not None:
        # Remove o sensor do grupo
        group.sensors.remove(sensor)
        db.session.commit()

        # Retorna uma mensagem de sucesso com código de status 200 (OK)
        return jsonify({'message': 'sensor removed from group'}), 200
    else:
        # Caso o grupo ou sensor não sejam encontrados, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'group or sensor not found'}), 404
    

@app.route('/group/<int:group_id>/sensors', methods=['GET'])
def get_sensors_in_group(group_id):
    """
    Rota que busca todos os sensores em um grupo.

    Parâmetros:
        group_id (int): O ID do grupo do qual os sensores serão buscados.

    Retorno:
        json: Uma lista contendo os dados de todos os sensores pertencentes ao grupo,
              ou uma mensagem de erro caso o grupo não seja encontrado.
    """

    # Busca o grupo no banco de dados pelo ID fornecido
    group = Group.query.get(group_id)

    # Verifica se o grupo foi encontrado
    if group is not None:
        # Serializa os dados de todos os sensores pertencentes ao grupo usando o esquema "SensorSchema"
        sensors = [sensor_schema.dump(sensor) for sensor in group.sensors]

        # Retorna a lista de sensores pertencentes ao grupo como resposta
        return jsonify(sensors)
    else:
        # Caso o grupo não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'group not found'}), 404
    

@app.route('/sensor/<int:sensor_id>/groups', methods=['GET'])
def get_groups_of_sensor(sensor_id):
    """
    Rota que busca todos os grupos de um sensor.

    Parâmetros:
        sensor_id (int): O ID do sensor do qual os grupos serão buscados.

    Retorno:
        json: Uma lista contendo os dados de todos os grupos aos quais o sensor pertence,
              ou uma mensagem de erro caso o sensor não seja encontrado.
    """

    # Busca o sensor no banco de dados pelo ID fornecido
    sensor = Sensor.query.get(sensor_id)

    # Verifica se o sensor foi encontrado
    if sensor is not None:
        # Serializa os dados de todos os grupos aos quais o sensor pertence usando o esquema "GroupSchema"
        groups = [group_schema.dump(group) for group in sensor.groups]

        # Retorna a lista de grupos aos quais o sensor pertence como resposta
        return jsonify(groups)
    else:
        # Caso o sensor não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'sensor not found'}), 404
