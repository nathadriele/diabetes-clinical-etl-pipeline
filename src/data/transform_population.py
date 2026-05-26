"""Transformação dos dados de população residente (IBGE/DATASUS). Autora: Nathalia Adriele"""

import pandas as pd
import numpy as np
from loguru import logger

from src.config.settings import (
    UF_REGIAO,
    UF_NOME,
    INTERIM_DIR,
    POPULATION_INTERIM_FILE,
    MUNICIPIOS_AMOSTRA,
)
from src.utils.text_normalization import normalize_column_name


def transform_population(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma dados brutos de população em formato padronizado."""
    logger.info(f"Transformando dados de população: {len(df)} registros")

    df = _padronizar_colunas(df)
    df = _mapear_colunas_pop(df)
    df = _converter_tipos(df)
    df = _padronizar_uf_regiao(df)
    df = _padronizar_municipio(df)
    df = _tratar_ausentes(df)
    df = _validar_populacao(df)

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(POPULATION_INTERIM_FILE, index=False, encoding="utf-8")
    logger.info(f"Dados de população transformados: {POPULATION_INTERIM_FILE} ({len(df)} registros)")

    return df


def _padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [normalize_column_name(c) for c in df.columns]
    return df


def _mapear_colunas_pop(df: pd.DataFrame) -> pd.DataFrame:
    mapeamento = {
        "ano": "ano",
        "uf": "uf",
        "municipio": "municipio",
        "cod_municipio": "codigo_municipio",
        "codigo_municipio": "codigo_municipio",
        "populacao": "populacao",
        "pop": "populacao",
    }

    cols_to_rename = {}
    for col in df.columns:
        if col in mapeamento:
            cols_to_rename[col] = mapeamento[col]

    df = df.rename(columns=cols_to_rename)
    return df


def _converter_tipos(df: pd.DataFrame) -> pd.DataFrame:
    if "ano" in df.columns:
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")

    if "populacao" in df.columns:
        df["populacao"] = pd.to_numeric(df["populacao"], errors="coerce")

    colunas_str = ["uf", "municipio", "codigo_municipio"]
    for col in colunas_str:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def _padronizar_uf_regiao(df: pd.DataFrame) -> pd.DataFrame:
    if "uf" in df.columns:
        df["uf"] = df["uf"].str.strip().str.upper()
        df["regiao"] = df["uf"].map(UF_REGIAO).fillna("Ignorado")
    return df


def _padronizar_municipio(df: pd.DataFrame) -> pd.DataFrame:
    if "municipio" not in df.columns and "codigo_municipio" in df.columns:
        COD_MUN_NOME = {}
        for uf, municipios in MUNICIPIOS_AMOSTRA.items():
            for nome, cod in municipios:
                COD_MUN_NOME[cod] = nome

        df["municipio"] = df["codigo_municipio"].map(COD_MUN_NOME).fillna("Não informado")

    return df


def _tratar_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    if "populacao" in df.columns:
        df["populacao"] = df["populacao"].fillna(0)
    return df


def _validar_populacao(df: pd.DataFrame) -> pd.DataFrame:
    if "populacao" in df.columns:
        invalidos = (df["populacao"] <= 0).sum()
        if invalidos > 0:
            logger.warning(f"Registros com população <= 0: {invalidos}")
            df = df[df["populacao"] > 0]
    return df
