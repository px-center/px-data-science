
import pandas as pd
import numpy as np
import statsmodels.api as sm

def regressao_exponencial(df: pd.DataFrame, date_col: str, volume_col: str):
    """
    Aplica regressão exponencial sobre os dados de volume por data e calcula uma proxy para o desvio padrão.
    
    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    date_col (str): Nome da coluna contendo as datas.
    volume_col (str): Nome da coluna contendo os volumes.
    
    Retorna:
    pd.DataFrame: DataFrame original com colunas adicionais de previsão e desvio padrão estimado.
    """
    df = df.copy()
    
    # Garantir que a coluna de data está no formato datetime
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    # Criar variável de tempo em dias
    df["time"] = (df[date_col] - df[date_col].min()).dt.total_seconds() / (60 * 60 * 24)
    
    # Aplicar transformação logarítmica para regressão exponencial
    df["log_volume"] = np.log(df[volume_col])
    
    # Ajustar regressão exponencial
    X_exp = sm.add_constant(df["time"])
    y_exp = df["log_volume"]
    model_exp = sm.OLS(y_exp, X_exp).fit()
    
    # Fazer previsões e reverter transformação logarítmica
    df["predicted_exp"] = np.exp(model_exp.predict(X_exp))
    
    # Calcular erro absoluto como proxy para o desvio padrão
    df["std_proxy"] = np.abs(df[volume_col] - df["predicted_exp"])
    
    # Aplicar transformação logarítmica ao desvio padrão proxy
    df["log_std_proxy"] = np.log(df["std_proxy"] + 1e-6)  # Adiciona pequena constante para evitar log(0)
    
    # Ajustar regressão exponencial para o desvio padrão proxy
    X_std = sm.add_constant(df["time"])
    y_std = df["log_std_proxy"]
    model_std = sm.OLS(y_std, X_std).fit()
    
    # Fazer previsões e reverter transformação logarítmica
    df["predicted_std"] = np.exp(model_std.predict(X_std))
    
    return df, model_exp, model_std


import pandas as pd

def process_contracts(df_volumes):
    # Converter colunas para datetime
    df_volumes['created_at'] = pd.to_datetime(df_volumes['created_at'])
    # df_volumes['start_at'] = pd.to_datetime(df_volumes['start_at'])
    
    # Ordenar pelo campo created_at
    df_volumes = df_volumes.sort_values("created_at")
    
    # Adicionar a coluna com a data sem hora
    df_volumes['date'] = df_volumes['created_at'].dt.date  # Apenas a data no formato "AAAA-MM-DD"
    
    # Extrair metadados
    df_volumes['hour_of_day'] = df_volumes['created_at'].dt.hour  # Hora do dia
    df_volumes['year'] = df_volumes['created_at'].dt.year  # Ano
    df_volumes['month'] = df_volumes['created_at'].dt.month  # Mês
    df_volumes['day'] = df_volumes['created_at'].dt.day  # Dia
    
    # Definir o período do dia
    def get_period(hour):
        if 5 <= hour < 12:
            return "Manhã"
        elif 12 <= hour < 18:
            return "Tarde"
        else:
            return "Noite"
    
    df_volumes['period_of_day'] = df_volumes['hour_of_day'].apply(get_period)  # Período do dia
    
    # Outros metadados
    df_volumes['day_of_week'] = df_volumes['created_at'].dt.day_name()  # Dia da semana
    df_volumes['day_of_month'] = df_volumes['created_at'].dt.day  # Dia do mês
    df_volumes['day_of_year'] = df_volumes['created_at'].dt.dayofyear  # Dia do ano
    df_volumes['month_of_year'] = df_volumes['created_at'].dt.month  # Mês do ano
    df_volumes['quarter_of_year'] = df_volumes['created_at'].dt.quarter  # Trimestre do ano
    df_volumes['semester_of_year'] = df_volumes['created_at'].dt.month.apply(lambda x: 1 if x <= 6 else 2)  # Semestre do ano
    
    # Calcular volume de contratos por data
    df_volumes["volume_by_date"] = df_volumes.groupby("date")["date"].transform("count")
    return df_volumes
    
