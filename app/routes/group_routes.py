from flask import request, jsonify
from app import app, db
from ..models.group import Group, GroupSchema

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)

@app.route('/group', methods=['POST'])
def add_group():
    """
    Rota que adiciona um novo grupo.

    Parâmetros:
        None (os dados do grupo são enviados pelo corpo da requisição como JSON).

    Retorno:
        json: Os dados do grupo adicionado.
    """

    # Obtém os dados do grupo enviados pelo corpo da requisição como JSON
    name = request.json['name']
    description = request.json.get('description')

    # Cria uma nova instância do grupo usando os dados recebidos
    new_group = Group(name=name, description=description)

    # Adiciona o novo grupo ao banco de dados
    db.session.add(new_group)
    db.session.commit()

    # Retorna os dados do grupo adicionado como resposta com código de status 201 (Created)
    return jsonify(group_schema.dump(new_group)), 201

@app.route('/group/<int:id>', methods=['GET'])
def get_group(id):
    """
    Rota que busca um grupo pelo seu ID.

    Parâmetros:
        id (int): O ID do grupo a ser buscado.

    Retorno:
        json: Os dados do grupo encontrado ou uma mensagem de erro caso o grupo não seja encontrado.
    """

    # Busca o grupo no banco de dados pelo ID fornecido
    group = Group.query.get(id)

    # Verifica se o grupo foi encontrado
    if group is not None:
        # Retorna os dados do grupo encontrado como resposta
        return jsonify(group_schema.dump(group))
    else:
        # Caso o grupo não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'group not found'}), 404
    

@app.route('/group/<int:id>', methods=['PUT'])
def update_group(id):
    """
    Rota que atualiza um grupo existente.

    Parâmetros:
        id (int): O ID do grupo a ser atualizado.

    Retorno:
        json: Os dados do grupo atualizado ou uma mensagem de erro caso o grupo não seja encontrado.
    """

    # Busca o grupo no banco de dados pelo ID fornecido
    group = Group.query.get(id)

    # Verifica se o grupo foi encontrado
    if group is not None:
        # Atualiza os dados do grupo com base nos dados enviados pelo corpo da requisição como JSON
        group.name = request.json['name']
        group.description = request.json.get('description')

        # Realiza a atualização no banco de dados
        db.session.commit()

        # Retorna os dados do grupo atualizado como resposta
        return jsonify(group_schema.dump(group))
    else:
        # Caso o grupo não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'group not found'}), 404
    

@app.route('/group/<int:id>', methods=['DELETE'])
def delete_group(id):
    """
    Rota que deleta um grupo existente.

    Parâmetros:
        id (int): O ID do grupo a ser deletado.

    Retorno:
        json: Os dados do grupo deletado ou uma mensagem de erro caso o grupo não seja encontrado.
    """

    # Busca o grupo no banco de dados pelo ID fornecido
    group = Group.query.get(id)

    # Verifica se o grupo foi encontrado
    if group is not None:
        # Deleta o grupo do banco de dados
        db.session.delete(group)
        db.session.commit()

        # Retorna os dados do grupo deletado como resposta
        return jsonify(group_schema.dump(group))
    else:
        # Caso o grupo não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'group not found'}), 404
    

@app.route('/group', methods=['GET'])
def get_groups():
    """
    Rota que busca todos os grupos cadastrados.

    Parâmetros:
        None.

    Retorno:
        json: Uma lista contendo os dados de todos os grupos cadastrados.
    """

    # Busca todos os grupos no banco de dados
    all_groups = Group.query.all()

    # Serializa os dados de todos os grupos usando o esquema "groups_schema"
    result = groups_schema.dump(all_groups)

    # Retorna a lista de grupos cadastrados como resposta
    return jsonify(result)
