from flask import request, jsonify
from app import app, db
from ..models.subsystem import Subsystem, SubsystemSchema

subsystem_schema = SubsystemSchema()
subsystems_schema = SubsystemSchema(many=True)


@app.route('/subsystem', methods=['POST'])
def add_subsystem():
    """
    Rota que adiciona um novo subsistema.

    Parâmetros:
        None (os dados do subsistema são enviados pelo corpo da requisição como JSON).

    Retorno:
        json: Os dados do subsistema adicionado.
    """

    # Obtém os dados do subsistema enviados pelo corpo da requisição como JSON
    name = request.json['name']
    system_idsystem = request.json['system_idsystem']

    # Cria uma nova instância do subsistema usando os dados recebidos
    new_subsystem = Subsystem(name=name, system_idsystem=system_idsystem)

    # Adiciona o novo subsistema ao banco de dados
    db.session.add(new_subsystem)
    db.session.commit()

    # Retorna os dados do subsistema adicionado como resposta com código de status 201 (Created)
    return jsonify(subsystem_schema.dump(new_subsystem)), 201


@app.route('/subsystem/<int:id>', methods=['GET'])
def get_subsystem(id):
    """
    Rota que busca um subsistema pelo ID.

    Parâmetros:
        id (int): O ID do subsistema a ser buscado.

    Retorno:
        json: Os dados do subsistema encontrado ou uma mensagem de erro caso o subsistema não seja encontrado.
    """

    # Busca o subsistema no banco de dados pelo ID fornecido
    subsystem = Subsystem.query.get(id)

    # Verifica se o subsistema foi encontrado
    if subsystem is not None:
        # Retorna os dados do subsistema encontrado como resposta
        return jsonify(subsystem_schema.dump(subsystem))
    else:
        # Caso o subsistema não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'subsystem not found'}), 404


@app.route('/subsystem/<int:id>', methods=['PUT'])
def update_subsystem(id):
    """
    Rota que atualiza os dados de um subsistema pelo ID.

    Parâmetros:
        id (int): O ID do subsistema a ser atualizado.

    Retorno:
        json: Os dados do subsistema atualizado ou uma mensagem de erro caso o subsistema não seja encontrado.
    """

    # Busca o subsistema no banco de dados pelo ID fornecido
    subsystem = Subsystem.query.get(id)

    # Verifica se o subsistema foi encontrado
    if subsystem is not None:
        # Atualiza os dados do subsistema com os novos dados enviados pelo corpo da requisição como JSON
        subsystem.name = request.json['name']
        subsystem.system_idsystem = request.json['system_idsystem']

        # Realiza a atualização no banco de dados
        db.session.commit()

        # Retorna os dados do subsistema atualizado como resposta
        return jsonify(subsystem_schema.dump(subsystem))
    else:
        # Caso o subsistema não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'subsystem not found'}), 404


@app.route('/subsystem/<int:id>', methods=['DELETE'])
def delete_subsystem(id):
    """
    Rota que exclui um subsistema pelo ID.

    Parâmetros:
        id (int): O ID do subsistema a ser excluído.

    Retorno:
        json: Os dados do subsistema excluído ou uma mensagem de erro caso o subsistema não seja encontrado.
    """

    # Busca o subsistema no banco de dados pelo ID fornecido
    subsystem = Subsystem.query.get(id)

    # Verifica se o subsistema foi encontrado
    if subsystem is not None:
        # Remove o subsistema do banco de dados
        db.session.delete(subsystem)
        db.session.commit()

        # Retorna os dados do subsistema excluído como resposta
        return jsonify(subsystem_schema.dump(subsystem))
    else:
        # Caso o subsistema não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'subsystem not found'}), 404


@app.route('/subsystem', methods=['GET'])
def get_subsystems():
    """
    Rota que busca todos os subsistemas.

    Parâmetros:
        None.

    Retorno:
        json: Uma lista contendo os dados de todos os subsistemas no banco de dados.
    """

    # Busca todos os subsistemas no banco de dados
    all_subsystems = Subsystem.query.all()

    # Serializa os dados de todos os subsistemas usando o esquema "SubsystemsSchema"
    result = subsystems_schema.dump(all_subsystems)

    # Retorna os dados de todos os subsistemas como resposta
    return jsonify(result)
