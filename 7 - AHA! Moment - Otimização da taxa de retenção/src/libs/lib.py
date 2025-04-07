import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import time
import numpy as np


def insert_into_bigquery(
    df,
    table_id = "simulated_future_contracts",     
    dataset_id = "datascience",
    project_id = "formal-purpose-354320"
    ):
    """
    Insere os dados de um DataFrame no Google BigQuery.

    Parâmetros:
    - df: DataFrame do pandas contendo os dados a serem inseridos.
    - project_id: ID do projeto no Google Cloud.
    - dataset_id: Nome do dataset no BigQuery.
    - table_id: Nome da tabela no BigQuery.

    Retorna:
    - Confirmação da inserção.
    """


    cred_path = ".px-data-science-functions-formal-purpose-354320-07aada286f4e.json"
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Arquivo de credenciais '{cred_path}' não encontrado.")
    # print(cred_path)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

    table_ref = f"{project_id}.{dataset_id}.{table_id}"


    # Configuração do cliente do BigQuery
    client = bigquery.Client()

    # Configuração do job para truncar a tabela antes de inserir os dados
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    # Carregando o DataFrame para a tabela do BigQuery
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)

    # Espera o job terminar (opcional)
    job.result()

    print(f"Dados inseridos com sucesso na tabela: {table_ref}")


import hashlib

import hashlib
import os
from pathlib import Path

def gerar_hash_numerica(texto=None):
    if texto is None:
        # Caminho do script atual
        path = Path(__file__).resolve()
        # Pegar o nome da pasta dois níveis acima
        texto = path.parents[2].name

    # Gerar hash MD5
    hash_md5 = hashlib.md5(texto.encode()).hexdigest()
    # Converter os primeiros 8 caracteres da hash em um número inteiro
    numero = int(hash_md5[:8], 16)
    # Reduzir para 5 dígitos
    hash_5_digitos = numero % 100000
    print(f"Nome do estudo: {texto}")
    print(f"Hash numérica de 5 dígitos: {hash_5_digitos:05d}")
    return numero % 100000





from google.cloud import bigquery
def load_data_bq():
    import os
    import pandas as pd
    from google.cloud import bigquery

    # Configurações do pandas
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # Configura o cliente BigQuery com o dataset padrão
    client = bigquery.Client()
    default_dataset = bigquery.DatasetReference('formal-purpose-354320', 'px_motorista')
    job_config = bigquery.QueryJobConfig(default_dataset=default_dataset)

    # Diretório que contém os arquivos SQL
    queries_path = os.getenv("QUERIES_PATH", "src/queries")

    # Lista para armazenar os DataFrames
    dfs = []

    try:
        # Verifica se o diretório de queries existe
        if not os.path.isdir(queries_path):
            raise FileNotFoundError(f"O diretório de queries '{queries_path}' não foi encontrado.")

        # Itera sobre os arquivos .sql na pasta
        for query_file in os.listdir(queries_path):
            if query_file.endswith(".sql"):
                file_path = os.path.join(queries_path, query_file)
                with open(file_path, 'r') as file:
                    sql_query = file.read()

                try:
                    # Executa a query
                    query_job = client.query(sql_query, job_config=job_config)

                    # Converte o resultado para um DataFrame
                    df = query_job.result().to_dataframe()
                    dfs.append(df)

                    print(f"Query {query_file} executada com sucesso.")

                except Exception as e:
                    print(f"Erro ao executar a query {query_file}: {e}")
                    raise(e)
                    continue

    except FileNotFoundError as fnf_error:
        print(fnf_error)
        raise(fnf_error)
    except Exception as e:
        print(f"Erro geral: {e}")
        raise(fnf_error)

    # Verifica se há DataFrames carregados
    if dfs:
        print("Queries executadas com sucesso, DataFrames disponíveis na lista `dfs`.")
    else:
        print("Nenhuma query foi executada com sucesso ou não há arquivos SQL no diretório.")
    return dfs



import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv, find_dotenv

