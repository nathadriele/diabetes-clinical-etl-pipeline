"""Cálculo de indicadores epidemiológicos agregados. Autora: Nathalia Adriele"""

import pandas as pd
import numpy as np
from loguru import logger

from src.config.settings import (
    REGIOES_UF,
    FAIXAS_ETARIAS,
)


def calculate_indicators(df: pd.DataFrame) -> dict:
    """Calcula todos os indicadores epidemiológicos."""
    logger.info("Calculando indicadores epidemiológicos...")

    indicators = {}

    indicators["nacionais"] = _calcular_indicadores_nacionais(df)
    indicators["por_ano"] = _calcular_por_ano(df)
    indicators["por_uf"] = _calcular_por_uf(df)
    indicators["por_regiao"] = _calcular_por_regiao(df)
    indicators["por_sexo"] = _calcular_por_sexo(df)
    indicators["por_faixa_etaria"] = _calcular_por_faixa_etaria(df)
    indicators["por_cid10"] = _calcular_por_cid10(df)
    indicators["por_tipo_diabetes"] = _calcular_por_tipo_diabetes(df)

    logger.info("Indicadores epidemiológicos calculados com sucesso.")

    return indicators


def _calcular_indicadores_nacionais(df: pd.DataFrame) -> pd.DataFrame:
    data = {
        "total_internacoes": int(df["internacoes"].sum()) if "internacoes" in df.columns else 0,
        "total_obitos_hospitalares": int(df["obitos_hospitalares"].sum()) if "obitos_hospitalares" in df.columns else 0,
        "total_obitos_sim": int(df["obitos_sim"].sum()) if "obitos_sim" in df.columns else 0,
    }

    if "valor_total" in df.columns:
        data["valor_total_internacoes"] = round(float(df["valor_total"].sum()), 2)

    if "valor_medio_internacao" in df.columns:
        internacoes_total = data["total_internacoes"]
        valor_total = data.get("valor_total_internacoes", 0)
        data["valor_medio_internacao"] = round(
            valor_total / internacoes_total, 2
        ) if internacoes_total > 0 else 0.0

    if "media_permanencia" in df.columns:
        total_dias = int(df["dias_permanencia"].sum()) if "dias_permanencia" in df.columns else 0
        internacoes_total = data["total_internacoes"]
        data["media_permanencia"] = round(
            total_dias / internacoes_total, 2
        ) if internacoes_total > 0 else 0.0

    if data["total_internacoes"] > 0:
        data["taxa_mortalidade_hospitalar"] = round(
            data["total_obitos_hospitalares"] / data["total_internacoes"] * 100, 2
        )
    else:
        data["taxa_mortalidade_hospitalar"] = 0.0

    if "populacao" in df.columns:
        pop_total = df["populacao"].sum()
        data["taxa_internacao_100k"] = round(
            data["total_internacoes"] / pop_total * 100000, 2
        ) if pop_total > 0 else 0.0
        data["taxa_mortalidade_100k"] = round(
            data["total_obitos_sim"] / pop_total * 100000, 2
        ) if pop_total > 0 else 0.0

    return pd.DataFrame([data])


def _calcular_por_ano(df: pd.DataFrame) -> pd.DataFrame:
    if "ano" not in df.columns:
        return pd.DataFrame()

    colunas_agg = {}
    if "internacoes" in df.columns:
        colunas_agg["internacoes"] = ("internacoes", "sum")
    if "obitos_hospitalares" in df.columns:
        colunas_agg["obitos_hospitalares"] = ("obitos_hospitalares", "sum")
    if "obitos_sim" in df.columns:
        colunas_agg["obitos_sim"] = ("obitos_sim", "sum")
    if "valor_total" in df.columns:
        colunas_agg["valor_total"] = ("valor_total", "sum")
    if "dias_permanencia" in df.columns:
        colunas_agg["dias_permanencia"] = ("dias_permanencia", "sum")
    if "populacao" in df.columns:
        colunas_agg["populacao"] = ("populacao", "sum")

    if not colunas_agg:
        return pd.DataFrame()

    result = df.groupby("ano", as_index=False).agg(**colunas_agg)

    if "internacoes" in result.columns and "valor_total" in result.columns:
        result["valor_medio_internacao"] = np.where(
            result["internacoes"] > 0,
            (result["valor_total"] / result["internacoes"]).round(2),
            0.0,
        )

    if "internacoes" in result.columns and "dias_permanencia" in result.columns:
        result["media_permanencia"] = np.where(
            result["internacoes"] > 0,
            (result["dias_permanencia"] / result["internacoes"]).round(2),
            0.0,
        )

    if "obitos_hospitalares" in result.columns and "internacoes" in result.columns:
        result["taxa_mortalidade_hospitalar"] = np.where(
            result["internacoes"] > 0,
            (result["obitos_hospitalares"] / result["internacoes"] * 100).round(2),
            0.0,
        )

    if "internacoes" in result.columns and "populacao" in result.columns:
        result["taxa_internacao_100k"] = np.where(
            result["populacao"] > 0,
            (result["internacoes"] / result["populacao"] * 100000).round(2),
            0.0,
        )

    if "obitos_sim" in result.columns and "populacao" in result.columns:
        result["taxa_mortalidade_100k"] = np.where(
            result["populacao"] > 0,
            (result["obitos_sim"] / result["populacao"] * 100000).round(2),
            0.0,
        )

    return result


