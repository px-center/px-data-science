import pandas as pd
import numpy as np
import re
import unicodedata
from src.libs.lib import load_data_bq, gerar_hash_numerica, insert_into_bigquery

def processar_pontuacao_ocorrencias_academia():
    # 1) Carregar dados
    dfs = load_data_bq()
    dfs_original = dfs["drivers_occurences"].copy()
    df_original_table = pd.read_csv('src/data/tabela_de_pontuações.csv', delimiter=";")
    df_original_table_correspondeces = pd.read_csv('src/data/tabela_de_pontuações_correspondencias.csv', delimiter=";")

    # Ajustar colunas de correspondências
    columns = ['Código', 'Ocorrência DB-PX', 'Ocorrência Tabela - Academia', 'Pontuação']
    df_original_table_correspondeces.columns = columns

    # 2) Preprocessamento
    dfs_original['contract_start'] = pd.to_datetime(dfs_original['contract_start'])
    dfs_original['occurence_create'] = pd.to_datetime(dfs_original['occurence_create'])
    dfs_original['diff_horas'] = (dfs_original['contract_start'] - dfs_original['occurence_create']).dt.total_seconds() / 3600
    dfs_original = dfs_original.dropna(axis=0)

    # 3) Merge com tabela de correspondências
    dfs_original = dfs_original.merge(df_original_table_correspondeces, how='left', left_on="description", right_on="Ocorrência DB-PX")
    dfs_original.drop(["Código", "Ocorrência DB-PX", "Ocorrência Tabela - Academia"], axis=1, inplace=True)

    # 4) Corrigir pontuação de 'Desistência de contratos'
    mask = (dfs_original["description"] == "Desistência de contratos") & (dfs_original["diff_horas"] >= 36)
    dfs_original.loc[mask, "Pontuação"] = 0

    mask = (dfs_original["description"] == "Desistência de contratos") & (dfs_original["diff_horas"] < 36) & (dfs_original["diff_horas"] >= 12)
    dfs_original.loc[mask, "Pontuação"] = 125

    mask = (dfs_original["description"] == "Desistência de contratos") & (dfs_original["diff_horas"] < 12) & (dfs_original["diff_horas"] >= 0)
    dfs_original.loc[mask, "Pontuação"] = 185

    mask = (dfs_original["description"] == "Desistência de contratos") & (dfs_original["diff_horas"] < 0)
    dfs_original.loc[mask, "Pontuação"] = 125

    dfs_original.drop("diff_horas", axis=1, inplace=True)

    # 5) Ajuste para 'Dia agenciado'
    mask = dfs_original["description"] == "Dia agenciado"
    dfs_original.loc[mask, "Pontuação"] = -1 * dfs_original.loc[mask, "observation"].astype(float)

    # 6) Pivot para somar pontuação por motorista
    df = dfs_original.copy()
    df['Pontuação'] = pd.to_numeric(df['Pontuação'], errors='coerce').fillna(0)
    df['occurence_create'] = pd.to_datetime(df['occurence_create'])

    first_dates = df.groupby('driver_id')['occurence_create'].min().rename('first_event')
    last_dates = df.groupby('driver_id')['occurence_create'].max().rename('last_event')
    dias_elapsed = (last_dates - first_dates).dt.days.rename('Dias decorridos') * (-1)

    pivot_df = (
        df.pivot_table(
            index='driver_id',
            columns='description',
            values='Pontuação',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
    )
    pivot_df.columns.name = None
    pivot_df = pivot_df.merge(dias_elapsed.reset_index(), on='driver_id')

    # 7) Calcular pontuação total e definir ação
    columns_ocorrencias = pivot_df.columns.drop(['driver_id', 'Dias decorridos', 'Dia agenciado'])
    pivot_df['Pontuação'] = pivot_df[columns_ocorrencias].sum(axis=1)

    dfs_final = pivot_df.copy()
    dfs_final['Ação'] = "Nenhuma"
    dfs_final.loc[(dfs_final['Pontuação'] > 370) & (dfs_final['Pontuação'] <= 740), 'Ação'] = "Atualização"
    dfs_final.loc[dfs_final['Pontuação'] > 740, 'Ação'] = "Comitê"

    # 8) Sanitizar colunas para BigQuery
    def sanitize_column(col: str) -> str:
        nfkd = unicodedata.normalize('NFKD', col)
        only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
        clean = re.sub(r'[^0-9a-zA-Z_]', '_', only_ascii)
        if re.match(r'^[0-9]', clean):
            clean = '_' + clean
        clean = clean.lower()
        return clean[:300]

    dfs_final.columns = [sanitize_column(c) for c in dfs_final.columns]

    # 9) Salvar CSVs intermediários
    dfs_final.to_csv("src/data/tabela_ocorrencias_dbpx_com_a_pontuacao_academia.csv", index=False)
    df_original_table_correspondeces.to_csv("src/data/tabela-dbpx-pontuacao_academia.csv", index=False)

    # 10) Inserir no BigQuery
    texto = "12 - Peso das ocorrências comportamentais"
    hash_5_digitos = gerar_hash_numerica(texto)
    nome_tabela_bq = f"{hash_5_digitos}_pontuacao_ocorrencias_academia"
    insert_into_bigquery(dfs_final, table_id=nome_tabela_bq)

    print(f"Processamento concluído e dados inseridos na tabela: {nome_tabela_bq}")