def load_data_db():
    # Configurações do pandas
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    
    # Carrega as variáveis de ambiente do .env
    load_dotenv(find_dotenv())
    host = os.getenv("DB_URL")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    conn_string = f"host={host} port={port} dbname={dbname} user={user} password={password}"

    # Diretório que contém os arquivos SQL
    queries_path = os.getenv("QUERIES_PATH", "src/queries/")
    
    # Dicionário para armazenar os DataFrames
    dataframes = {}

    try:
        # Estabelece conexão com o banco de dados
        conn = psycopg2.connect(conn_string)
        print("Conexão estabelecida com sucesso!")
        
        # Itera sobre os arquivos .sql na pasta
        for query_file in os.listdir(queries_path):
            if query_file.endswith(".sql"):
                file_path = os.path.join(queries_path, query_file)
                with open(file_path, 'r') as file:
                    sql_query = file.read()

                # Executa a query e obtém os resultados
                try:
                    cursor = conn.cursor()
                    cursor.execute(sql_query)
                    records = cursor.fetchall()
                    col_names = [desc[0] for desc in cursor.description]
                    
                    # Cria um DataFrame para cada query
                    df = pd.DataFrame(records, columns=col_names)
                    
                    # Extrai o nome do arquivo sem extensão e adiciona ao dicionário
                    key = os.path.splitext(query_file)[0]
                    dataframes[key] = df
                    
                    cursor.close()

                except Exception as e:
                    print(f"Erro ao executar a query {query_file}: {e}")
                    continue

        conn.close()

    except Exception as e:
        print("Ocorreu um erro ao conectar ao banco de dados:", e)
        return {}

    # Retorna o dicionário de DataFrames
    return dataframes


# id
# company_id -- id da empresa
# driver_id -- id do motorista
# origin_id -- pode ser  id de reembolso, pode ser id de bônus
# origin_type -- pode ser App/Models/Reimbursement, pode ser App/Models/DriverContractBonus
# created_at -- data de criação
# updated_at -- data de atualização
# reliability_score

# Index(['index', 'id', 'updated_at', 'contract_id', 'value', 'reason',
#        'reason_description', 'type', 'description', 'contract_days', 'price',
#        'contract_day_of_week', 'driver_id', 'driver_name', 'service_supplier',
#        'company_name', 'valor_por_dia', 'is_outlier_contract_days',
#        'is_outlier_description', 'is_outlier_contract_day_of_week',
#        'is_outlier_driver_id', 'is_outlier_company_name', 'is_outlier_value',
#        'is_outlier_value_real', 'PIP_score', 'PIP_score_index'],
#       dtype='object')


# Função para inserir os dados no banco de dados
def insert_data_db(df):
    def generate_bulk_insert_query(df):
        query = """
            INSERT INTO transaction_reliability_score (
            created_at, 
            updated_at,
            company_id,
            driver_id, 
            origin_id,
            origin_type,
            reliability_score
            )
            VALUES
            """
        values = []
        for _, row in df.iterrows():
            # Adicionando NOW() para created_at e updated_at
            values.append(f"""(
            NOW(), NOW(), 
            {int(row['company_id'])}, 
            {int(row['driver_id'])},
            {int(row['id'])}, 
            'App/Models/Reimbursement', 
            {int(row['PIP_score_index'])}            
            )""")

        # Concatenar os valores com vírgula
        query += ",\n".join(values) + ";"
        return query
    bulk_insert_query = generate_bulk_insert_query(df)
    # Código para se conectar ao banco PostgreSQL e executar a query
    try:
        # Conectar ao banco de dados usando variáveis de ambiente para segurança
        load_dotenv(find_dotenv())
        user = os.getenv("DB_USER_WRITE")
        password = os.getenv("DB_PASSWORD_WRITE")
        host = os.getenv("DB_URL_WRITE")
        port = os.getenv("DB_PORT_WRITE")
        database = os.getenv("DB_NAME_WRITE")
        conn_string = f"host={host} port={port} dbname={database} user={user} password={password}"

        # Carregar as variáveis de ambiente do arquivo .env
        load_dotenv(find_dotenv())

        # Conectar ao PostgreSQL
        connection = psycopg2.connect(conn_string)
        cursor = connection.cursor()
        from psycopg2 import sql
        timezone_query = sql.SQL("SET TIMEZONE TO {timezone}").format(timezone=sql.Literal('America/Sao_Paulo'))
        cursor.execute(timezone_query)
        # Executar a query de inserção em lote
        cursor.execute(bulk_insert_query)

        # Confirmar as transações
        connection.commit()

        print("Dados inseridos com sucesso!")

    except (Exception, psycopg2.Error) as error:
        print("Erro ao inserir dados no PostgreSQL", error)
        raise("Erro ao inserir dados no PostgreSQL")
    finally:
        # Fechar a conexão
        if connection:
            cursor.close()
            connection.close()

