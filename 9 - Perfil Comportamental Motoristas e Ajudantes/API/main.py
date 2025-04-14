import functions_framework
from static_server import get_static_file
from data_processing import get_request_data, process_data

# Senha predefinida para liberar o acesso (por exemplo, "1234")
VERIFICATION_PASSWORD = "8763"

@functions_framework.http
def hello_http(request):
    # Responde a requisições OPTIONS para pré-verificação CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)

    # Para ambos GET e POST, vamos extrair o parâmetro ou o campo "password"
    password_from_query = request.args.get("verificationCode") if request.method == 'GET' else None
    password_from_form = request.form.get("verificationCode") if request.method == 'POST' else None

    # Determine o código informado, priorizando (para POST) o campo do formulário e (para GET) a query string
    current_password = password_from_form if password_from_form is not None else password_from_query

    # Se o código não for informado ou estiver incorreto, retorne verification.html, exceto se for requisitado algum arquivo estático
    # Permite acesso livre aos arquivos CSS e JS
    if request.method == 'GET':
        url_path = request.path  # Ex.: /index.html, /style.css, /script.js
        if url_path == "/style.css":
            return get_static_file("style.css", "text/css")
        elif url_path == "/script.js":
            return get_static_file("script.js", "application/javascript")

        if url_path in ["/", "/index.html"]:
            if current_password != VERIFICATION_PASSWORD:
                return get_static_file("verification.html", "text/html")
            else:
                return get_static_file("index.html", "text/html")
        else:
            return ("Arquivo não encontrado", 404, {'Access-Control-Allow-Origin': '*'})

    # Para requisições POST
    if request.method == 'POST':
        # Se o campo password não foi informado ou está incorreto, retorna verification.html
        if current_password != VERIFICATION_PASSWORD:
            return get_static_file("verification.html", "text/html")

        # Se o envio contém apenas o campo password (fluxo de verificação) e está correto, retorna index.html
        # ou se o envio contém também os campos do questionário, processa os dados.
        if not (request.form.get("fullName") or request.form.get("cpf")):
            # Apenas verificação via POST
            return get_static_file("index.html", "text/html")
        else:
            full_name, cpf, uploaded_file = get_request_data(request)
            if not cpf or not full_name:
                return ("Campos 'cpf' e 'fullName' são obrigatórios", 400, {'Access-Control-Allow-Origin': '*'})
            result = process_data(full_name, cpf, uploaded_file)
            return (result, 200, {'Access-Control-Allow-Origin': '*'})
    
    return ("Method not supported", 405, {'Access-Control-Allow-Origin': '*'})
