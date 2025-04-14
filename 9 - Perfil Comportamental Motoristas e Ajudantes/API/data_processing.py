import json
from google.cloud import storage

def get_request_data(request):
    """
    Extrai os dados do formulário da requisição POST.
    Retorna: full_name, cpf, uploaded_file.
    """
    full_name = request.form.get('fullName')
    cpf = request.form.get('cpf')
    uploaded_file = request.files.get('file')  # Pode ser None se nenhum arquivo foi enviado
    return full_name, cpf, uploaded_file

def process_data(full_name, cpf, uploaded_file):
    """
    Processa os dados enviados:
      - Testa leitura/escrita no bucket;
      - Se houver arquivo, salva-o em {cpf}/{cpf}_{file_name};
      - Cria e salva um JSON de identificação em {cpf}/{cpf}_identification.json.
    Retorna uma mensagem com o status das operações.
    """
    bucket_name = "ds-drivers-interviews-data-acquisition"
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    # Teste opcional de leitura/escrita no bucket
    try:
        test_blob = bucket.blob("test.txt")
        test_blob.upload_from_string("Teste de leitura e escrita")
        content = test_blob.download_as_text()
        test_blob.delete()
        storage_status = f"Bucket read/write ok: {content}"
    except Exception as e:
        storage_status = f"Erro no bucket: {str(e)}"

    # Processa o arquivo se ele foi enviado
    if uploaded_file:
        file_name = uploaded_file.filename

        # Calcula o tamanho do arquivo
        uploaded_file.seek(0, 2)  # Vai para o fim do arquivo
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)     # Retorna ao início

        # Define o caminho no bucket: pasta {cpf} e nome {cpf}_{file_name}
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

    # Cria e salva o arquivo JSON de identificação na pasta {cpf}/ com nome {cpf}_identification.json
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
    return full_response
