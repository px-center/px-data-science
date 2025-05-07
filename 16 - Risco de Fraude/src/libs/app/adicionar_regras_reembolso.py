from lib import *
"""
Regras de risco em reembolsos
-----------------------------
Este script lê um CSV com dados de reembolsos, cria **apenas** as colunas-bandeira
(`True` / `False`) correspondentes às nove regras de fraude definidas pelo especialista
e devolve um DataFrame pronto para análise posterior.

📌 Colunas adicionadas
    regra_1_valor_contrato
    regra_2_valor_maior_3000
    regra_3_tres_maiores_500
    regra_4_dois_maiores_1000
    regra_5_total_maior_70p_contrato
    regra_6_aprovacao_rapida
    regra_7_horario_tarde
    regra_8_variacao_ambas_maior_30
    regra_9_variacao_valor_dias_agenciado_maior_30
"""

import pandas as pd


def adicionar_regras_reembolso() -> pd.DataFrame:
    # ────────────────────────────────
    # 1) Carregamento e pré-processamento mínimo
    # ────────────────────────────────
    dfs = load_data_bq()
    df = dfs["reembolsos"]

    date_cols = [
        "Data da criação do reembolso",
        "Data da ultima atualização do reembolso",
        "Data da aprovação ou rejeição do reembolso",
    ]
    df[date_cols] = df[date_cols].apply(
        pd.to_datetime, errors="coerce", utc=False  # assume fuso local já embutido
    )

    # ────────────────────────────────
    # 2) Regras INDIVIDUAIS (por transação)
    # ────────────────────────────────
    df["regra_1_valor_contrato"] = (
        # (df["Valor do contrato"] >= 500)
        # & 
        (df["Valor total do reembolso"] >= 0.5 * df["Valor do contrato"])
    )

    df["regra_2_valor_maior_3000"] = df["Valor total do reembolso"] > 3000

    df["regra_6_aprovacao_rapida"] = (
        df["Data da aprovação ou rejeição do reembolso"].notna()
        & df["Data da criação do reembolso"].notna()
        & (
            (
                df["Data da aprovação ou rejeição do reembolso"]
                - df["Data da criação do reembolso"]
            ).dt.total_seconds()
            / 60
            < 15
        )
        #& (df["Valor total do reembolso"] > 500)
    )

    df["regra_7_horario_tarde"] = (
        df["Data da criação do reembolso"].dt.hour >= 21
    ) & (df["Valor total do reembolso"] > 300)

    # ────────────────────────────────
    # 3) Regras AGREGADAS (por dia | transportadora | motorista)
    # ────────────────────────────────
    df["Data da criação do reembolso Date"] = df[
        "Data da criação do reembolso"
    ].dt.date

    agrupado = (
        df.groupby(
            [
                "Data da criação do reembolso Date",
                "Nome da transportadora",
                "Nome do motorista",
                "Valor do contrato",
                "Número de dias agenciados do contrato",
            ],
            as_index=False,
        )
        .agg(
            total_reembolsos=("Valor total do reembolso", "sum"),
            num_reembolsos=("Valor total do reembolso", "count"),
            num_reembolsos_alto_valor=(
                "Valor total do reembolso",
                lambda x: (x > 500).sum(),
            ),
            num_reembolsos_valor_muito_alto=(
                "Valor total do reembolso",
                lambda x: (x > 1000).sum(),
            ),
        )
        .sort_values(
            ["Nome da transportadora", "Nome do motorista", "Data da criação do reembolso Date"]
        )
    )

    # Regras 3, 4, 5
    agrupado["regra_3_tres_maiores_500"] = agrupado[
        "num_reembolsos_alto_valor"
    ] >= 3
    agrupado["regra_4_dois_maiores_1000"] = agrupado[
        "num_reembolsos_valor_muito_alto"
    ] >= 2
    agrupado["regra_5_total_maior_70p_contrato"] = (
        agrupado["total_reembolsos"] > 0.7 * agrupado["Valor do contrato"]
    )

    # Variações p/ regras 8 e 9
    agrupado["variacao_num_reembolsos"] = (
        agrupado.groupby(["Nome da transportadora", "Nome do motorista"])["num_reembolsos"]
        .pct_change()
        .abs()
    )
    agrupado["variacao_total_reembolsos"] = (
        agrupado.groupby(["Nome da transportadora", "Nome do motorista"])["total_reembolsos"]
        .pct_change()
        .abs()
    )

    agrupado.dropna(
        subset=["variacao_num_reembolsos", "variacao_total_reembolsos"], inplace=True
    )

    agrupado["regra_8_variacao_ambas_maior_30"] = (
        (agrupado["variacao_num_reembolsos"] >= 0.30)
        & (agrupado["variacao_total_reembolsos"] >= 0.30)
    )

    agrupado["regra_9_variacao_valor_dias_agenciado_maior_30"] = (
        (agrupado["variacao_total_reembolsos"] / agrupado["Número de dias agenciados do contrato"])
        .abs()
        >= 0.30
    )

    # ────────────────────────────────
    # 4) Junta regras agregadas de volta ao DataFrame principal
    # ────────────────────────────────
    df = df.merge(
        agrupado[
            [
                "Data da criação do reembolso Date",
                "Nome da transportadora",
                "Nome do motorista",
                "regra_3_tres_maiores_500",
                "regra_4_dois_maiores_1000",
                "regra_5_total_maior_70p_contrato",
                "regra_8_variacao_ambas_maior_30",
                "regra_9_variacao_valor_dias_agenciado_maior_30",
            ]
        ],
        on=[
            "Data da criação do reembolso Date",
            "Nome da transportadora",
            "Nome do motorista",
        ],
        how="left",
    )

    # Qualquer NaN virou False
    regra_cols = [c for c in df.columns if c.startswith("regra_")]
    df[regra_cols] = df[regra_cols].fillna(False)

    # Remove coluna auxiliar de data
    df.drop(columns="Data da criação do reembolso Date", inplace=True)

    columns = [ 'regra_1_valor_contrato', 'regra_2_valor_maior_3000',
       'regra_6_aprovacao_rapida', 'regra_7_horario_tarde',
       'regra_3_tres_maiores_500', 'regra_4_dois_maiores_1000',
       'regra_5_total_maior_70p_contrato', 'regra_8_variacao_ambas_maior_30',
       'regra_9_variacao_valor_dias_agenciado_maior_30']
    df["Risco"] = df[columns].mean(axis=1)

    texto = "16 - Risco de Fraude"
    hash_5_digitos = gerar_hash_numerica(texto)
    nome_tabela_bq = f"{hash_5_digitos}_risco_fraude_reembolso"
    insert_into_bigquery(df, table_id=nome_tabela_bq)

    print(f"Processamento concluído e dados inseridos na tabela: {nome_tabela_bq}")
    return df


