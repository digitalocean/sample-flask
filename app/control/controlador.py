from flask import request, jsonify
from app import app, spec, db
import app.routes.sensor_routes as sensors
import app.routes.influx_routes as influx
import requests
import json
from ..models.sensor import Sensor, SensorSchema
from ..models.group import Group, GroupSchema
from datetime import datetime

sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)
group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)

url_base = 'http://localhost:5000'

@app.route('/controlador/buckets/ativos_nao_importados', methods=['GET'])
def importar_ativos():
    """
    Rota que retorna uma lista de ativos não importados de um bucket específico.

    Parâmetros:
        Nenhum parâmetro é passado na URL. Os dados devem ser enviados no corpo da requisição
        como um JSON contendo a chave 'bucket' com o nome do bucket para obter os ativos não importados.

    Retorno:
        JSON: Uma lista de objetos contendo informações sobre os ativos não importados.
    """
    data = request.get_json()

    if not data or 'bucket' not in data:
        return jsonify({"error": "A requisição JSON deve conter a chave 'bucket' com o nome do bucket no banco de dados InfluxDB."}), 400

    bucket = data['bucket']

    # Obtendo a lista de equipamentos do bucket
    equipamentos = requests.get(f'{url_base}/buckets/{bucket}/schema/measurements').json()

    # Obtendo a lista de sensores do serviço local
    resposta = requests.get(f'{url_base}/sensor')

    if resposta.status_code == 200:
        sensores_atlas = resposta.json()
    else:
        print('Ocorreu um erro ao obter os sensores:', resposta)

    # Criando um conjunto de IDs dos sensores do serviço local para agilizar comparações
    ids_atlas = set([sensor['id_influx_sensor'] for sensor in sensores_atlas])
    lista_sensor = []

    # Iterando pelos equipamentos para obter os IDs não importados
    for equip in equipamentos:
        ids_influx = set((requests.get(f'{url_base}/buckets/{bucket}/measurements/{equip}/ids').json()))
        lista_sensor.append({'equipment': equip, 'ids': list(ids_influx - ids_atlas)})

    return jsonify(lista_sensor)



@app.route('/controlador/salvar_sensores', methods=['POST'])
def salvar_sensores():
    """
    Rota que salva os sensores enviados pelo formulário da interface web.

    Parâmetros:
        None (os dados dos sensores são enviados pelo corpo da requisição como JSON).
        sensor{
            idsensor :(int) ID do sensor (chave primária, gerado pelo banco de dados)
            id_influx_sensor :(str) ID do sensor no banco de dados InfluxDB (obrigatório)
            friendly_name :(str) Nome amigável do sensor (opcional)
            model_number :(str) Número do modelo do sensor (opcional)
            manufacturer :(str) Fabricante do sensor (opcional)
            installation_date :(datetime) Data de instalação do sensor (opcional)
            measurement_type :(str) Tipo de medição do sensor (opcional)
            measurement_unit :(str) Unidade de medição do sensor (opcional)
            measurement_unit_abbreviation :(str) Abreviação da unidade de medição do sensor (opcional)
            description :(str) Descrição do sensor (opcional)
            precision :(float) Precisão do sensor (opcional)
            max :(float) Valor máximo que o sensor pode medir (opcional)
            min :(float) Valor mínimo que o sensor pode medir (opcional)
            equipment_idequipment :(int) ID do equipamento associado a este sensor (chave estrangeira, opcional)
            }

    Retorno:
        json: Uma lista de sensores com erros, se houver, caso contrário, retorna sucesso.
    """

    # Obtém os dados dos sensores enviados pelo formulário da interface web
    lista_sensores = request.json
    
    # Lista para armazenar os sensores com erros
    sensores_erro = []

    # Lista para armazenar os sensores salvos
    sensores_salvos = []

    # Itera sobre os sensores recebidos
    for sensor in lista_sensores:
        # Converte a data de instalação para objeto datetime
        if 'installation_date' in sensor:
            sensor['installation_date'] = datetime.fromisoformat(sensor['installation_date'])

        # Serializa o sensor para enviar como JSON
        sensor_json = sensor_schema.dump(sensor)

        # Envia o sensor para a API usando o método POST e obtém a resposta
        resposta = requests.post(f'{url_base}/sensor', json=sensor_json)

        if resposta.status_code == 201:
            # Se o sensor for adicionado com sucesso, imprime a mensagem de sucesso
            sensores_salvos.append(sensor)
        else:
            # Se ocorrer um erro, adiciona o sensor à lista de sensores com erros
            sensores_erro.append(sensor)            

    # Retorna a lista de sensores com erros como resposta
    # Se houver sensores com erro, retorna o código de status 400, caso contrário, retorna o código de status 200
    return jsonify({'sensores_com_erro': sensores_erro, 'sensores_salvos' : sensores_salvos})


