"""Geração de relatórios de qualidade em CSV. Autora: Nathalia Adriele"""

import pandas as pd
from loguru import logger
from datetime import datetime

from src.config.settings import (
    REPORTS_DIR,
    DATA_QUALITY_REPORT,
    MISSING_VALUES_REPORT,
)


def generate_quality_report(checks: list, df: pd.DataFrame) -> None:
    """Gera relatórios de qualidade em CSV."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    _gerar_relatorio_qualidade_csv(checks)
    _gerar_relatorio_ausentes_csv(df)

    logger.info("Relatórios de qualidade gerados com sucesso.")


def _gerar_relatorio_qualidade_csv(checks: list) -> None:
    linhas = []

    for check in checks:
        linhas.append({
            "check": check.get("check", ""),
            "status": check.get("status", ""),
            "descricao": check.get("descricao", ""),
            "data_verificacao": check.get("timestamp", ""),
        })

    df_relatorio = pd.DataFrame(linhas)
    df_relatorio.to_csv(DATA_QUALITY_REPORT, index=False, encoding="utf-8")
    logger.info(f"Relatório de qualidade salvo: {DATA_QUALITY_REPORT}")


def _gerar_relatorio_ausentes_csv(df: pd.DataFrame) -> None:
    ausentes = df.isnull().sum()
    total = len(df)

    linhas = []
    for coluna in df.columns:
        n_ausente = int(ausentes[coluna])
        pct = round(n_ausente / total * 100, 2) if total > 0 else 0.0
        linhas.append({
            "coluna": coluna,
            "total_registros": total,
            "valores_ausentes": n_ausente,
            "percentual_ausente": pct,
            "valores_preenchidos": total - n_ausente,
            "percentual_preenchido": round(100 - pct, 2),
        })

    df_relatorio = pd.DataFrame(linhas)
    df_relatorio = df_relatorio.sort_values("percentual_ausente", ascending=False)
    df_relatorio.to_csv(MISSING_VALUES_REPORT, index=False, encoding="utf-8")
    logger.info(f"Relatório de ausentes salvo: {MISSING_VALUES_REPORT}")
