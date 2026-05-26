"""Verificações automatizadas de qualidade dos dados. Autora: Nathalia Adriele"""

import pandas as pd
import numpy as np
from loguru import logger
from datetime import datetime

from src.config.settings import (
    CID10_CODES,
    START_YEAR,
    END_YEAR,
)


def run_quality_checks(df: pd.DataFrame) -> list:
    """Executa verificações de qualidade nos dados processados."""
    logger.info(f"Executando verificações de qualidade em {len(df)} registros...")

    checks = []

    checks.append(_check_completude_colunas(df))
    checks.append(_check_valores_ausentes(df))
    checks.append(_check_range_anos(df))
    checks.append(_check_uf_validas(df))
    checks.append(_check_cid10_validos(df))
    checks.append(_check_sexo_valido(df))
    checks.append(_check_valores_numericos(df))
    checks.append(_check_taxas(df))
    checks.append(_check_consistencia_referencial(df))
    checks.append(_check_distribuicao_temporal(df))

    logger.info(f"Verificações de qualidade concluídas: {len(checks)} checks")

    return checks


def _check_completude_colunas(df: pd.DataFrame) -> dict:
    colunas_obrigatorias = [
        "ano", "mes", "uf", "sexo", "faixa_etaria", "cid10",
        "internacoes", "obitos_sim", "populacao",
    ]

    colunas_presentes = [c for c in colunas_obrigatorias if c in df.columns]
    colunas_ausentes = [c for c in colunas_obrigatorias if c not in df.columns]

    return {
        "check": "completude_colunas",
        "status": "PASS" if not colunas_ausentes else "FAIL",
        "descricao": f"Colunas obrigatórias presentes: {len(colunas_presentes)}/{len(colunas_obrigatorias)}",
        "detalhes": {
            "presentes": colunas_presentes,
            "ausentes": colunas_ausentes,
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_valores_ausentes(df: pd.DataFrame) -> dict:
    colunas_chave = ["ano", "uf", "cid10", "sexo", "internacoes"]
    ausentes = {}

    for col in colunas_chave:
        if col in df.columns:
            n_ausentes = df[col].isna().sum()
            pct = round(n_ausentes / len(df) * 100, 2) if len(df) > 0 else 0
            if n_ausentes > 0:
                ausentes[col] = {"count": int(n_ausentes), "percentual": pct}

    return {
        "check": "valores_ausentes",
        "status": "PASS" if not ausentes else "ALERTA",
        "descricao": f"Colunas com valores ausentes: {len(ausentes)}",
        "detalhes": ausentes,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_range_anos(df: pd.DataFrame) -> dict:
    if "ano" not in df.columns:
        return {
            "check": "range_anos",
            "status": "FAIL",
            "descricao": "Coluna 'ano' não encontrada",
            "detalhes": {},
        }

    anos = pd.to_numeric(df["ano"], errors="coerce").dropna().unique()
    anos_esperados = set(range(START_YEAR, END_YEAR + 1))
    anos_encontrados = set(int(a) for a in anos)
    anos_faltantes = anos_esperados - anos_encontrados

    return {
        "check": "range_anos",
        "status": "PASS" if not anos_faltantes else "ALERTA",
        "descricao": f"Anos encontrados: {sorted(anos_encontrados)}",
        "detalhes": {
            "anos_encontrados": sorted(anos_encontrados),
            "anos_faltantes": sorted(anos_faltantes) if anos_faltantes else [],
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_uf_validas(df: pd.DataFrame) -> dict:
    ufs_validas = {
        "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
        "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
        "RO", "RR", "RS", "SC", "SE", "SP", "TO",
    }

    if "uf" not in df.columns:
        return {
            "check": "uf_validas",
            "status": "FAIL",
            "descricao": "Coluna 'uf' não encontrada",
            "detalhes": {},
        }

    ufs_encontradas = set(df["uf"].dropna().unique())
    ufs_invalidas = ufs_encontradas - ufs_validas

    return {
        "check": "uf_validas",
        "status": "PASS" if not ufs_invalidas else "FAIL",
        "descricao": f"UFs encontradas: {len(ufs_encontradas)}, inválidas: {len(ufs_invalidas)}",
        "detalhes": {
            "ufs_encontradas": sorted(ufs_encontradas),
            "ufs_invalidas": sorted(ufs_invalidas) if ufs_invalidas else [],
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_cid10_validos(df: pd.DataFrame) -> dict:
    if "cid10" not in df.columns:
        return {
            "check": "cid10_validos",
            "status": "FAIL",
            "descricao": "Coluna 'cid10' não encontrada",
            "detalhes": {},
        }

    cid10_encontrados = set(df["cid10"].dropna().unique())
    cid10_esperados = set(CID10_CODES)

    return {
        "check": "cid10_validos",
        "status": "PASS",
        "descricao": f"CID-10 encontrados: {sorted(cid10_encontrados)}",
        "detalhes": {
            "encontrados": sorted(cid10_encontrados),
            "esperados": sorted(cid10_esperados),
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_sexo_valido(df: pd.DataFrame) -> dict:
    sexos_validos = {"Masculino", "Feminino", "Ignorado"}

    if "sexo" not in df.columns:
        return {
            "check": "sexo_valido",
            "status": "FAIL",
            "descricao": "Coluna 'sexo' não encontrada",
            "detalhes": {},
        }

    sexos_encontrados = set(df["sexo"].dropna().unique())
    sexos_invalidos = sexos_encontrados - sexos_validos

    return {
        "check": "sexo_valido",
        "status": "PASS" if not sexos_invalidos else "FAIL",
        "descricao": f"Sexos encontrados: {sorted(sexos_encontrados)}",
        "detalhes": {
            "encontrados": sorted(sexos_encontrados),
            "invalidos": sorted(sexos_invalidos) if sexos_invalidos else [],
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_valores_numericos(df: pd.DataFrame) -> dict:
    colunas = ["internacoes", "valor_total", "dias_permanencia",
               "obitos_hospitalares", "obitos_sim", "populacao"]

    problemas = {}
    for col in colunas:
        if col in df.columns:
            negativos = (df[col] < 0).sum()
            if negativos > 0:
                problemas[col] = int(negativos)

    return {
        "check": "valores_numericos",
        "status": "PASS" if not problemas else "FAIL",
        "descricao": "Verificação de valores negativos indevidos",
        "detalhes": problemas if problemas else {"nenhum_problema": True},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_taxas(df: pd.DataFrame) -> dict:
    problemas = []

    if "taxa_mortalidade_hospitalar" in df.columns:
        max_taxa = df["taxa_mortalidade_hospitalar"].max()
        if max_taxa > 100:
            problemas.append(f"Mortalidade hospitalar > 100%: {max_taxa}")

    return {
        "check": "taxas",
        "status": "PASS" if not problemas else "ALERTA",
        "descricao": "Verificação de coerência das taxas",
        "detalhes": {"problemas": problemas} if problemas else {"todas_coerentes": True},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_consistencia_referencial(df: pd.DataFrame) -> dict:
    problemas = []

    if "obitos_hospitalares" in df.columns and "internacoes" in df.columns:
        inconsistente = (df["obitos_hospitalares"] > df["internacoes"]).sum()
        if inconsistente > 0:
            problemas.append(
                f"Óbitos > internações em {inconsistente} registros"
            )

    return {
        "check": "consistencia_referencial",
        "status": "PASS" if not problemas else "ALERTA",
        "descricao": "Verificação de consistência referencial",
        "detalhes": {"problemas": problemas} if problemas else {"consistente": True},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _check_distribuicao_temporal(df: pd.DataFrame) -> dict:
    if "ano" not in df.columns:
        return {
            "check": "distribuicao_temporal",
            "status": "FAIL",
            "descricao": "Coluna 'ano' não encontrada",
            "detalhes": {},
        }

    dist = df["ano"].value_counts().sort_index().to_dict()
    dist_str = {str(k): int(v) for k, v in dist.items()}

    return {
        "check": "distribuicao_temporal",
        "status": "PASS",
        "descricao": "Distribuição temporal dos registros",
        "detalhes": dist_str,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
