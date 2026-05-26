"""Transformação dos dados do SIM (mortalidade) para Diabetes Mellitus. Autora: Nathalia Adriele"""

import pandas as pd
import numpy as np
from loguru import logger

from src.config.settings import (
    CID10_DIABETES,
    CID10_PREFIXES,
    UF_REGIAO,
    SEXO_MAP,
    MUNICIPIOS_AMOSTRA,
    START_YEAR,
    END_YEAR,
    INTERIM_DIR,
    SIM_INTERIM_FILE,
)
from src.utils.text_normalization import normalize_column_name
from src.config.settings import classificar_faixa_etaria


COD_MUN_NOME = {}
for uf, municipios in MUNICIPIOS_AMOSTRA.items():
    for nome, cod in municipios:
        COD_MUN_NOME[cod] = nome


def transform_sim(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma dados brutos do SIM em formato analítico padronizado."""
    logger.info(f"Transformando dados SIM: {len(df)} registros de entrada")

    df = _padronizar_colunas(df)
    df = _mapear_colunas_sim(df)
    df = _converter_tipos(df)
    df = _filtrar_cid_diabetes(df)
    df = _padronizar_uf_regiao(df)
    df = _padronizar_municipio(df)
    df = _padronizar_sexo(df)
    df = _criar_faixa_etaria(df)
    df = _criar_tipo_diabetes(df)
    df = _remover_duplicidades(df)
    df = _tratar_ausentes(df)
    df = _agrupar_sim(df)

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SIM_INTERIM_FILE, index=False, encoding="utf-8")
    logger.info(f"Dados SIM transformados salvos: {SIM_INTERIM_FILE} ({len(df)} registros)")

    return df


def _padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [normalize_column_name(c) for c in df.columns]
    return df


def _mapear_colunas_sim(df: pd.DataFrame) -> pd.DataFrame:
    mapeamento = {
        "ano_obito": "ano",
        "ano": "ano",
        "mes_obito": "mes",
        "uf_resid": "uf",
        "munic_res": "codigo_municipio",
        "sexo": "sexo",
        "idade": "idade",
        "causa_basica": "cid10",
        "linhaa": "cid10_linha_a",
        "dt_obito": "data_obito",
        "numerodo": "id_obito",
    }

    cols_to_rename = {}
    for col in df.columns:
        if col in mapeamento:
            cols_to_rename[col] = mapeamento[col]

    # ano_obito e ano mapeiam para 'ano' - preferir ano_obito
    if "ano_obito" in cols_to_rename and "ano" in df.columns:
        df = df.rename(columns={"ano_obito": "ano_obito_temp"})
        df = df.drop(columns=["ano"], errors="ignore")
        df = df.rename(columns={"ano_obito_temp": "ano"})
    else:
        df = df.rename(columns=cols_to_rename)

    return df


def _converter_tipos(df: pd.DataFrame) -> pd.DataFrame:
    colunas_numericas = ["ano", "mes", "idade"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    colunas_str = ["uf", "cid10", "sexo", "codigo_municipio"]
    for col in colunas_str:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def _filtrar_cid_diabetes(df: pd.DataFrame) -> pd.DataFrame:
    if "cid10" not in df.columns:
        logger.warning("Coluna 'cid10' não encontrada no SIM.")
        return df

    antes = len(df)
    df = df[df["cid10"].str.upper().str.startswith(CID10_PREFIXES)]
    depois = len(df)
    logger.info(f"Filtro CID-10 SIM: {antes} -> {depois} registros")

    return df


def _padronizar_uf_regiao(df: pd.DataFrame) -> pd.DataFrame:
    if "uf" in df.columns:
        df["uf"] = df["uf"].str.strip().str.upper()
        df["regiao"] = df["uf"].map(UF_REGIAO).fillna("Ignorado")
    return df


def _padronizar_municipio(df: pd.DataFrame) -> pd.DataFrame:
    if "codigo_municipio" in df.columns:
        df["codigo_municipio"] = df["codigo_municipio"].astype(str).str.strip()
        df["municipio"] = df["codigo_municipio"].map(COD_MUN_NOME).fillna("Não informado")
    return df


def _padronizar_sexo(df: pd.DataFrame) -> pd.DataFrame:
    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].astype(str).str.strip().str.upper()
        df["sexo"] = df["sexo"].map(SEXO_MAP).fillna("Ignorado")
    return df


def _criar_faixa_etaria(df: pd.DataFrame) -> pd.DataFrame:
    if "idade" in df.columns:
        df["faixa_etaria"] = df["idade"].apply(classificar_faixa_etaria)
    return df


def _criar_tipo_diabetes(df: pd.DataFrame) -> pd.DataFrame:
    if "cid10" in df.columns:
        def _classificar(cid: str) -> str:
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

        df["tipo_diabetes"] = df["cid10"].str.upper().apply(_classificar)
    return df


def _remover_duplicidades(df: pd.DataFrame) -> pd.DataFrame:
    antes = len(df)

    subset = ["ano", "mes", "uf", "codigo_municipio", "sexo", "faixa_etaria", "cid10"]
    subset_existente = [c for c in subset if c in df.columns]

    if subset_existente:
        df = df.drop_duplicates(subset=subset_existente, keep="first")

    logger.info(f"Duplicidades SIM removidas: {antes} -> {len(df)}")
    return df


def _tratar_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    return df


def _agrupar_sim(df: pd.DataFrame) -> pd.DataFrame:
    dimensoes = [
        "ano", "mes", "regiao", "uf", "municipio",
        "codigo_municipio", "sexo", "faixa_etaria",
        "cid10", "tipo_diabetes",
    ]

    dimensoes_existentes = [c for c in dimensoes if c in df.columns]

    agg_dict = {}

    if "id_obito" in df.columns:
        agg_dict["obitos_sim"] = ("id_obito", "count")
    else:
        if dimensoes_existentes:
            agg_dict["obitos_sim"] = (dimensoes_existentes[0], "size")

    if not agg_dict:
        logger.warning("Nenhuma métrica para agregar no SIM")
        return df

    df_agg = df.groupby(dimensoes_existentes, as_index=False).agg(**agg_dict)

    df_agg["descricao_cid10"] = df_agg["cid10"].apply(
        lambda c: CID10_DIABETES.get(
            str(c).upper()[:3], "Diabetes Mellitus"
        )
    )

    if "obitos_sim" in df_agg.columns:
        df_agg["obitos_sim"] = df_agg["obitos_sim"].astype(int)

    logger.info(f"SIM agregado: {len(df_agg)} registros analíticos")

    return df_agg
