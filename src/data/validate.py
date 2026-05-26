"""Validação de integridade, consistência e completude dos dados processados. Autora: Nathalia Adriele"""

import pandas as pd
import numpy as np
from loguru import logger
from datetime import datetime

from src.config.settings import (
    CID10_CODES,
    CID10_PREFIXES,
    START_YEAR,
    END_YEAR,
    COLUNAS_BASE_FINAL,
    COLUNAS_OBRIGATORIAS_SIH,
    COLUNAS_OBRIGATORIAS_SIM,
    COLUNAS_OBRIGATORIAS_POP,
    REPORTS_DIR,
    VALIDATION_REPORT,
)


def validate_data(df: pd.DataFrame) -> dict:
    """Executa todas as validações na base de dados processada."""
    logger.info("Iniciando validação dos dados processados...")

    resultados = {}

    resultados["colunas_obrigatorias"] = _validar_colunas_obrigatorias(df)
    resultados["cid10_validos"] = _validar_cid10(df)
    resultados["valores_numericos"] = _validar_valores_numericos(df)
    resultados["populacao"] = _validar_populacao(df)
    resultados["anos"] = _validar_anos(df)
    resultados["duplicidades"] = _validar_duplicidades(df)
    resultados["identificadores"] = _validar_ausencia_identificadores(df)
    resultados["taxas"] = _validar_taxas(df)

    _gerar_relatorio_validacao(resultados)

    total_validacoes = len(resultados)
    validacoes_passaram = sum(
        1 for r in resultados.values() if r.get("status") == "PASS"
    )
    validacoes_falharam = total_validacoes - validacoes_passaram

    logger.info(f"Validação concluída: {validacoes_passaram}/{total_validacoes} passaram")

    if validacoes_falharam > 0:
        logger.warning(f"{validacoes_falharam} validações falharam:")
        for nome, resultado in resultados.items():
            if resultado.get("status") != "PASS":
                logger.warning(f"  - {nome}: {resultado.get('mensagem', 'Falha')}")

    return resultados


def _validar_colunas_obrigatorias(df: pd.DataFrame) -> dict:
    colunas_esperadas = [
        "ano", "mes", "uf", "sexo", "faixa_etaria", "cid10",
        "internacoes", "obitos_sim", "populacao",
        "taxa_internacao_100k", "taxa_mortalidade_100k",
    ]

    colunas_ausentes = [c for c in colunas_esperadas if c not in df.columns]
    colunas_presentes = [c for c in colunas_esperadas if c in df.columns]

    if colunas_ausentes:
        return {
            "status": "FAIL",
            "mensagem": f"Colunas ausentes: {colunas_ausentes}",
            "detalhes": {
                "ausentes": colunas_ausentes,
                "presentes": colunas_presentes,
            },
        }

    return {
        "status": "PASS",
        "mensagem": f"Todas as {len(colunas_esperadas)} colunas obrigatórias presentes",
    }


def _validar_cid10(df: pd.DataFrame) -> dict:
    if "cid10" not in df.columns:
        return {"status": "FAIL", "mensagem": "Coluna cid10 não encontrada"}

    cid10_unicos = df["cid10"].dropna().unique()
    cid10_invalidos = [
        c for c in cid10_unicos
        if not str(c).upper().startswith(CID10_PREFIXES)
    ]

    if cid10_invalidos:
        return {
            "status": "FAIL",
            "mensagem": f"CID-10 fora do escopo: {cid10_invalidos[:10]}",
            "detalhes": {"invalidos": list(cid10_invalidos[:20])},
        }

    return {
        "status": "PASS",
        "mensagem": f"Todos os {len(cid10_unicos)} CID-10 são válidos (E10-E14)",
    }


def _validar_valores_numericos(df: pd.DataFrame) -> dict:
    colunas_verificar = [
        "internacoes", "valor_total", "dias_permanencia",
        "obitos_hospitalares", "obitos_sim", "populacao",
        "taxa_internacao_100k", "taxa_mortalidade_100k",
        "media_permanencia", "valor_medio_internacao",
    ]

    problemas = {}
    for col in colunas_verificar:
        if col in df.columns:
            negativos = (df[col] < 0).sum()
            if negativos > 0:
                problemas[col] = int(negativos)

    if problemas:
        return {
            "status": "FAIL",
            "mensagem": f"Valores negativos encontrados: {problemas}",
            "detalhes": problemas,
        }

    return {
        "status": "PASS",
        "mensagem": "Nenhum valor negativo indevido encontrado",
    }


