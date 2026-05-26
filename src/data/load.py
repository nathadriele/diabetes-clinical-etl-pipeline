"""Exportação da base analítica final em CSV, Parquet e Excel. Autora: Nathalia Adriele"""

import pandas as pd
from loguru import logger

from src.config.settings import (
    PROCESSED_DIR,
    PROCESSED_CSV,
    PROCESSED_PARQUET,
    PROCESSED_XLSX,
    COLUNAS_BASE_FINAL,
)


def load_data(df: pd.DataFrame) -> dict:
    """Exporta a base processada em CSV, Parquet e Excel."""
    logger.info(f"Iniciando exportação dos dados processados ({len(df)} registros)...")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    resultados = {}

    colunas_ordenadas = [c for c in COLUNAS_BASE_FINAL if c in df.columns]
    colunas_extras = [c for c in df.columns if c not in COLUNAS_BASE_FINAL]
    df_export = df[colunas_ordenadas + colunas_extras].copy()

    for col in ["ano", "mes"]:
        if col in df_export.columns:
            df_export[col] = pd.to_numeric(df_export[col], errors="coerce").astype("Int64")
            df_export[col] = df_export[col].astype(int)

    try:
        df_export.to_csv(PROCESSED_CSV, index=False, encoding="utf-8")
        tamanho_mb = PROCESSED_CSV.stat().st_size / (1024 * 1024)
        resultados["csv"] = {
            "status": "SUCESSO",
            "arquivo": str(PROCESSED_CSV),
            "tamanho_mb": round(tamanho_mb, 2),
        }
        logger.info(f"CSV exportado: {PROCESSED_CSV} ({tamanho_mb:.2f} MB)")
    except Exception as e:
        resultados["csv"] = {"status": "FALHA", "erro": str(e)}
        logger.error(f"Erro ao exportar CSV: {e}")

    try:
        df_parquet = df_export.copy()
        for col in df_parquet.columns:
            if df_parquet[col].dtype.name == "Int64":
                df_parquet[col] = df_parquet[col].astype("float64")

        df_parquet.to_parquet(PROCESSED_PARQUET, index=False, engine="pyarrow")
        tamanho_mb = PROCESSED_PARQUET.stat().st_size / (1024 * 1024)
        resultados["parquet"] = {
            "status": "SUCESSO",
            "arquivo": str(PROCESSED_PARQUET),
            "tamanho_mb": round(tamanho_mb, 2),
        }
        logger.info(f"Parquet exportado: {PROCESSED_PARQUET} ({tamanho_mb:.2f} MB)")
    except Exception as e:
        resultados["parquet"] = {"status": "FALHA", "erro": str(e)}
        logger.error(f"Erro ao exportar Parquet: {e}")

    try:
        df_excel = df_export.copy()
        for col in df_excel.columns:
            if df_excel[col].dtype.name == "Int64":
                df_excel[col] = df_excel[col].astype("float64")

        df_excel.to_excel(
            PROCESSED_XLSX,
            index=False,
            engine="openpyxl",
            sheet_name="Diabetes_SUS",
        )
        tamanho_mb = PROCESSED_XLSX.stat().st_size / (1024 * 1024)
        resultados["xlsx"] = {
            "status": "SUCESSO",
            "arquivo": str(PROCESSED_XLSX),
            "tamanho_mb": round(tamanho_mb, 2),
        }
        logger.info(f"Excel exportado: {PROCESSED_XLSX} ({tamanho_mb:.2f} MB)")
    except Exception as e:
        resultados["xlsx"] = {"status": "FALHA", "erro": str(e)}
        logger.error(f"Erro ao exportar Excel: {e}")

    sucessos = sum(1 for r in resultados.values() if r["status"] == "SUCESSO")
    logger.info(f"Exportação concluída: {sucessos}/{len(resultados)} formatos exportados")

    return resultados