def _calcular_por_uf(df: pd.DataFrame) -> pd.DataFrame:
    if "uf" not in df.columns:
        return pd.DataFrame()

    colunas_agg = {}
    if "internacoes" in df.columns:
        colunas_agg["internacoes"] = ("internacoes", "sum")
    if "obitos_hospitalares" in df.columns:
        colunas_agg["obitos_hospitalares"] = ("obitos_hospitalares", "sum")
    if "obitos_sim" in df.columns:
        colunas_agg["obitos_sim"] = ("obitos_sim", "sum")
    if "valor_total" in df.columns:
        colunas_agg["valor_total"] = ("valor_total", "sum")
    if "populacao" in df.columns:
        colunas_agg["populacao"] = ("populacao", "sum")

    if not colunas_agg:
        return pd.DataFrame()

    result = df.groupby("uf", as_index=False).agg(**colunas_agg)

    if "internacoes" in result.columns and "populacao" in result.columns:
        result["taxa_internacao_100k"] = np.where(
            result["populacao"] > 0,
            (result["internacoes"] / result["populacao"] * 100000).round(2),
            0.0,
        )

    if "obitos_sim" in result.columns and "populacao" in result.columns:
        result["taxa_mortalidade_100k"] = np.where(
            result["populacao"] > 0,
            (result["obitos_sim"] / result["populacao"] * 100000).round(2),
            0.0,
        )

    return result


def _calcular_por_regiao(df: pd.DataFrame) -> pd.DataFrame:
    if "regiao" not in df.columns:
        return pd.DataFrame()

    colunas_agg = {}
    if "internacoes" in df.columns:
        colunas_agg["internacoes"] = ("internacoes", "sum")
    if "obitos_hospitalares" in df.columns:
        colunas_agg["obitos_hospitalares"] = ("obitos_hospitalares", "sum")
    if "obitos_sim" in df.columns:
        colunas_agg["obitos_sim"] = ("obitos_sim", "sum")
    if "valor_total" in df.columns:
        colunas_agg["valor_total"] = ("valor_total", "sum")
    if "populacao" in df.columns:
        colunas_agg["populacao"] = ("populacao", "sum")

    if not colunas_agg:
        return pd.DataFrame()

    result = df.groupby("regiao", as_index=False).agg(**colunas_agg)

    if "internacoes" in result.columns and "populacao" in result.columns:
        result["taxa_internacao_100k"] = np.where(
            result["populacao"] > 0,
            (result["internacoes"] / result["populacao"] * 100000).round(2),
            0.0,
        )

    if "obitos_sim" in result.columns and "populacao" in result.columns:
        result["taxa_mortalidade_100k"] = np.where(
            result["populacao"] > 0,
            (result["obitos_sim"] / result["populacao"] * 100000).round(2),
            0.0,
        )

    return result


def _calcular_por_sexo(df: pd.DataFrame) -> pd.DataFrame:
    if "sexo" not in df.columns:
        return pd.DataFrame()

    colunas_agg = {}
    if "internacoes" in df.columns:
        colunas_agg["internacoes"] = ("internacoes", "sum")
    if "obitos_hospitalares" in df.columns:
        colunas_agg["obitos_hospitalares"] = ("obitos_hospitalares", "sum")
    if "obitos_sim" in df.columns:
        colunas_agg["obitos_sim"] = ("obitos_sim", "sum")
    if "valor_total" in df.columns:
        colunas_agg["valor_total"] = ("valor_total", "sum")

    if not colunas_agg:
        return pd.DataFrame()

    return df.groupby("sexo", as_index=False).agg(**colunas_agg)


def _calcular_por_faixa_etaria(df: pd.DataFrame) -> pd.DataFrame:
    if "faixa_etaria" not in df.columns:
        return pd.DataFrame()

    colunas_agg = {}
    if "internacoes" in df.columns:
        colunas_agg["internacoes"] = ("internacoes", "sum")
    if "obitos_hospitalares" in df.columns:
        colunas_agg["obitos_hospitalares"] = ("obitos_hospitalares", "sum")
    if "obitos_sim" in df.columns:
        colunas_agg["obitos_sim"] = ("obitos_sim", "sum")

    if not colunas_agg:
        return pd.DataFrame()

    result = df.groupby("faixa_etaria", as_index=False).agg(**colunas_agg)

    ordem = {fa: i for i, fa in enumerate(FAIXAS_ETARIAS)}
    result["_ordem"] = result["faixa_etaria"].map(ordem).fillna(99)
    result = result.sort_values("_ordem").drop(columns=["_ordem"]).reset_index(drop=True)

    return result


def _calcular_por_cid10(df: pd.DataFrame) -> pd.DataFrame:
    if "cid10" not in df.columns:
        return pd.DataFrame()

    colunas_agg = {}
    if "internacoes" in df.columns:
        colunas_agg["internacoes"] = ("internacoes", "sum")
    if "obitos_hospitalares" in df.columns:
        colunas_agg["obitos_hospitalares"] = ("obitos_hospitalares", "sum")
    if "obitos_sim" in df.columns:
        colunas_agg["obitos_sim"] = ("obitos_sim", "sum")
    if "valor_total" in df.columns:
        colunas_agg["valor_total"] = ("valor_total", "sum")

    if not colunas_agg:
        return pd.DataFrame()

    return df.groupby("cid10", as_index=False).agg(**colunas_agg)


def _calcular_por_tipo_diabetes(df: pd.DataFrame) -> pd.DataFrame:
    if "tipo_diabetes" not in df.columns:
        return pd.DataFrame()

    colunas_agg = {}
    if "internacoes" in df.columns:
        colunas_agg["internacoes"] = ("internacoes", "sum")
    if "obitos_hospitalares" in df.columns:
        colunas_agg["obitos_hospitalares"] = ("obitos_hospitalares", "sum")
    if "obitos_sim" in df.columns:
        colunas_agg["obitos_sim"] = ("obitos_sim", "sum")

    if not colunas_agg:
        return pd.DataFrame()

    return df.groupby("tipo_diabetes", as_index=False).agg(**colunas_agg)