def _validar_populacao(df: pd.DataFrame) -> dict:
    if "populacao" not in df.columns:
        return {"status": "FAIL", "mensagem": "Coluna populacao não encontrada"}

    pop_zero = (df["populacao"] == 0).sum()
    pop_negativa = (df["populacao"] < 0).sum()

    if pop_negativa > 0:
        return {
            "status": "FAIL",
            "mensagem": f"População negativa em {pop_negativa} registros",
        }

    if pop_zero > 0:
        logger.warning(f"População zero em {pop_zero} registros (pode ser esperado)")
        return {
            "status": "PASS",
            "mensagem": f"População validada ({pop_zero} registros com zero)",
            "detalhes": {"registros_zero": int(pop_zero)},
        }

    return {
        "status": "PASS",
        "mensagem": "Todos os registros têm população > 0",
    }


def _validar_anos(df: pd.DataFrame) -> dict:
    if "ano" not in df.columns:
        return {"status": "FAIL", "mensagem": "Coluna ano não encontrada"}

    anos = pd.to_numeric(df["ano"], errors="coerce").dropna().unique()
    anos_fora = [a for a in anos if a < START_YEAR or a > END_YEAR]

    if anos_fora:
        return {
            "status": "FAIL",
            "mensagem": f"Anos fora do período ({START_YEAR}-{END_YEAR}): {anos_fora}",
        }

    return {
        "status": "PASS",
        "mensagem": f"Anos dentro do período {START_YEAR}-{END_YEAR}: {sorted(anos)}",
    }


def _validar_duplicidades(df: pd.DataFrame) -> dict:
    subset = ["ano", "mes", "uf", "codigo_municipio", "sexo", "faixa_etaria", "cid10"]
    subset_existentes = [c for c in subset if c in df.columns]

    if not subset_existentes:
        return {"status": "PASS", "mensagem": "Sem colunas suficientes para verificar duplicidades"}

    duplicatas = df.duplicated(subset=subset_existentes, keep=False).sum()

    if duplicatas > 0:
        return {
            "status": "FAIL",
            "mensagem": f"{duplicatas} registros duplicados encontrados",
            "detalhes": {"duplicatas": int(duplicatas)},
        }

    return {
        "status": "PASS",
        "mensagem": "Nenhuma duplicidade encontrada nas dimensões analíticas",
    }


def _validar_ausencia_identificadores(df: pd.DataFrame) -> dict:
    colunas_proibidas = [
        "nome", "cpf", "cns", "cartao_sus", "telefone",
        "endereco", "nome_paciente", "nome_mae",
    ]

    colunas_df = [c.lower() for c in df.columns]
    encontradas = [c for c in colunas_proibidas if c in colunas_df]

    if encontradas:
        return {
            "status": "FAIL",
            "mensagem": f"Identificadores individuais encontrados: {encontradas}",
        }

    return {
        "status": "PASS",
        "mensagem": "Ausência de identificadores individuais confirmada",
    }


def _validar_taxas(df: pd.DataFrame) -> dict:
    problemas = []

    if "taxa_mortalidade_hospitalar" in df.columns:
        taxa_max = df["taxa_mortalidade_hospitalar"].max()
        if taxa_max > 100:
            problemas.append(f"Taxa mortalidade hospitalar > 100%: {taxa_max}")

    if "taxa_internacao_100k" in df.columns:
        taxa_max = df["taxa_internacao_100k"].max()
        if taxa_max > 10000:
            problemas.append(f"Taxa internação > 10.000/100k: {taxa_max}")

    if "taxa_mortalidade_100k" in df.columns:
        taxa_max = df["taxa_mortalidade_100k"].max()
        if taxa_max > 5000:
            problemas.append(f"Taxa mortalidade > 5.000/100k: {taxa_max}")

    if problemas:
        return {
            "status": "FAIL",
            "mensagem": f"Taxas fora do range esperado: {problemas}",
        }

    return {
        "status": "PASS",
        "mensagem": "Todas as taxas estão em ranges esperados",
    }


def _gerar_relatorio_validacao(resultados: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    linhas = []
    for nome, resultado in resultados.items():
        linhas.append({
            "validacao": nome,
            "status": resultado.get("status", "N/A"),
            "mensagem": resultado.get("mensagem", ""),
            "data_validacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    df_relatorio = pd.DataFrame(linhas)
    df_relatorio.to_csv(VALIDATION_REPORT, index=False, encoding="utf-8")
    logger.info(f"Relatório de validação salvo: {VALIDATION_REPORT}")