import numpy as np
import pandas as pd
import scipy.stats as stats
from itertools import combinations

def process_posterior_estimations(df_volumes, df_estimate, columns=['day_of_week', 'month']):
    if df_estimate is None or df_volumes is None:
        raise ValueError("Os DataFrames df_volumes e df_estimate devem ser fornecidos.")
    
    # Criar colunas para armazenar resultados se não existirem
    for col in ["posterior_mean", "posterior_std", "posterior_mode"]:
        if col not in df_estimate.columns:
            df_estimate[col] = np.nan

    # Criar valores x para estimar PDFs
    x_values = np.linspace(df_volumes["volume_by_date"].min(), df_volumes["volume_by_date"].max(), 500)

    def calculate_kde_pdf(data, x_values):
        if len(data) > 1 and np.std(data) > 0:
            kde = stats.gaussian_kde(data)
            pdf = kde(x_values)
            return pdf / pdf.sum()
        else:
            return np.ones_like(x_values) / len(x_values)

    posterior_means = []
    posterior_stds = []
    posterior_modes = []
    
    for i in range(len(df_estimate)):
        # print(f"Processando {i+1}/{len(df_estimate)} ({(i+1)/len(df_estimate)*100:.2f}%)")
        df_estimate_sub = df_estimate.iloc[i][columns]
        df_pdfs = pd.DataFrame({"x_values": x_values})
        
        priori_pdf = calculate_kde_pdf(df_volumes["volume_by_date"], x_values)
        df_pdfs["priori"] = priori_pdf

        for column in df_estimate_sub.index:
            value = df_estimate_sub[column]
            if column in df_volumes.columns:
                df_filtered = df_volumes[df_volumes[column] == value]["volume_by_date"]
                likelihood_pdf = calculate_kde_pdf(df_filtered, x_values)
                df_pdfs[f"{column}-{value}"] = likelihood_pdf

        for col1, col2 in combinations(df_estimate_sub.index, 2):
            value1, value2 = df_estimate_sub[col1], df_estimate_sub[col2]
            if col1 in df_volumes.columns and col2 in df_volumes.columns:
                df_filtered = df_volumes[(df_volumes[col1] == value1) & (df_volumes[col2] == value2)]["volume_by_date"]
                joint_pdf = calculate_kde_pdf(df_filtered, x_values)
                df_pdfs[f"{col1}-{value1}_{col2}-{value2}"] = joint_pdf

        if df_pdfs.shape[1] > 1:
            posterior_pdf = df_pdfs.iloc[:, 1:].prod(axis=1)
            posterior_pdf /= posterior_pdf.sum()
            df_pdfs["posteriori"] = posterior_pdf

            posterior_samples = np.random.choice(df_pdfs["x_values"], size=1000, p=df_pdfs["posteriori"])
            posterior_mean = np.mean(posterior_samples)
            posterior_std = np.std(posterior_samples)
            posterior_mode = stats.mode(posterior_samples, keepdims=True)[0][0]
        else:
            posterior_mean, posterior_std, posterior_mode = np.nan, np.nan, np.nan

        posterior_means.append(posterior_mean)
        posterior_stds.append(posterior_std)
        posterior_modes.append(posterior_mode)
        
        # print(posterior_std)
        # print(posterior_mean)

    df_estimate["posterior_mean"] = posterior_means
    df_estimate["posterior_std"] = posterior_stds
    df_estimate["posterior_mode"] = posterior_modes
    
    return df_estimate

import pandas as pd

def generate_df_estimate(start_date: str, end_date: str, columns=['day_of_week', 'month', 'year']):
    """
    Gera um DataFrame contendo datas e metadados entre duas datas definidas.
    
    Parâmetros:
        start_date (str): Data inicial no formato 'YYYY-MM-DD'.
        end_date (str): Data final no formato 'YYYY-MM-DD'.
        columns (list): Lista de colunas de metadados a serem incluídas.

    Retorna:
        pd.DataFrame: DataFrame contendo a data e os metadados especificados.
    """
    # Converter strings para objetos datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Criar intervalo de datas
    date_range = pd.date_range(start=start_date, end=end_date)
    df = pd.DataFrame({'date': date_range})
    
    # Adicionar metadados
    df['day_of_week'] = df['date'].dt.day_name()
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    
    return df



