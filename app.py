from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = 'chave_secreta'  # Necessário para usar sessões

# Função para carregar dados do arquivo JSON
def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            return json.load(f)
    return []

# Função para salvar dados no arquivo JSON
def salvar_dados(arquivo, dados):
    with open(arquivo, 'w') as f:
        json.dump(dados, f, indent=4)

# Carregar dados no início
arquivo_dados = 'dados.json'
dados_armazenados = carregar_dados(arquivo_dados)

# Dados de login (login e senha fixos)
usuarios = {
    'admin': 'admin'
}

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica se o login é válido
        if username in usuarios and usuarios[username] == password:
            session['user'] = username  # Armazena o nome de usuário na sessão
            return redirect(url_for('index'))  # Redireciona para o sistema de banco de dados

        return jsonify({'message': 'Credenciais inválidas'}), 401

    return render_template('login.html')

# Verifica se o usuário está logado
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Rota principal
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Rota para armazenar os dados
@app.route('/armazenar_dados', methods=['POST', 'GET'])
@login_required
def armazenar_dados():
    if request.method == 'POST':
        email = request.form.get('email')
        plano = request.form.get('plano')
        comecou = request.form.get('comecou')
        saldo = request.form.get('saldo')

        if not all([email, plano, comecou, saldo]):
            return jsonify({'message': 'Por favor, preencha todos os campos'}), 400

        # Gera um token único
        token = str(uuid.uuid4())

        # Armazena os dados
        novo_dado = {
            'Token': token,
            'E-mail': email,
            'Plano Investido': plano,
            'Começou com quanto': comecou,
            'Saldo Total': saldo
        }
        dados_armazenados.append(novo_dado)
        salvar_dados(arquivo_dados, dados_armazenados)

        return jsonify({'message': 'Dados armazenados com sucesso', 'data': novo_dado}), 200

    elif request.method == 'GET':
        # Retorna todos os dados armazenados
        return jsonify(dados_armazenados), 200

# Rota para buscar por token
@app.route('/buscar_por_token', methods=['POST'])
@login_required
def buscar_por_token():
    token = request.form.get('token')

    # Procura o token nos dados armazenados
    for dado in dados_armazenados:
        if dado['Token'] == token:
            return jsonify(dado), 200

    # Se não encontrar, retorna uma mensagem de erro
    return jsonify({'message': 'Token não encontrado'}), 404

# Rota para deletar dados pelo token
@app.route('/deletar_dado', methods=['POST'])
@login_required
def deletar_dado():
    token = request.form.get('token')

    # Lê o arquivo JSON
    dados = carregar_dados(arquivo_dados)

    # Filtra os dados para remover o item com o token correspondente
    dados_filtrados = [dado for dado in dados if dado['Token'] != token]

    # Salva a nova lista sem o dado removido
    salvar_dados(arquivo_dados, dados_filtrados)

    # Atualiza a variável global
    global dados_armazenados
    dados_armazenados = dados_filtrados

    return jsonify({'message': 'Dado deletado com sucesso'}), 200

# Rota para atualizar dados pelo token
@app.route('/atualizar_dado', methods=['POST'])
@login_required
def atualizar_dado():
    token = request.form.get('token')
    email = request.form.get('email')
    plano = request.form.get('plano')
    comecou = request.form.get('comecou')
    saldo = request.form.get('saldo')

    # Verifica se todos os campos foram fornecidos
    if not all([token, email, plano, comecou, saldo]):
        return jsonify({'message': 'Por favor, preencha todos os campos'}), 400

    # Carrega os dados do arquivo JSON
    dados = carregar_dados(arquivo_dados)

    # Procura o dado com o token correspondente e atualiza os valores
    for dado in dados:
        if dado['Token'] == token:
            dado['E-mail'] = email
            dado['Plano Investido'] = plano
            dado['Começou com quanto'] = comecou
            dado['Saldo Total'] = saldo

            # Salva os dados atualizados no arquivo JSON
            salvar_dados(arquivo_dados, dados)

            # Atualiza a variável global
            global dados_armazenados
            dados_armazenados = dados

            return jsonify({'message': 'Dados atualizados com sucesso!'}), 200

    # Se o token não for encontrado, retorna um erro
    return jsonify({'message': 'Token não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)