@app.route('/controlador/salvar_sensor', methods=['POST'])
def salvar_sensor():
    """
    Rota que salva um sensor enviado pelo formulário da interface web.

    Parâmetros:
        None (os dados dos sensores são enviados pelo corpo da requisição como JSON).
        sensor{
            idsensor :(int) ID do sensor (chave primária, gerado pelo banco de dados)
            id_influx_sensor :(str) ID do sensor no banco de dados InfluxDB (obrigatório)
            friendly_name :(str) Nome amigável do sensor (opcional)
            model_number :(str) Número do modelo do sensor (opcional)
            manufacturer :(str) Fabricante do sensor (opcional)
            installation_date :(datetime) Data de instalação do sensor (opcional)
            measurement_type :(str) Tipo de medição do sensor (opcional)
            measurement_unit :(str) Unidade de medição do sensor (opcional)
            measurement_unit_abbreviation :(str) Abreviação da unidade de medição do sensor (opcional)
            description :(str) Descrição do sensor (opcional)
            precision :(float) Precisão do sensor (opcional)
            max :(float) Valor máximo que o sensor pode medir (opcional)
            min :(float) Valor mínimo que o sensor pode medir (opcional)
            equipment_idequipment :(int) ID do equipamento associado a este sensor (chave estrangeira, opcional)
            }

    Retorno:
        json: id e descrição do sensor.
    """

    # Obtém os dados do sensor enviado pelo formulário da interface web
    sensor = request.json

    if 'installation_date' in sensor:
            sensor['installation_date'] = datetime.fromisoformat(sensor['installation_date'])

    sensor_json = sensor_schema.dump(sensor)
    resposta = requests.post(f'{url_base}/sensor', json=sensor_json)
    if resposta.status_code == 201:
        return jsonify({'idsensor': resposta['idsensor'], 'descrição' : resposta['description']}), 200

    
@app.route('/controlador/sensor_by_id_influx', methods=['GET'])
def buscar_sensor_by_influx_id():
    """
    Rota que busca um sensor pelo 'id_influx_sensor' enviado no corpo da requisição.
    Parâmetros:
        data (JSON): Deve ser enviado no corpo da requisição contendo a chave 'id_influx_sensor' com a string de busca.
    Retorno:
        JSON: Os dados do sensor encontrados ou uma mensagem de erro caso o sensor não seja encontrado.
    """

    data = request.get_json()

    if not data or 'id_influx_sensor' not in data:
        return jsonify({"error": "A requisição JSON deve conter a chave 'id_influx_sensor' com o ID do sensor no banco de dados InfluxDB."}), 400

    id_influx_sensor = data['id_influx_sensor']

    # Fazendo a requisição para a rota 'sensor_by_id_influx' no arquivo sensor_routes.py
    resposta = requests.get(f'{url_base}/sensor_by_id_influx/{id_influx_sensor}')

    # Verifica se a resposta foi bem-sucedida (código de status 200)
    if resposta.status_code == 200:
        sensor = resposta.json()

        # Completando as informações do sensor com dados adicionais, como equipamento, subsistema e sistema.
        if sensor['equipment_idequipment'] != "":
            equipamento = requests.get(f'{url_base}/equipment/{sensor["equipment_idequipment"]}').json()
            sensor.update(equipamento)

            if equipamento['subsystem_idsubsystem'] != "":
                subsystem = requests.get(f'{url_base}/subsystem/{equipamento["subsystem_idsubsystem"]}').json()
                sensor.update(subsystem)

                if subsystem['system_idsystem'] != "":
                    system = requests.get(f'{url_base}/system/{subsystem["system_idsystem"]}').json()
                    sensor.update(system)

        return sensor
    else:
        # Caso o sensor não seja encontrado, retorna um JSON com a mensagem de erro
        return jsonify({'error': 'Sensor not found'}), 404



