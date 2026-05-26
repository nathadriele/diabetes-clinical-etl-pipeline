"""Orquestrador do pipeline ETL completo. Autora: Nathalia Adriele"""

import sys
import time
from datetime import datetime

import pandas as pd
from loguru import logger

from src.utils.paths import ensure_directories
from src.utils.logger import setup_logger
from src.data.extract import extract_all
from src.data.transform_sih import transform_sih
from src.data.transform_sim import transform_sim
from src.data.transform_population import transform_population
from src.data.integrate import integrate_data
from src.data.validate import validate_data
from src.data.load import load_data
from src.quality.quality_checks import run_quality_checks
from src.quality.quality_report import generate_quality_report
from src.config.settings import PIPELINE_EXECUTION_REPORT, REPORTS_DIR


def run_pipeline() -> dict:
    """Executa o pipeline ETL completo de forma sequencial."""
    inicio = time.time()
    resultados = {}

    logger.info("=" * 70)
    logger.info("INICIANDO PIPELINE ETL - SUS DIABETES")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    try:
        ensure_directories()
        logger.info("[0/8] Setup de diretórios: OK")
    except Exception as e:
        logger.error(f"[0/8] Erro no setup: {e}")
        resultados["setup"] = {"status": "FALHA", "erro": str(e)}
        _gerar_relatorio_execucao(resultados, inicio)
        return resultados

    try:
        logger.info("-" * 60)
        logger.info("[1/8] Extraindo dados brutos...")
        data = extract_all()
        resultados["extracao"] = {
            "status": "SUCESSO",
            "sih": len(data["sih"]),
            "sim": len(data["sim"]),
            "population": len(data["population"]),
        }
        logger.info(f"[1/8] Extração: SIH={len(data['sih'])}, SIM={len(data['sim'])}, POP={len(data['population'])}")
    except Exception as e:
        logger.error(f"[1/8] Erro na extração: {e}")
        resultados["extracao"] = {"status": "FALHA", "erro": str(e)}
        _gerar_relatorio_execucao(resultados, inicio)
        return resultados

    try:
        logger.info("-" * 60)
        logger.info("[2/8] Transformando dados SIH...")
        df_sih = transform_sih(data["sih"])
        resultados["transformacao_sih"] = {
            "status": "SUCESSO",
            "registros": len(df_sih),
        }
        logger.info(f"[2/8] Transformação SIH: {len(df_sih)} registros")
    except Exception as e:
        logger.error(f"[2/8] Erro na transformação SIH: {e}")
        resultados["transformacao_sih"] = {"status": "FALHA", "erro": str(e)}
        _gerar_relatorio_execucao(resultados, inicio)
        return resultados

    try:
        logger.info("-" * 60)
        logger.info("[3/8] Transformando dados SIM...")
        df_sim = transform_sim(data["sim"])
        resultados["transformacao_sim"] = {
            "status": "SUCESSO",
            "registros": len(df_sim),
        }
        logger.info(f"[3/8] Transformação SIM: {len(df_sim)} registros")
    except Exception as e:
        logger.error(f"[3/8] Erro na transformação SIM: {e}")
        resultados["transformacao_sim"] = {"status": "FALHA", "erro": str(e)}
        _gerar_relatorio_execucao(resultados, inicio)
        return resultados

    try:
        logger.info("-" * 60)
        logger.info("[4/8] Transformando dados de população...")
        df_pop = transform_population(data["population"])
        resultados["transformacao_populacao"] = {
            "status": "SUCESSO",
            "registros": len(df_pop),
        }
        logger.info(f"[4/8] Transformação População: {len(df_pop)} registros")
    except Exception as e:
        logger.error(f"[4/8] Erro na transformação População: {e}")
        resultados["transformacao_populacao"] = {"status": "FALHA", "erro": str(e)}
        _gerar_relatorio_execucao(resultados, inicio)
        return resultados

    try:
        logger.info("-" * 60)
        logger.info("[5/8] Integrando bases de dados...")
        df_integrado = integrate_data(df_sih, df_sim, df_pop)
        resultados["integracao"] = {
            "status": "SUCESSO",
            "registros": len(df_integrado),
            "colunas": len(df_integrado.columns),
        }
        logger.info(f"[5/8] Integração: {len(df_integrado)} registros, {len(df_integrado.columns)} colunas")
    except Exception as e:
        logger.error(f"[5/8] Erro na integração: {e}")
        resultados["integracao"] = {"status": "FALHA", "erro": str(e)}
        _gerar_relatorio_execucao(resultados, inicio)
        return resultados

    try:
        logger.info("-" * 60)
        logger.info("[6/8] Validando dados processados...")
        validacoes = validate_data(df_integrado)
        passaram = sum(1 for v in validacoes.values() if v.get("status") == "PASS")
        total = len(validacoes)
        resultados["validacao"] = {
            "status": "SUCESSO" if passaram == total else "ALERTA",
            "passaram": passaram,
            "total": total,
            "detalhes": validacoes,
        }
        logger.info(f"[6/8] Validação: {passaram}/{total} passaram")
    except Exception as e:
        logger.error(f"[6/8] Erro na validação: {e}")
        resultados["validacao"] = {"status": "FALHA", "erro": str(e)}

    try:
        logger.info("-" * 60)
        logger.info("[7/8] Exportando dados processados...")
        exportacoes = load_data(df_integrado)
        sucessos = sum(1 for v in exportacoes.values() if v["status"] == "SUCESSO")
        resultados["carga"] = {
            "status": "SUCESSO" if sucessos == len(exportacoes) else "ALERTA",
            "formatos_exportados": exportacoes,
        }
        logger.info(f"[7/8] Exportação: {sucessos}/{len(exportacoes)} formatos")
    except Exception as e:
        logger.error(f"[7/8] Erro na exportação: {e}")
        resultados["carga"] = {"status": "FALHA", "erro": str(e)}

    try:
        logger.info("-" * 60)
        logger.info("[8/8] Gerando relatórios de qualidade...")
        quality_results = run_quality_checks(df_integrado)
        generate_quality_report(quality_results, df_integrado)
        resultados["qualidade"] = {
            "status": "SUCESSO",
            "registros": len(quality_results),
        }
        logger.info(f"[8/8] Relatórios de qualidade gerados")
    except Exception as e:
        logger.error(f"[8/8] Erro nos relatórios de qualidade: {e}")
        resultados["qualidade"] = {"status": "FALHA", "erro": str(e)}

    fim = time.time()
    duracao = fim - inicio

    logger.info("=" * 70)
    logger.info("PIPELINE ETL CONCLUÍDO")
    logger.info(f"Duração total: {duracao:.2f} segundos")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    resultados["duracao_segundos"] = round(duracao, 2)
    resultados["timestamp_fim"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    _gerar_relatorio_execucao(resultados, inicio)

    return resultados


def _gerar_relatorio_execucao(resultados: dict, inicio: float) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    duracao = time.time() - inicio

    linhas = [
        "# Relatório de Execução do Pipeline ETL",
        "",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duração:** {duracao:.2f} segundos",
        "",
        "## Resumo das Etapas",
        "",
        "| Etapa | Status | Detalhes |",
        "|-------|--------|----------|",
    ]

    for etapa, resultado in resultados.items():
        if isinstance(resultado, dict):
            status = resultado.get("status", "N/A")
            if etapa == "extracao":
                detalhes = f"SIH={resultado.get('sih', 0)}, SIM={resultado.get('sim', 0)}, POP={resultado.get('population', 0)}"
            elif "registros" in resultado:
                detalhes = f"{resultado.get('registros', 0)} registros"
            elif "passaram" in resultado:
                detalhes = f"{resultado.get('passaram', 0)}/{resultado.get('total', 0)} validações"
            elif "formatos_exportados" in resultado:
                detalhes = "Ver relatório de exportação"
            else:
                detalhes = resultado.get("erro", "")
            linhas.append(f"| {etapa} | {status} | {detalhes} |")

    linhas.extend([
        "",
        "## Notas",
        "",
        "- Dados obtidos do DATASUS/SUS (fontes: SIH, SIM, IBGE)",
        "- Dados públicos agregados, sem identificadores individuais",
        "- CID-10 filtrados: E10, E11, E12, E13, E14 (Diabetes Mellitus)",
    ])

    conteudo = "\n".join(linhas)

    with open(PIPELINE_EXECUTION_REPORT, "w", encoding="utf-8") as f:
        f.write(conteudo)

    logger.info(f"Relatório de execução salvo: {PIPELINE_EXECUTION_REPORT}")


def main():
    setup_logger()
    resultados = run_pipeline()

    falhas = [
        k for k, v in resultados.items()
        if isinstance(v, dict) and v.get("status") == "FALHA"
    ]

    if falhas:
        logger.error(f"Pipeline falhou nas etapas: {falhas}")
        sys.exit(1)
    else:
        logger.info("Pipeline executado com sucesso!")


if __name__ == "__main__":
    main()
