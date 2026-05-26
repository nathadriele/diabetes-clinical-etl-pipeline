"""Módulo de extração de dados brutos. Autora: Nathalia Adriele"""

import pandas as pd
from loguru import logger

import src.config.settings as _settings


def extract_sih() -> pd.DataFrame:
    logger.info(f"Extraindo dados SIH de: {_settings.SIH_RAW_FILE}")

    if not _settings.SIH_RAW_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo SIH não encontrado: {_settings.SIH_RAW_FILE}. "
            "Execute o download dos dados primeiro."
        )

    df = pd.read_csv(_settings.SIH_RAW_FILE, dtype=str, low_memory=False)
    logger.info(f"SIH: {len(df)} registros extraídos, {len(df.columns)} colunas")
    logger.debug(f"Colunas SIH: {list(df.columns)}")

    return df


def extract_sim() -> pd.DataFrame:
    logger.info(f"Extraindo dados SIM de: {_settings.SIM_RAW_FILE}")

    if not _settings.SIM_RAW_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo SIM não encontrado: {_settings.SIM_RAW_FILE}. "
            "Execute o download dos dados primeiro."
        )

    df = pd.read_csv(_settings.SIM_RAW_FILE, dtype=str, low_memory=False)
    logger.info(f"SIM: {len(df)} registros extraídos, {len(df.columns)} colunas")
    logger.debug(f"Colunas SIM: {list(df.columns)}")

    return df


def extract_population() -> pd.DataFrame:
    logger.info(f"Extraindo dados de população de: {_settings.POPULATION_RAW_FILE}")

    if not _settings.POPULATION_RAW_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo de população não encontrado: {_settings.POPULATION_RAW_FILE}. "
            "Execute o download dos dados primeiro."
        )

    df = pd.read_csv(_settings.POPULATION_RAW_FILE, dtype=str, low_memory=False)
    logger.info(f"População: {len(df)} registros extraídos, {len(df.columns)} colunas")
    logger.debug(f"Colunas População: {list(df.columns)}")

    return df


def extract_all() -> dict:
    logger.info("Iniciando extração de todas as fontes de dados...")

    data = {
        "sih": extract_sih(),
        "sim": extract_sim(),
        "population": extract_population(),
    }

    logger.info("Extração de todas as fontes concluída.")
    return data