@app.route('/controlador/buscar_ativos', methods=['GET'])
def buscar_ativos():
    """
    Rota que busca ativos (sensores) com base em uma string de busca fornecida no formato JSON.

    Parâmetros:
        data (JSON): Deve ser enviado no corpo da requisição contendo a chave 'query' com a string de busca.

    Retorno:
        JSON: Uma lista de objetos contendo informações dos sensores que correspondem à string de busca.
              Retorna código de status 200 em caso de sucesso ou código de status 400 em caso de erro.
    """

    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({"message": "A string de busca deve ser fornecida no formato JSON com a chave 'query'."}), 400

    search_query = data['query']

    if len(search_query) < 3:
        return jsonify({"message": "A busca deve conter pelo menos 3 caracteres."}), 400

    # Realiza a busca nos sensores com base na string de busca, filtrando por descrição, ID e nome amigável.
    sensors = Sensor.query.filter(
        (Sensor.description.ilike(f'%{search_query}%')) |
        (Sensor.id_influx_sensor.ilike(f'%{search_query}%')) |
        (Sensor.friendly_name.ilike(f'%{search_query}%'))
    ).all()

    sensor_schema = SensorSchema(many=True)
    result = sensor_schema.dump(sensors)

    return jsonify({"sensors": result}), 200


@app.route('/controlador/edita_sensor', methods=['PUT'])
def editar_sensor_by_influx_id():
    """
    Rota que atualiza os dados de um sensor pelo ID do Influx.

    Parâmetros:
        Nenhum parâmetro é passado na URL. Os dados do sensor e o ID do Influx a serem atualizados devem ser enviados no corpo da requisição
        como um JSON contendo a chave 'id_influx_sensor' com o ID do sensor no banco de dados InfluxDB e os campos a serem atualizados.

    Retorno:
        JSON: Os dados do sensor atualizado ou uma mensagem de erro caso o sensor não seja encontrado.
    """

    data = request.get_json()

    if not data or 'id_influx_sensor' not in data:
        return jsonify({"error": "A requisição JSON deve conter a chave 'id_influx_sensor' com o ID do sensor no banco de dados InfluxDB."}), 400

    id_influx_sensor = data['id_influx_sensor']

    # Busca o sensor no banco de dados pelo ID do Influx fornecido
    sensor = Sensor.query.filter_by(id_influx_sensor=id_influx_sensor).first()

    # Verifica se o sensor foi encontrado
    if sensor is not None:
        # Atualiza os dados do sensor com os novos dados enviados pelo corpo da requisição como JSON
        sensor.friendly_name = data.get('friendly_name')
        sensor.model_number = data.get('model_number')
        sensor.manufacturer = data.get('manufacturer')
        sensor.installation_date = data.get('installation_date')
        sensor.measurement_type = data.get('measurement_type')
        sensor.measurement_unit = data.get('measurement_unit')
        sensor.measurement_unit_abbreviation = data.get('measurement_unit_abbreviation')
        sensor.description = data.get('description')
        sensor.precision = data.get('precision')
        sensor.max = data.get('max')
        sensor.min = data.get('min')
        sensor.equipment_idequipment = data.get('equipment_idequipment')

        # Realiza a atualização no banco de dados
        db.session.commit()

        # Retorna os dados do sensor atualizado como resposta
        return jsonify(sensor_schema.dump(sensor))
    else:
        # Caso o sensor não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'sensor not found'}), 404