import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime, timedelta

def run_predict(df_volumes, past_days=365, next_days=365):
    """
    Realiza previsão com base em contratos passados e gera estimativas futuras.
    
    Parâmetros:
    df_volumes (pd.DataFrame): DataFrame contendo os dados de contratos.
    past_days (int): Número de dias passados a considerar.
    next_days (int): Número de dias futuros a prever.
    
    Retorna:
    pd.DataFrame: DataFrame contendo previsões futuras ajustadas.
    """
    df_volumes = df_volumes.copy()
    

    df_volumes = process_contracts(df_volumes).drop_duplicates("date")
    df_volumes = df_volumes.sort_values("date").tail(365)
    
    df_volumes, model_exp, model_std = regressao_exponencial(df_volumes, date_col="date", volume_col="volume_by_date")
    
    df_volumes["volume_by_date_original"] = df_volumes["volume_by_date"]
    df_volumes["volume_by_date"] = (df_volumes["volume_by_date"] - df_volumes["predicted_exp"]) / df_volumes["predicted_std"]
    
    start_date = (datetime.today() - timedelta(days=past_days)).strftime('%Y-%m-%d')
    end_date = (datetime.today() + timedelta(days=next_days)).strftime('%Y-%m-%d')
    
    df_estimate = generate_df_estimate(start_date, end_date, columns=['day_of_week', 'month', 'year'])
    df_estimate = process_posterior_estimations(df_volumes, df_estimate.copy(), columns=['day_of_week', 'month'])
    df_estimate["date"] = pd.to_datetime(df_estimate["date"], errors="coerce")
    df_estimate["time"] = (df_estimate["date"] - df_volumes["date"].min()).dt.total_seconds() / (60 * 60 * 24)
    
    X_exp = sm.add_constant(df_estimate["time"])
    df_estimate["predicted_exp"] = np.exp(model_exp.predict(X_exp))
    df_estimate["predicted_std"] = np.exp(model_std.predict(X_exp))
    
    df_estimate["posterior_mean_original"] = df_estimate["posterior_mean"]
    df_estimate["posterior_mean"] = df_estimate["posterior_mean"] * df_estimate["predicted_std"] + df_estimate["predicted_exp"]
    df_estimate["posterior_std"] = (df_estimate["posterior_std"] ** 2 + df_estimate["predicted_std"] ** 2)**0.5
    
    columns = ['date', 'day_of_week', 'month', 'year',
    'posterior_std', 'posterior_mean']
    df = df_estimate[columns].merge(df_volumes[["date", "volume_by_date_original"]], how='left', on="date")

    df_results = pd.DataFrame()
    df_results["date"] = df["date"]
    df_results["volumes_by_date_error"] = df["posterior_std"] 
    df_results["volumes_by_date_prediction"] = df["posterior_mean"] 
    df_results["volumes_by_date_real"] = df["volume_by_date_original"] 
    df_results["created_at"] = [pd.Timestamp.now()] * len(df_results)

    return df_results

from google.cloud import bigquery
import pandas as pd
import os
import pandas as pd
from google.cloud import bigquery

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


    cred_path = "px-data-science-functions-formal-purpose-354320-07aada286f4e.json"
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




import pandas as pd

