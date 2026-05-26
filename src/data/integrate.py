"""Integração das bases SIH, SIM e população em base analítica única. Autora: Nathalia Adriele"""

import pandas as pd
import numpy as np
from loguru import logger

from src.config.settings import (
    CID10_DIABETES,
    DATA_EXTRACAO,
    DATA_PROCESSAMENTO,
    PROCESSED_DIR,
)


def integrate_data(
    df_sih: pd.DataFrame,
    df_sim: pd.DataFrame,
    df_pop: pd.DataFrame,
) -> pd.DataFrame:
    """Integra as bases SIH, SIM e população em uma base analítica final."""
    logger.info("Iniciando integração das bases de dados...")
    logger.info(f"  SIH: {len(df_sih)} registros")
    logger.info(f"  SIM: {len(df_sim)} registros")
    logger.info(f"  População: {len(df_pop)} registros")

    for df in [df_sih, df_sim, df_pop]:
        for col in ["ano", "mes"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                df[col] = df[col].astype(int)
        for col in ["uf", "codigo_municipio", "sexo", "faixa_etaria", "cid10"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

    chaves_sih_sim = ["ano", "mes", "uf", "codigo_municipio", "sexo",
                      "faixa_etaria", "cid10"]

    chaves_existentes_sih = [c for c in chaves_sih_sim if c in df_sih.columns]
    chaves_existentes_sim = [c for c in chaves_sih_sim if c in df_sim.columns]
    chaves_merge = [c for c in chaves_sih_sim
                    if c in chaves_existentes_sih and c in chaves_existentes_sim]

    logger.info(f"Chaves de merge SIH-SIM: {chaves_merge}")

    colunas_sim = chaves_merge + [c for c in ["obitos_sim"] if c in df_sim.columns]
    df_sim_subset = df_sim[[c for c in colunas_sim if c in df_sim.columns]].copy()

    if chaves_merge and "obitos_sim" in df_sim_subset.columns:
        df_sim_agg = df_sim_subset.groupby(chaves_merge, as_index=False)["obitos_sim"].sum()
        df_integrado = df_sih.merge(
            df_sim_agg,
            on=chaves_merge,
            how="left",
        )
        logger.info(f"Merge SIH-SIM: {len(df_integrado)} registros")
    else:
        df_integrado = df_sih.copy()
        logger.warning("Merge SIH-SIM: chaves insuficientes, SIM não integrado")

    chaves_pop = ["ano", "uf", "codigo_municipio"]
    chaves_existentes_pop = [c for c in chaves_pop if c in df_pop.columns]
    chaves_merge_pop = [c for c in chaves_pop
                        if c in df_integrado.columns and c in df_pop.columns]

    logger.info(f"Chaves de merge População: {chaves_merge_pop}")

    colunas_pop = chaves_merge_pop + [c for c in ["populacao"] if c in df_pop.columns]
    df_pop_subset = df_pop[[c for c in colunas_pop if c in df_pop.columns]].copy()

    if chaves_merge_pop and "populacao" in df_pop_subset.columns:
        df_pop_agg = df_pop_subset.groupby(chaves_merge_pop, as_index=False)["populacao"].sum()
        df_integrado = df_integrado.merge(
            df_pop_agg,
            on=chaves_merge_pop,
            how="left",
        )
        logger.info(f"Merge com População: {len(df_integrado)} registros")
    else:
        logger.warning("Merge com População: chaves insuficientes")

    if chaves_merge and "obitos_sim" in df_sim.columns:
        df_sim_full = df_sim.groupby(
            [c for c in chaves_merge if c in df_sim.columns],
            as_index=False,
        )["obitos_sim"].sum()

        colunas_sih_exclusivas = [
            "internacoes", "valor_total", "dias_permanencia",
            "obitos_hospitalares", "valor_medio_internacao",
            "media_permanencia", "taxa_mortalidade_hospitalar",
        ]

        for col in colunas_sih_exclusivas:
            if col not in df_sim_full.columns:
                df_sim_full[col] = 0

        for col in df_integrado.columns:
            if col not in df_sim_full.columns:
                if col in ["descricao_cid10", "tipo_diabetes", "regiao", "municipio"]:
                    pass
                elif col == "fonte_dados":
                    df_sim_full[col] = "SIM"
                elif col in ["data_extracao", "data_processamento"]:
                    df_sim_full[col] = DATA_EXTRACAO
                else:
                    df_sim_full[col] = np.nan

        chaves_integrado = df_integrado[chaves_merge].drop_duplicates()

        df_sim_only = df_sim_full.merge(
            chaves_integrado,
            on=chaves_merge,
            how="left",
            indicator=True,
        )
        df_sim_only = df_sim_only[df_sim_only["_merge"] == "left_only"]
        df_sim_only = df_sim_only.drop(columns=["_merge"])

        if len(df_sim_only) > 0:
            for col in ["descricao_cid10"]:
                if col not in df_sim_only.columns and "cid10" in df_sim_only.columns:
                    df_sim_only[col] = df_sim_only["cid10"].apply(
                        lambda c: CID10_DIABETES.get(str(c).upper()[:3], "Diabetes Mellitus")
                    )

            if "tipo_diabetes" not in df_sim_only.columns and "cid10" in df_sim_only.columns:
                df_sim_only["tipo_diabetes"] = df_sim_only["cid10"].apply(_classificar_diabetes)

            for col in df_integrado.columns:
                if col not in df_sim_only.columns:
                    df_sim_only[col] = np.nan

            colunas_finais = [c for c in df_integrado.columns if c in df_sim_only.columns]
            df_sim_only = df_sim_only[colunas_finais]

            df_integrado = pd.concat([df_integrado, df_sim_only], ignore_index=True)
            logger.info(f"Registros exclusivos do SIM adicionados: {len(df_sim_only)}")

    df_integrado["obitos_sim"] = df_integrado.get("obitos_sim", 0).fillna(0).astype(int)
    df_integrado["populacao"] = df_integrado.get("populacao", 0).fillna(0)
    df_integrado["internacoes"] = df_integrado.get("internacoes", 0).fillna(0)

    colunas_zero = [
        "valor_total", "dias_permanencia", "obitos_hospitalares",
        "valor_medio_internacao", "media_permanencia",
        "taxa_mortalidade_hospitalar",
    ]
    for col in colunas_zero:
        if col in df_integrado.columns:
            df_integrado[col] = df_integrado[col].fillna(0)

    df_integrado = _calcular_indicadores(df_integrado)

    df_integrado["fonte_dados"] = df_integrado.get("fonte_dados", pd.Series(dtype=str)).fillna("SIH/SUS + SIM + IBGE")
    if "fonte_dados" not in df_integrado.columns:
        df_integrado["fonte_dados"] = "SIH/SUS + SIM + IBGE"
    df_integrado["data_extracao"] = DATA_EXTRACAO
    df_integrado["data_processamento"] = DATA_PROCESSAMENTO

    for col in ["regiao", "municipio"]:
        if col not in df_integrado.columns:
            df_integrado[col] = "Não informado"

    if "descricao_cid10" not in df_integrado.columns:
        df_integrado["descricao_cid10"] = df_integrado["cid10"].apply(
            lambda c: CID10_DIABETES.get(str(c).upper()[:3], "Diabetes Mellitus")
        )

    if "tipo_diabetes" not in df_integrado.columns:
        df_integrado["tipo_diabetes"] = df_integrado["cid10"].apply(_classificar_diabetes)

    logger.info(f"Base integrada final: {len(df_integrado)} registros, {len(df_integrado.columns)} colunas")

    return df_integrado


def _classificar_diabetes(cid: str) -> str:
    cid = str(cid).upper().strip()
    if cid.startswith("E10"):
        return "Insulinodependente (Tipo 1)"
    elif cid.startswith("E11"):
        return "Não insulinodependente (Tipo 2)"
    elif cid.startswith("E12"):
        return "Relacionado com desnutrição"
    elif cid.startswith("E13"):
        return "Outros tipos especificados"
    elif cid.startswith("E14"):
        return "Não especificado"
    return "Não classificado"


def _calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    if "internacoes" in df.columns and "populacao" in df.columns:
        df["taxa_internacao_100k"] = np.where(
            df["populacao"] > 0,
            (df["internacoes"] / df["populacao"] * 100000).round(2),
            0.0,
        )
    else:
        df["taxa_internacao_100k"] = 0.0

    if "obitos_sim" in df.columns and "populacao" in df.columns:
        df["taxa_mortalidade_100k"] = np.where(
            df["populacao"] > 0,
            (df["obitos_sim"] / df["populacao"] * 100000).round(2),
            0.0,
        )
    else:
        df["taxa_mortalidade_100k"] = 0.0

    if "obitos_hospitalares" in df.columns and "internacoes" in df.columns:
        df["taxa_mortalidade_hospitalar"] = np.where(
            df["internacoes"] > 0,
            (df["obitos_hospitalares"] / df["internacoes"] * 100).round(2),
            0.0,
        )
    else:
        df["taxa_mortalidade_hospitalar"] = 0.0

    if "valor_medio_internacao" not in df.columns:
        if "valor_total" in df.columns and "internacoes" in df.columns:
            df["valor_medio_internacao"] = np.where(
                df["internacoes"] > 0,
                (df["valor_total"] / df["internacoes"]).round(2),
                0.0,
            )
        else:
            df["valor_medio_internacao"] = 0.0

    if "media_permanencia" not in df.columns:
        if "dias_permanencia" in df.columns and "internacoes" in df.columns:
            df["media_permanencia"] = np.where(
                df["internacoes"] > 0,
                (df["dias_permanencia"] / df["internacoes"]).round(2),
                0.0,
            )
        else:
            df["media_permanencia"] = 0.0

    logger.info("Indicadores epidemiológicos calculados")

    return df