def calculate_transaction_reliability():
    
    try:
        dfs = load_data_bq()
    except Exception as e:
        dfs = load_data_db()

    df_reebolso = dfs[0]
    df_reebolso = df_reebolso.loc[:, ~df_reebolso.columns.duplicated()]
    df_reebolso = df_reebolso.sort_values("updated_at", ascending=True)
    # Função para identificar outliers dentro de cada categoria separadamente e criar nova coluna
    def label_outliers_by_category(df, category_column):
        """
        Função para identificar outliers dentro de cada categoria separadamente.
        O cálculo de outliers será feito por grupo categórico na coluna especificada.
        A função adiciona uma nova coluna 'is_outlier_<categoria>' ao DataFrame.

        Args:
        df: DataFrame contendo os dados.
        category_column: Nome da coluna categórica para agrupar.

        Returns:
        DataFrame com uma nova coluna indicando se o valor é um outlier.
        """
        # Função interna para calcular outliers com base no IQR
        def detect_outliers(group):
            upper_bound = group['valor_por_dia'].quantile(0.99)
            # Adiciona uma nova coluna com nome "is_outlier_<category>"
            group[f'is_outlier_{category_column}'] = (group['valor_por_dia'] > upper_bound)
            return group
        
        # Aplicar a função por grupo categórico
        df = df.groupby(category_column, group_keys=False).apply(detect_outliers)
        return df



    df = df_reebolso
    df["valor_por_dia"] = np.log(df["value"]**2 / (df["price"] * df["contract_days"] + 1) + 10)
    df = df[~df["valor_por_dia"].isna()]
    names = ['contract_days', 'description',
        'contract_day_of_week', 'driver_id',
        'company_name']

    for name in names:
        df = label_outliers_by_category(df, name)

    
    # Converta todas as colunas mencionadas para string
    columns_to_convert = [
        "is_outlier_description",
        "is_outlier_company_name",
        "is_outlier_driver_id",
        "is_outlier_contract_day_of_week",
        "is_outlier_contract_days",
    ]

    # Certifique-se de que as colunas podem armazenar strings
    df[columns_to_convert] = df[columns_to_convert].astype(str)

    # Atualize os valores nas colunas
    for column in columns_to_convert:
        mask = df[column] == "True"  # Certifique-se de que o valor booleano original é tratado corretamente
        df.loc[mask, column] = "F"
        df.loc[~mask, column] = "A"

    df['valor_por_dia'] = pd.to_numeric(df['valor_por_dia'], errors='coerce')  # Converter para numérico
    df = df.dropna(subset=['valor_por_dia'])  # Remover NaN
    df = df[np.isfinite(df['valor_por_dia'])]  # Remover infinitos


    quantiles = [0, 0.1667, 0.3333, 0.5, 0.6667, 0.999, 1]
    
    cutoffs = df['valor_por_dia'].dropna().quantile(quantiles)
    classes = ['A', 'B', 'C', 'D', 'E', 'F']
    df['is_outlier_value'] = pd.cut(df['valor_por_dia'], bins=cutoffs, labels=classes, include_lowest=True)
    cutoffs = df['value'].quantile(quantiles)
    classes = ['A', 'B', 'C', 'D', 'E', 'F']
    df['is_outlier_value_real'] = pd.cut(df['value'], bins=cutoffs, labels=classes, include_lowest=True)

    df["PIP_score"] =  df["is_outlier_value"].astype(str) +df["is_outlier_value_real"].astype(str) + df["is_outlier_contract_day_of_week"].astype(str) + df["is_outlier_description"].astype(str) + df["is_outlier_company_name"].astype(str)+ df["is_outlier_driver_id"].astype(str)
    # df.sort_values("valor_por_dia", ascending=False).head(1000)
    df = df.sort_values("PIP_score", ascending=False).reset_index()
    unique_pip_scores = {score: idx for idx, score in enumerate(df['PIP_score'].unique())}  
    df['PIP_score_index'] = df['PIP_score'].map(unique_pip_scores)
    df['PIP_score_index'] = (df['PIP_score_index'] / df['PIP_score_index'].max() * 1000).astype(int)
    return df


# Definir a função para calcular a distância usando Haversine
def haversine(lat1, lon1, lat2, lon2):
    # Raio da Terra em quilômetros
    R = 6371.0
    
    # Converter de graus para radianos
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    
    # Diferença entre as latitudes e longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Fórmula de Haversine
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Distância em quilômetros
    distance = R * c
    return distance