@app.route('/controlador/adicionar_sensor_grupo', methods=['POST'])
def adicionar_sensor_grupo():
    """
    Rota para adicionar um sensor a um grupo no sistema Atlas.

    Parâmetros:
        None. (Os dados do sensor e grupo devem ser fornecidos no corpo da requisição JSON.)

    Retorno:
        json: Uma mensagem de sucesso caso o sensor seja adicionado ao grupo com êxito,
              ou uma mensagem de erro caso o sensor ou grupo não sejam encontrados.
    """

    # Obtém os dados da requisição JSON enviados no corpo da requisição
    data = request.get_json()

    # Verifica se os dados foram enviados corretamente e contêm as chaves 'idsensor' e 'idgroup'
    if not data or 'idsensor' not in data or 'idgroup' not in data:
        return jsonify({"error": "A requisição JSON deve conter a chave 'idsensor' e a chave 'idgroup' com o ID do sensor no banco de dados do Atlas e do grupo."}), 400

    # Obtém os IDs do sensor e do grupo da requisição JSON
    sensor_id = data['idsensor']
    group_id = data['idgroup']

    # Realiza a requisição para adicionar o sensor ao grupo no sistema Atlas
    resposta = requests.post(f'{url_base}/group/{group_id}/sensor/{sensor_id}')

    # Verifica se a requisição foi bem sucedida (código de status 201)
    if resposta.status_code == 201:
        # Retorna uma mensagem de sucesso caso o sensor seja adicionado ao grupo com êxito
        return jsonify({'message': 'sensor adicionado ao grupo'}), 201
    else:
        # Caso o grupo ou sensor não sejam encontrados, retorna uma mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'grupo ou sensor não encontrado'}), 404


@app.route('/controlador/buscar_sensor_no_grupo', methods=['GET'])
def buscar_sensor_no_grupo():
    """
    Rota para buscar os sensores em um grupo no sistema Atlas.

    Parâmetros:
        None. (Os dados do grupo devem ser fornecidos no corpo da requisição JSON.)

    Retorno:
        json: Uma lista contendo os sensores do grupo caso o grupo não esteja vazio,
              ou uma mensagem de erro caso o grupo esteja vazio ou não seja encontrado.
    """

    # Obtém os dados da requisição JSON enviados no corpo da requisição
    data = request.get_json()

    # Verifica se os dados foram enviados corretamente e contêm a chave 'idgroup'
    if not data or 'idgroup' not in data:
        return jsonify({"error": "A requisição JSON deve conter a chave 'idgroup' com o ID do grupo no banco de dados do Atlas."}), 400

    # Obtém o ID do grupo da requisição JSON
    group_id = data['idgroup']

    # Realiza a requisição para buscar os sensores do grupo no sistema Atlas
    resposta = requests.get(f'{url_base}/group/{group_id}/sensors')

    # Verifica se a requisição foi bem sucedida (código de status diferente de 404)
    if resposta.status_code != 404:
        # Serializa os dados dos sensores retornados em uma lista
        result = resposta.json()

        # Retorna uma lista contendo os sensores do grupo como resposta
        return jsonify({"sensors": result}), 200
    else:
        # Caso o grupo esteja vazio ou não seja encontrado, retorna uma mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'grupo vazio'}), 404

    
    
@app.route('/controlador/buscar_grupo_por_sensor', methods=['GET'])
def buscar_grupo_por_sensor():
    """
    Rota para buscar os grupos aos quais um sensor pertence no sistema Atlas.

    Parâmetros:
        None. (Os dados do sensor devem ser fornecidos no corpo da requisição JSON.)

    Retorno:
        json: Uma lista contendo os grupos aos quais o sensor pertence,
              ou uma mensagem de erro caso o sensor não seja encontrado ou não pertença a nenhum grupo.
    """

    # Obtém os dados da requisição JSON enviados no corpo da requisição
    data = request.get_json()

    # Verifica se os dados foram enviados corretamente e contêm a chave 'sensor_id'
    if not data or 'sensor_id' not in data:
        return jsonify({"error": "A requisição JSON deve conter a chave 'sensor_id' com o ID do sensor no banco de dados do Atlas."}), 400

    # Obtém o ID do sensor da requisição JSON
    sensor_id = data['sensor_id']

    # Realiza a requisição para buscar os grupos aos quais o sensor pertence no sistema Atlas
    resposta = requests.get(f'{url_base}/group/{sensor_id}/groups')

    # Verifica se a requisição foi bem sucedida (código de status diferente de 404)
    if resposta.status_code != 404:
        # Serializa os dados dos grupos retornados em uma lista
        group_schema = groups_schema(many=True)
        result = group_schema.dump(resposta)

        # Retorna uma lista contendo os grupos aos quais o sensor pertence como resposta
        return jsonify({"grupos:": result}), 200
    else:
        # Caso o sensor não seja encontrado ou não pertença a nenhum grupo,
        # retorna uma mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'sensor não pertence a nenhum grupo'}), 404

