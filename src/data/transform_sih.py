"""Transformação dos dados do SIH/SUS para Diabetes Mellitus. Autora: Nathalia Adriele"""

import pandas as pd
import numpy as np
from loguru import logger

from src.config.settings import (
    CID10_DIABETES,
    CID10_PREFIXES,
    UF_REGIAO,
    UF_NOME,
    SEXO_MAP,
    MUNICIPIOS_AMOSTRA,
    START_YEAR,
    END_YEAR,
    INTERIM_DIR,
    SIH_INTERIM_FILE,
)
from src.utils.text_normalization import normalize_column_name
from src.config.settings import classificar_faixa_etaria


COD_MUN_NOME = {}
for uf, municipios in MUNICIPIOS_AMOSTRA.items():
    for nome, cod in municipios:
        COD_MUN_NOME[cod] = nome


def transform_sih(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma dados brutos do SIH em formato analítico padronizado."""
    logger.info(f"Transformando dados SIH: {len(df)} registros de entrada")

    df = _padronizar_colunas(df)
    df = _mapear_colunas_sih(df)
    df = _converter_tipos(df)
    df = _filtrar_cid_diabetes(df)
    df = _padronizar_uf_regiao(df)
    df = _padronizar_municipio(df)
    df = _padronizar_sexo(df)
    df = _criar_faixa_etaria(df)
    df = _criar_tipo_diabetes(df)
    df = _remover_duplicidades(df)
    df = _tratar_ausentes(df)
    df = _agrupar_sih(df)

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SIH_INTERIM_FILE, index=False, encoding="utf-8")
    logger.info(f"Dados SIH transformados salvos: {SIH_INTERIM_FILE} ({len(df)} registros)")

    return df


def _padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [normalize_column_name(c) for c in df.columns]
    logger.debug(f"Colunas padronizadas: {list(df.columns)}")
    return df


def _mapear_colunas_sih(df: pd.DataFrame) -> pd.DataFrame:
    mapeamento = {
        "ano_cmpt": "ano",
        "mes_cmpt": "mes",
        "uf_zi": "uf",
        "munic_res": "codigo_municipio",
        "munic_mov": "codigo_municipio_mov",
        "sexo": "sexo",
        "idade": "idade",
        "diag_princ": "cid10",
        "diag_secun": "cid10_secundario",
        "n_aih": "id_aih",
        "val_total": "valor_total",
        "val_serv_hosp": "valor_servicos_hospitalares",
        "val_serv_prof": "valor_servicos_profissionais",
        "dias_perm": "dias_permanencia",
        "morte": "obito_hospitalar",
        "dt_inter": "data_internacao",
        "dt_saida": "data_saida",
    }

    cols_to_rename = {}
    for col in df.columns:
        if col in mapeamento:
            cols_to_rename[col] = mapeamento[col]

    df = df.rename(columns=cols_to_rename)
    logger.debug(f"Colunas mapeadas: {list(df.columns)}")
    return df


def _converter_tipos(df: pd.DataFrame) -> pd.DataFrame:
    colunas_numericas = [
        "ano", "mes", "idade", "valor_total",
        "valor_servicos_hospitalares", "valor_servicos_profissionais",
        "dias_permanencia", "obito_hospitalar",
    ]
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
        logger.warning("Coluna 'cid10' não encontrada para filtro.")
        return df

    antes = len(df)
    df = df[df["cid10"].str.upper().str.startswith(CID10_PREFIXES)]
    depois = len(df)
    logger.info(f"Filtro CID-10 Diabetes: {antes} -> {depois} registros (removidos: {antes - depois})")

    return df


def _padronizar_uf_regiao(df: pd.DataFrame) -> pd.DataFrame:
    if "uf" in df.columns:
        df["uf"] = df["uf"].str.strip().str.upper()
        df["regiao"] = df["uf"].map(UF_REGIAO).fillna("Ignorado")
        logger.debug("UF e região padronizados")

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
        logger.debug("Sexo padronizado")

    return df


def _criar_faixa_etaria(df: pd.DataFrame) -> pd.DataFrame:
    if "idade" in df.columns:
        df["faixa_etaria"] = df["idade"].apply(classificar_faixa_etaria)
        logger.debug("Faixa etária criada")

    return df


def _criar_tipo_diabetes(df: pd.DataFrame) -> pd.DataFrame:
    if "cid10" in df.columns:
        cid_upper = df["cid10"].str.upper()

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

        df["tipo_diabetes"] = cid_upper.apply(_classificar)
        logger.debug("Tipo de diabetes classificado")

    return df


def _remover_duplicidades(df: pd.DataFrame) -> pd.DataFrame:
    antes = len(df)

    subset = ["ano", "mes", "uf", "codigo_municipio", "sexo", "faixa_etaria", "cid10"]
    subset_existente = [c for c in subset if c in df.columns]

    if subset_existente:
        df = df.drop_duplicates(subset=subset_existente, keep="first")

    depois = len(df)
    logger.info(f"Duplicidades removidas: {antes} -> {depois} (removidos: {antes - depois})")

    return df


def _tratar_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    colunas_preencher = {
        "valor_total": 0.0,
        "dias_permanencia": 0,
        "obito_hospitalar": 0,
    }

    for col, valor in colunas_preencher.items():
        if col in df.columns:
            df[col] = df[col].fillna(valor)

    return df


def _agrupar_sih(df: pd.DataFrame) -> pd.DataFrame:
    dimensoes = [
        "ano", "mes", "regiao", "uf", "municipio",
        "codigo_municipio", "sexo", "faixa_etaria",
        "cid10", "tipo_diabetes",
    ]

    dimensoes_existentes = [c for c in dimensoes if c in df.columns]

    agg_dict = {}

    if "id_aih" in df.columns:
        agg_dict["internacoes"] = ("id_aih", "count")
    elif len(df.columns) > 0:
        agg_dict["internacoes"] = (dimensoes_existentes[0], "size") if dimensoes_existentes else None

    if "valor_total" in df.columns:
        agg_dict["valor_total"] = ("valor_total", "sum")
        agg_dict["valor_medio_internacao"] = ("valor_total", "mean")

    if "dias_permanencia" in df.columns:
        agg_dict["dias_permanencia"] = ("dias_permanencia", "sum")
        agg_dict["media_permanencia"] = ("dias_permanencia", "mean")

    if "obito_hospitalar" in df.columns:
        agg_dict["obitos_hospitalares"] = ("obito_hospitalar", "sum")

    agg_dict = {k: v for k, v in agg_dict.items() if v is not None}

    if not agg_dict:
        logger.warning("Nenhuma métrica para agregar no SIH")
        return df

    df_agg = df.groupby(dimensoes_existentes, as_index=False).agg(**agg_dict)

    df_agg["descricao_cid10"] = df_agg["cid10"].apply(
        lambda c: CID10_DIABETES.get(
            str(c).upper()[:3], "Diabetes Mellitus"
        )
    )

    if "obitos_hospitalares" in df_agg.columns and "internacoes" in df_agg.columns:
        df_agg["taxa_mortalidade_hospitalar"] = np.where(
            df_agg["internacoes"] > 0,
            (df_agg["obitos_hospitalares"] / df_agg["internacoes"] * 100).round(2),
            0.0,
        )

    colunas_arredondar = [
        "valor_total", "valor_medio_internacao",
        "media_permanencia", "taxa_mortalidade_hospitalar",
    ]
    for col in colunas_arredondar:
        if col in df_agg.columns:
            df_agg[col] = df_agg[col].round(2)

    colunas_int = ["internacoes", "dias_permanencia", "obitos_hospitalares"]
    for col in colunas_int:
        if col in df_agg.columns:
            df_agg[col] = df_agg[col].astype(int)

    logger.info(f"SIH agregado: {len(df_agg)} registros analíticos")

    return df_agg