def calculate_value_statistics_by_category(df, category, value_column, operation):
    """
    Função para calcular estatísticas com base na operação especificada por contrato para cada categoria.
    Funciona para operações como 'mean', 'std', 'count' e também para 'diff'.

    Parâmetros:
    df: DataFrame com os dados.
    category: Categoria pela qual os valores serão agrupados (ex: 'driver_id', 'company_name').
    value_column: Coluna que contém os valores (ex: valor de reembolso).
    operation: Operação a ser realizada (ex: 'mean', 'std', 'count', 'diff').

    Retorna:
    DataFrame com as estatísticas adicionadas.
    """
    
    df = df.sort_values(by=[category, value_column])

    if operation == 'diff':
        # Aplicar diff() diretamente no grupo e adicionar a nova coluna
        df[category + '_' + value_column + "_diff"] = df.groupby(category)[value_column].diff()
    else:
        # Para outras operações como mean, std, count
        stats = df.groupby(category)[value_column].agg([operation]).reset_index()
        new_col_name = category + '_' + value_column + "_" + operation
        df = pd.merge(df, stats, on=category, how='left', suffixes=('', '_' + operation))
        df = df.rename(columns={operation: new_col_name})

    stats = df.groupby(category)[category + '_' + value_column + "_" + operation].agg(['mean']).reset_index()
    new_col_name = category + '_' + value_column + "_" + operation
    df = pd.merge(df, stats, on=category, how='left', suffixes=('', '_' + operation))
    df[new_col_name] = df['mean']
    df = df.drop('mean', axis=1)
    df = df.rename(columns={operation: new_col_name})

    df = df.fillna(0)
    return df


def calculate_transaction_reliability_by_flow():
    # Exemplo de uso[
    
    try:
        dfs = load_data_bq()
    except:
        dfs = load_data_db()
        
    df_reebolso = dfs[0]
    df_reebolso = df_reebolso.loc[:, ~df_reebolso.columns.duplicated()]
    df_reebolso = df_reebolso.sort_values("updated_at", ascending=True)
    df_reebolso.head()
    df = df_reebolso.copy()
    df = df.sort_values(["company_name", 'driver_id', 'updated_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['updated_at_days'] = (df['updated_at'] - pd.to_datetime('2000-01-01')).dt.days.astype(float)
    # Aplicar a função calculate_value_statistics_by_category
    df = calculate_value_statistics_by_category(df, 'company_name', 'updated_at_days', 'diff')
    df = calculate_value_statistics_by_category(df, 'company_name', 'value', 'mean')
    df = calculate_value_statistics_by_category(df, 'company_name', 'price', 'mean')
    df = calculate_value_statistics_by_category(df, 'company_name', 'value', 'std')
    df = calculate_value_statistics_by_category(df, 'company_name', 'driver_id', 'count')
    df["company_name_I"] = df['company_name_value_mean']**2 / (df['company_name_price_mean'] * df['company_name_updated_at_days_diff'])
    df["company_name_E"] = df["company_name_I"]**2 *(df["company_name_driver_id_count"] )

    df = calculate_value_statistics_by_category(df, 'driver_id', 'updated_at_days', 'diff')
    df = calculate_value_statistics_by_category(df, 'driver_id', 'value', 'mean')
    df = calculate_value_statistics_by_category(df, 'driver_id', 'price', 'mean')
    df = calculate_value_statistics_by_category(df, 'driver_id', 'value', 'std')
    df = calculate_value_statistics_by_category(df, 'driver_id', 'driver_id', 'count')
    df["driver_id_I"] = df['value']**2 / (df['price'] * df['contract_days'])
    df["driver_id_E"] = df["driver_id_I"]**2 *(df["driver_id_driver_id_count"] )
    df = df.fillna(0)
    df = df.replace([np.inf, -np.inf], 0)

    columns = ['updated_at_days',
        'company_name_updated_at_days_diff', 'company_name_value_mean',
        'company_name_price_mean', 'company_name_value_std',
        'company_name_driver_id_count', 'driver_id_updated_at_days_diff',
        'driver_id_value_mean', 'driver_id_price_mean', 'driver_id_value_std',
        'driver_id_driver_id_count']

    df = df.sort_values(["company_name", 'driver_id', 'updated_at'])
    df = df.drop(columns, axis=1)


    df["score"] = (df["company_name_I"] + df["driver_id_I"]) / 2
    df["score_E"] = (df["company_name_E"] + df["driver_id_E"]) / 2
    df["score_E"] = np.log(df["score_E"])
    df = df.sort_values("score_E", ascending=False)


    df["score_E"].replace([np.inf, -np.inf], np.nan, inplace=True)
    df["score_E"].fillna(0, inplace=True)
    df["score_E_1000"] = df["score_E"]
    df["score_E_1000"] = df["score_E_1000"] - df["score_E_1000"].min()
    df["score_E_1000"] = df["score_E_1000"] / df["score_E_1000"].max()
    df["score_E_1000"] = df["score_E_1000"] * -1000
    df["score_E_1000"] = df["score_E_1000"]  + 1000
    df["PIP_score_index"] = df["score_E_1000"]
    df.sort_values("score_E_1000", ascending=True).head(100)
    return df






gerar_hash_numerica(texto=None)
from datetime import datetime
agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Execução em: {agora}")