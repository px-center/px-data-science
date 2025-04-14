import os

# Valor secreto para proteger os arquivos estáticos
API_SECRET = os.environ.get("API_SECRET", "supersecret")

def is_authorized(request):
    """
    Verifica se a requisição possui autorização válida.
    Espera um header "Authorization" com o valor "Bearer <API_SECRET>".
    """
    auth_header = request.headers.get("Authorization")
    return auth_header == f"Bearer {API_SECRET}"

def get_static_file(file_path, content_type):
    """
    Lê o arquivo local e retorna seu conteúdo com o content-type apropriado.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        headers = {'Content-Type': content_type, 'Access-Control-Allow-Origin': '*'}
        return (content, 200, headers)
    except Exception as e:
        return (f"Erro ao ler o arquivo {file_path}: {str(e)}", 500, {'Access-Control-Allow-Origin': '*'})
