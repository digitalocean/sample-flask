from flask import request, jsonify
from app import app, db, spec
from ..models.equipment import Equipment, EquipmentSchema

equipment_schema = EquipmentSchema()
equipments_schema = EquipmentSchema(many=True)


@app.route('/equipment', methods=['POST'])
def add_equipment():
    """
    Rota que adiciona um novo equipamento.

    Parâmetros:
        None (os dados do equipamento são enviados pelo corpo da requisição como JSON).

    Retorno:
        json: Os dados do equipamento adicionado.
    """

    # Obtém os dados do equipamento enviados pelo corpo da requisição como JSON
    name = request.json['name']
    geo_location = request.json.get('geo_location')
    subsystem_idsubsystem = request.json['subsystem_idsubsystem']

    # Cria uma nova instância do equipamento usando os dados recebidos
    new_equipment = Equipment(name=name, geo_location=geo_location, subsystem_idsubsystem=subsystem_idsubsystem)

    # Adiciona o novo equipamento ao banco de dados
    db.session.add(new_equipment)
    db.session.commit()

    # Retorna os dados do equipamento adicionado como resposta com código de status 201 (Created)
    return jsonify(equipment_schema.dump(new_equipment)), 201


@app.route('/equipment/<int:id>', methods=['GET'])
def get_equipment(id):
    """
    Rota que busca um equipamento pelo seu ID.

    Parâmetros:
        id (int): O ID do equipamento a ser buscado.

    Retorno:
        json: Os dados do equipamento encontrado ou uma mensagem de erro caso o equipamento não seja encontrado.
    """

    # Busca o equipamento no banco de dados pelo ID fornecido
    equipment = Equipment.query.get(id)

    # Verifica se o equipamento foi encontrado
    if equipment is not None:
        # Retorna os dados do equipamento encontrado como resposta
        return jsonify(equipment_schema.dump(equipment))
    else:
        # Caso o equipamento não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'equipment not found'}), 404


@app.route('/equipment/<int:id>', methods=['PUT'])
def update_equipment(id):
    """
    Rota que atualiza os dados de um equipamento pelo ID.

    Parâmetros:
        id (int): O ID do equipamento a ser atualizado.

    Retorno:
        json: Os dados do equipamento atualizado ou uma mensagem de erro caso o equipamento não seja encontrado.
    """

    # Busca o equipamento no banco de dados pelo ID fornecido
    equipment = Equipment.query.get(id)

    # Verifica se o equipamento foi encontrado
    if equipment is not None:
        # Atualiza os dados do equipamento com os novos dados enviados pelo corpo da requisição como JSON
        equipment.name = request.json['name']
        equipment.geo_location = request.json.get('geo_location')
        equipment.subsystem_idsubsystem = request.json['subsystem_idsubsystem']

        # Realiza a atualização no banco de dados
        db.session.commit()

        # Retorna os dados do equipamento atualizado como resposta
        return jsonify(equipment_schema.dump(equipment))
    else:
        # Caso o equipamento não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'equipment not found'}), 404


@app.route('/equipment/<int:id>', methods=['DELETE'])
def delete_equipment(id):
    """
    Rota que deleta um equipamento existente.

    Parâmetros:
        id (int): O ID do equipamento a ser deletado.

    Retorno:
        json: Os dados do equipamento deletado ou uma mensagem de erro caso o equipamento não seja encontrado.
    """

    # Busca o equipamento no banco de dados pelo ID fornecido
    equipment = Equipment.query.get(id)

    # Verifica se o equipamento foi encontrado
    if equipment is not None:
        # Deleta o equipamento do banco de dados
        db.session.delete(equipment)
        db.session.commit()

        # Retorna os dados do equipamento deletado como resposta
        return jsonify(equipment_schema.dump(equipment))
    else:
        # Caso o equipamento não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'equipment not found'}), 404


@app.route('/equipment', methods=['GET'])
def get_equipments():
    """
    Rota que busca todos os equipamentos cadastrados.

    Parâmetros:
        None.

    Retorno:
        json: Uma lista contendo os dados de todos os equipamentos cadastrados.
    """

    # Busca todos os equipamentos no banco de dados
    all_equipments = Equipment.query.all()

    # Serializa os dados de todos os equipamentos usando o esquema "equipments_schema"
    result = equipments_schema.dump(all_equipments)

    # Retorna a lista de equipamentos cadastrados como resposta
    return jsonify(result)