def process_regions(df):
    # 🚀 Carregar os dados das regiões
    df_regions = pd.read_csv("data/RELATORIO_DTB_BRASIL_DISTRITO.csv", delimiter=";")

    # 🔹 Remover duplicatas para garantir apenas uma correspondência por cidade e estado
    df_regions = df_regions[["Nome_Município", "Nome_UF", "Nome_Mesorregião"]].drop_duplicates()

    # 🚀 Realizando o merge sem duplicar linhas de `df`
    df_merged = df.merge(
        df_regions,
        left_on=["city", "state"],
        right_on=["Nome_Município", "Nome_UF"],
        how="left"
    )

    # 🔹 Remover colunas desnecessárias após o merge
    df_merged.drop(columns=["Nome_Município", "Nome_UF"], inplace=True)

    # 🔹 Renomear coluna para `region`
    df_merged = df_merged.rename(columns={"Nome_Mesorregião": "region"})

    return df_merged


def run_predict_filtered(df_candidates_filterd, df_contracts_filtered, past_days=365, next_days=365):
       df_volumes = df_contracts_filtered
       df_volumes = df_volumes[['created_at']]
       df_volumes["start_at"] = df_volumes["created_at"]
       df = run_predict(df_volumes, past_days, next_days)
       df_contracts = df.copy()

       df_volumes = df_candidates_filterd
       df_volumes = df_volumes[['created_at']]
       df_volumes["start_at"] = df_volumes["created_at"]
       df = run_predict(df_volumes, past_days, next_days)
       df_candidates = df.copy()

       df_rates = pd.DataFrame()
       df_rates["date"] = df_candidates["date"]
       df_rates["volumes_by_date_error"] = (
       df_candidates["volumes_by_date_prediction"] /  df_contracts["volumes_by_date_prediction"] *
       (
       (df_candidates["volumes_by_date_error"] / df_candidates["volumes_by_date_prediction"] ) ** 2 + 
       (df_contracts["volumes_by_date_error"] / df_contracts["volumes_by_date_prediction"] ) ** 2
       )**0.5
       )
       df_rates["volumes_by_date_prediction"] = df_candidates["volumes_by_date_prediction"] /  df_contracts["volumes_by_date_prediction"] 

       df_rates["volumes_by_date_real"] = df_candidates["volumes_by_date_real"] /  df_contracts["volumes_by_date_real"]
       df_results = pd.DataFrame()
       df_results["date"] = df_contracts["date"]
       df_results["contract_by_date_error"] = df_contracts["volumes_by_date_error"] 
       df_results["contract_by_date_prediction"] = df_contracts["volumes_by_date_prediction"]  
       df_results["contract_by_date_real"] = df_contracts["volumes_by_date_real"] 
       df_results["candidates_by_date_error"] = df_candidates["volumes_by_date_error"] 
       df_results["candidates_by_date_prediction"] = df_candidates["volumes_by_date_prediction"]
       df_results["candidates_by_date_real"] = df_candidates["volumes_by_date_real"]
       df_results["rate_by_date_error"] = df_rates["volumes_by_date_error"] 
       df_results["rate_by_date_prediction"] = df_rates["volumes_by_date_prediction"] 
       df_results["rate_by_date_real"] = df_rates["volumes_by_date_real"] 
       return df_results, df_candidates, df_contracts, df_rates



import pandas as pd
import numpy as np

import numpy as np
def apply_filters_freq(df, colunas, valores):
    """
    Filtra o DataFrame baseado nas colunas e valores fornecidos e calcula a proporção
    das linhas que atendem aos filtros em relação ao conjunto original.

    Parâmetros:
    - df: DataFrame Pandas original
    - colunas: Lista de colunas a serem filtradas
    - valores: Lista de listas contendo os valores aceitáveis para cada coluna
    
    Retorna:
    - Um array NumPy contendo a proporção para cada linha do DataFrame.
    """

    if len(df) == 0:
        return np.zeros(len(df))  # Retorna um array vazio se o DataFrame for vazio

    # Criar um array booleano de filtro usando numpy (mais eficiente)
    condicao = np.ones(len(df), dtype=bool)
    print(len(colunas))
    for i in np.arange(0,len(colunas),1):
       
        condicao &= df[colunas[i]] == valores[i] 
        
    # # Calcula a proporção das linhas que atendem aos filtros
    proporcao = condicao.sum() / len(df)

    # Retorna um array com essa proporção, para ser aplicado a cada linha
    return proporcao

