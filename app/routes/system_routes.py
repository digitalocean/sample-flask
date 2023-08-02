from flask import request, jsonify
from app import app, db
from ..models.system import System, SystemSchema

system_schema = SystemSchema()
systems_schema = SystemSchema(many=True)


@app.route('/system', methods=['POST'])
def add_system():
    """
    Rota que adiciona um novo sistema.

    Parâmetros:
        None (os dados do sistema são enviados pelo corpo da requisição como JSON).

    Retorno:
        json: Os dados do sistema adicionado.
    """

    # Obtém os dados do sistema enviados pelo corpo da requisição como JSON
    name = request.json['Name']
    address = request.json.get('Address')
    customer = request.json.get('Customer')

    # Cria uma nova instância do sistema usando os dados recebidos
    new_system = System(Name=name, Address=address, Customer=customer)

    # Adiciona o novo sistema ao banco de dados
    db.session.add(new_system)
    db.session.commit()

    # Retorna os dados do sistema adicionado como resposta com código de status 201 (Created)
    return jsonify(system_schema.dump(new_system)), 201


@app.route('/system/<int:id>', methods=['GET'])
def get_system(id):
    """
    Rota que busca um sistema pelo ID.

    Parâmetros:
        id (int): O ID do sistema a ser buscado.

    Retorno:
        json: Os dados do sistema encontrado ou uma mensagem de erro caso o sistema não seja encontrado.
    """

    # Busca o sistema no banco de dados pelo ID fornecido
    system = System.query.get(id)

    # Verifica se o sistema foi encontrado
    if system is not None:
        # Retorna os dados do sistema encontrado como resposta
        return jsonify(system_schema.dump(system))
    else:
        # Caso o sistema não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'system not found'}), 404
    
    
@app.route('/system/<int:id>', methods=['PUT'])
def update_system(id):
    """
    Rota que atualiza os dados de um sistema pelo ID.

    Parâmetros:
        id (int): O ID do sistema a ser atualizado.

    Retorno:
        json: Os dados do sistema atualizado ou uma mensagem de erro caso o sistema não seja encontrado.
    """

    # Busca o sistema no banco de dados pelo ID fornecido
    system = System.query.get(id)

    # Verifica se o sistema foi encontrado
    if system is not None:
        # Atualiza os dados do sistema com os novos dados enviados pelo corpo da requisição como JSON
        system.Name = request.json['Name']
        system.Address = request.json.get('Address')
        system.Customer = request.json.get('Customer')

        # Realiza a atualização no banco de dados
        db.session.commit()

        # Retorna os dados do sistema atualizado como resposta
        return jsonify(system_schema.dump(system))
    else:
        # Caso o sistema não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'system not found'}), 404
    

@app.route('/system/<int:id>', methods=['DELETE'])
def delete_system(id):
    """
    Rota que exclui um sistema pelo ID.

    Parâmetros:
        id (int): O ID do sistema a ser excluído.

    Retorno:
        json: Os dados do sistema excluído ou uma mensagem de erro caso o sistema não seja encontrado.
    """

    # Busca o sistema no banco de dados pelo ID fornecido
    system = System.query.get(id)

    # Verifica se o sistema foi encontrado
    if system is not None:
        # Remove o sistema do banco de dados
        db.session.delete(system)
        db.session.commit()

        # Retorna os dados do sistema excluído como resposta
        return jsonify(system_schema.dump(system))
    else:
        # Caso o sistema não seja encontrado, retorna um JSON com a mensagem de erro e código de status 404 (Not Found)
        return jsonify({'error': 'system not found'}), 404


@app.route('/system', methods=['GET'])
def get_systems():
    """
    Rota que busca todos os sistemas.

    Parâmetros:
        None.

    Retorno:
        json: Uma lista contendo os dados de todos os sistemas no banco de dados.
    """

    # Busca todos os sistemas no banco de dados
    all_systems = System.query.all()

    # Serializa os dados de todos os sistemas usando o esquema "SystemsSchema"
    result = systems_schema.dump(all_systems)

    # Retorna os dados de todos os sistemas como resposta
    return jsonify(result)
