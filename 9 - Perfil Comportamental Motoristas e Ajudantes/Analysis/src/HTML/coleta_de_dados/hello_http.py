import functions_framework
import json
from google.cloud import storage

@functions_framework.http
def hello_http(request):
    # Responde a requisições OPTIONS para pré-verificação CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    bucket_name = "ds-drivers-interviews-data-acquisition"
    storage_status = "Teste de bucket não executado"
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        
        # Teste de leitura e escrita no bucket (opcional)
        test_blob = bucket.blob("test.txt")
        test_blob.upload_from_string("Teste de leitura e escrita")
        content = test_blob.download_as_text()
        test_blob.delete()
        storage_status = f"Bucket read/write ok: {content}"
    except Exception as e:
        storage_status = f"Erro no bucket: {str(e)}"
    
    # Recupera CPF e Nome completo enviados no formulário
    cpf = request.form.get('cpf')
    full_name = request.form.get('fullName')
    if not cpf or not full_name:
        return ("Campos 'cpf' e 'fullName' são obrigatórios", 400, {'Access-Control-Allow-Origin': '*'})
    
    # Se um arquivo foi enviado, salva-o na pasta {cpf}/ com o nome {cpf}_{file_name}
    if 'file' in request.files:
        uploaded_file = request.files['file']
        file_name = uploaded_file.filename

        # Calcula o tamanho do arquivo
        uploaded_file.seek(0, 2)  # Vai para o final do arquivo
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)     # Retorna ao início

        # Define o caminho no bucket para o arquivo enviado
        blob_path = f"{cpf}/{cpf}_{file_name}"
        blob = bucket.blob(blob_path)
        
        try:
            blob.upload_from_file(uploaded_file)
            storage_action = f"Arquivo salvo em {blob_path} no bucket."
        except Exception as e:
            storage_action = f"Erro ao salvar arquivo: {str(e)}"
    else:
        storage_action = "No file provided"
        file_size = 0
        file_name = "N/A"
    
    # Cria e salva o arquivo JSON de identificação na mesma pasta, com nome {cpf}_identification.json
    identification_data = {
        "fullName": full_name,
        "cpf": cpf
    }
    json_blob_path = f"{cpf}/{cpf}_identification.json"
    json_blob = bucket.blob(json_blob_path)
    try:
        json_content = json.dumps(identification_data)
        json_blob.upload_from_string(json_content, content_type='application/json')
        json_status = f"Arquivo de identificação salvo em {json_blob_path} no bucket."
    except Exception as e:
        json_status = f"Erro ao salvar arquivo de identificação: {str(e)}"
    
    response_text = (
        f"File Name: {file_name}, File Size: {file_size} bytes\n"
        f"{storage_action}\n{json_status}"
    )
    full_response = f"{response_text}\nBucket Status: {storage_status}"
    headers = {'Access-Control-Allow-Origin': '*'}
    return (full_response, 200, headers)