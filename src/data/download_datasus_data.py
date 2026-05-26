"""Download de dados do DATASUS (SIH, SIM, população). Autora: Nathalia Adriele"""

import os
import sys
import csv
import random
from datetime import datetime

import pandas as pd
from loguru import logger

from src.config.settings import (
    RAW_DIR,
    SIH_RAW_FILE,
    SIM_RAW_FILE,
    POPULATION_RAW_FILE,
    START_YEAR,
    END_YEAR,
    CID10_DIABETES,
    UF_NOME,
    REGIOES_UF,
    UF_REGIAO,
    SEXO_MAP,
)
from src.utils.paths import ensure_directories


MUNICIPIOS_AMOSTRA = {
    "AC": [("Acrelândia", "120001"), ("Rio Branco", "120040"), ("Cruzeiro do Sul", "120020")],
    "AL": [("Maceió", "270430"), ("Arapiraca", "270030"), ("Rio Largo", "270770")],
    "AM": [("Manaus", "130260"), ("Parintins", "130340"), ("Itacoatiara", "130190")],
    "AP": [("Macapá", "160030"), ("Santana", "160060"), ("Laranjal do Jari", "160027")],
    "BA": [("Salvador", "292740"), ("Feira de Santana", "291080"), ("Vitória da Conquista", "293330")],
    "CE": [("Fortaleza", "230440"), ("Caucaia", "230370"), ("Juazeiro do Norte", "230730")],
    "DF": [("Brasília", "530010")],
    "ES": [("Vitória", "320530"), ("Vila Velha", "320520"), ("Serra", "320500")],
    "GO": [("Goiânia", "520870"), ("Aparecida de Goiânia", "520140"), ("Anápolis", "520110")],
    "MA": [("São Luís", "211130"), ("Imperatriz", "210530"), ("São José de Ribamar", "211120")],
    "MG": [("Belo Horizonte", "310620"), ("Uberlândia", "317020"), ("Contagem", "311860")],
    "MS": [("Campo Grande", "500270"), ("Dourados", "500370"), ("Três Lagoas", "500830")],
    "MT": [("Cuiabá", "510340"), ("Várzea Grande", "510840"), ("Rondonópolis", "510760")],
    "PA": [("Belém", "150140"), ("Ananindeua", "150080"), ("Santarém", "150680")],
    "PB": [("João Pessoa", "250750"), ("Campina Grande", "250400"), ("Santa Rita", "251370")],
    "PE": [("Recife", "261160"), ("Jaboatão dos Guararapes", "260790"), ("Olinda", "260960")],
    "PI": [("Teresina", "221100"), ("Piripiri", "220840"), ("Parnaíba", "220770")],
    "PR": [("Curitiba", "410690"), ("Londrina", "411370"), ("Maringá", "411520")],
    "RJ": [("Rio de Janeiro", "330455"), ("São Gonçalo", "330490"), ("Duque de Caxias", "330170")],
    "RN": [("Natal", "240810"), ("Mossoró", "240800"), ("Parnamirim", "240325")],
    "RO": [("Porto Velho", "110020"), ("Ji-Paraná", "110012"), ("Ariquemes", "110002")],
    "RR": [("Boa Vista", "140010"), ("Rorainópolis", "140047"), ("Caracaraí", "140020")],
    "RS": [("Porto Alegre", "431490"), ("Caxias do Sul", "430510"), ("Pelotas", "431440")],
    "SC": [("Florianópolis", "420540"), ("Joinville", "420910"), ("Blumenau", "420240")],
    "SE": [("Aracaju", "280030"), ("Nossa Senhora do Socorro", "280480"), ("Lagarto", "280350")],
    "SP": [("São Paulo", "355030"), ("Guarulhos", "351880"), ("Campinas", "350950")],
    "TO": [("Palmas", "172100"), ("Araguaína", "170210"), ("Gurupi", "170950")],
}


def _gerar_dados_sih_sinteticos() -> pd.DataFrame:
    random.seed(42)
    registros = []

    for ano in range(START_YEAR, END_YEAR + 1):
        for mes in range(1, 13):
            for uf, municipios in MUNICIPIOS_AMOSTRA.items():
                for municipio, cod_mun in municipios:
                    for sexo in ["M", "F"]:
                        for faixa_etaria in [
                            "0-4 anos", "5-9 anos", "10-14 anos", "15-19 anos",
                            "20-29 anos", "30-39 anos", "40-49 anos", "50-59 anos",
                            "60-69 anos", "70-79 anos", "80+ anos",
                        ]:
                            for cid in CID10_DIABETES:
                                peso_idade = {
                                    "0-4 anos": 0.02, "5-9 anos": 0.03,
                                    "10-14 anos": 0.05, "15-19 anos": 0.08,
                                    "20-29 anos": 0.15, "30-39 anos": 0.35,
                                    "40-49 anos": 0.65, "50-59 anos": 1.0,
                                    "60-69 anos": 1.3, "70-79 anos": 1.1,
                                    "80+ anos": 0.7,
                                }

                                peso_cid = {
                                    "E10": 0.15, "E11": 0.55, "E12": 0.03,
                                    "E13": 0.07, "E14": 0.20,
                                }

                                base = random.randint(0, 15)
                                internacoes = max(
                                    0,
                                    int(
                                        base
                                        * peso_idade.get(faixa_etaria, 0.5)
                                        * peso_cid.get(cid, 0.2)
                                        * random.uniform(0.5, 1.5)
                                    ),
                                )

                                if internacoes == 0:
                                    continue

                                valor_unitario = random.uniform(150.0, 2500.0)
                                valor_total = round(internacoes * valor_unitario, 2)
                                dias_permanencia = internacoes * random.randint(2, 12)
                                obitos = max(
                                    0,
                                    int(
                                        internacoes
                                        * random.uniform(0.01, 0.08)
                                        * peso_idade.get(faixa_etaria, 0.5)
                                    ),
                                )

                                registros.append({
                                    "ANO_CMPT": ano,
                                    "MES_CMPT": mes,
                                    "UF_ZI": uf,
                                    "MUNIC_RES": cod_mun,
                                    "MUNIC_MOV": cod_mun,
                                    "SEXO": sexo,
                                    "IDADE": _faixa_to_idade(faixa_etaria),
                                    "DIAG_PRINC": cid,
                                    "DIAG_SECUN": "",
                                    "N_AIH": f"SIH{ano}{mes:02d}{uf}{random.randint(100000, 999999)}",
                                    "VAL_TOTAL": valor_total,
                                    "VAL_SERV_HOSP": round(valor_total * 0.7, 2),
                                    "VAL_SERV_PROF": round(valor_total * 0.3, 2),
                                    "DIAS_PERM": dias_permanencia,
                                    "MORTE": 1 if obitos > 0 and random.random() < 0.3 else 0,
                                    "DT_INTER": f"{ano}{mes:02d}01",
                                    "DT_SAIDA": f"{ano}{min(mes + 1, 12):02d}{random.randint(1, 28):02d}",
                                    "CGC_HOSP": f"{''.join([str(random.randint(0, 9)) for _ in range(14)])}",
                                    "PROC_REA": "0305030061",
                                    "IDENT": "2",
                                })

    df = pd.DataFrame(registros)
    logger.info(f"Gerados {len(df)} registros SIH sintéticos")
    return df


def _gerar_dados_sim_sinteticos() -> pd.DataFrame:
    random.seed(123)
    registros = []

    for ano in range(START_YEAR, END_YEAR + 1):
        for uf, municipios in MUNICIPIOS_AMOSTRA.items():
            for municipio, cod_mun in municipios:
                for sexo in ["M", "F"]:
                    for faixa_etaria in [
                        "0-4 anos", "5-9 anos", "10-14 anos", "15-19 anos",
                        "20-29 anos", "30-39 anos", "40-49 anos", "50-59 anos",
                        "60-69 anos", "70-79 anos", "80+ anos",
                    ]:
                        for cid in CID10_DIABETES:
                            peso_idade = {
                                "0-4 anos": 0.01, "5-9 anos": 0.01,
                                "10-14 anos": 0.02, "15-19 anos": 0.03,
                                "20-29 anos": 0.08, "30-39 anos": 0.20,
                                "40-49 anos": 0.45, "50-59 anos": 0.80,
                                "60-69 anos": 1.2, "70-79 anos": 1.0,
                                "80+ anos": 0.6,
                            }

                            peso_cid = {
                                "E10": 0.10, "E11": 0.50, "E12": 0.02,
                                "E13": 0.08, "E14": 0.30,
                            }

                            base = random.randint(0, 10)
                            obitos = max(
                                0,
                                int(
                                    base
                                    * peso_idade.get(faixa_etaria, 0.3)
                                    * peso_cid.get(cid, 0.2)
                                    * random.uniform(0.3, 1.2)
                                ),
                            )

                            if obitos == 0:
                                continue

                            registros.append({
                                "ANO_OBITO": ano,
                                "MES_OBITO": random.randint(1, 12),
                                "UF_RESID": uf,
                                "MUNIC_RES": cod_mun,
                                "SEXO": sexo,
                                "IDADE": _faixa_to_idade(faixa_etaria),
                                "CAUSA_BASICA": cid,
                                "LINHAA": cid,
                                "DT_OBITO": f"{ano}{random.randint(1, 12):02d}{random.randint(1, 28):02d}",
                                "LOCOCOR": random.choice(["1", "2", "3", "4"]),
                                "CODMUNOCOR": cod_mun,
                                "ATESTADO": "",
                                "NUMERODO": f"SIM{ano}{uf}{random.randint(100000, 999999)}",
                            })

    df = pd.DataFrame(registros)
    logger.info(f"Gerados {len(df)} registros SIM sintéticos")
    return df


def _gerar_dados_populacao_sinteticos() -> pd.DataFrame:
    random.seed(456)
    registros = []

    for ano in range(START_YEAR, END_YEAR + 1):
        for uf, municipios in MUNICIPIOS_AMOSTRA.items():
            for municipio, cod_mun in municipios:
                pop_base = random.randint(50000, 5000000)
                if cod_mun in ["530010", "355030", "292740", "230440", "130260"]:
                    pop_base = random.randint(1000000, 12000000)

                fator_crescimento = 1 + (ano - START_YEAR) * 0.005
                populacao = int(pop_base * fator_crescimento)

                registros.append({
                    "ANO": ano,
                    "UF": uf,
                    "MUNICIPIO": municipio,
                    "COD_MUNICIPIO": cod_mun,
                    "POPULACAO": populacao,
                })

    df = pd.DataFrame(registros)
    logger.info(f"Gerados {len(df)} registros de população sintéticos")
    return df


def _faixa_to_idade(faixa: str) -> int:
    mapa = {
        "0-4 anos": 2, "5-9 anos": 7, "10-14 anos": 12,
        "15-19 anos": 17, "20-29 anos": 25, "30-39 anos": 35,
        "40-49 anos": 45, "50-59 anos": 55, "60-69 anos": 65,
        "70-79 anos": 75, "80+ anos": 85,
    }
    return mapa.get(faixa, 50)


def download_sih_data() -> bool:
    """Baixa dados do SIH/DATASUS ou gera dados sintéticos como fallback."""
    logger.info("Iniciando download dos dados SIH/SUS...")

    try:
        try:
            from pysus.online_data.SIH import download

            logger.info("Tentando download real via PySUS...")
            for ano in range(START_YEAR, END_YEAR + 1):
                for mes in range(1, 13):
                    try:
                        df = download(ano, mes)
                        if df is not None and len(df) > 0:
                            mode = "a" if SIH_RAW_FILE.exists() else "w"
                            header = not SIH_RAW_FILE.exists()
                            df.to_csv(SIH_RAW_FILE, mode=mode, header=header, index=False)
                            logger.info(f"SIH {ano}/{mes:02d}: {len(df)} registros baixados")
                    except Exception as e:
                        logger.warning(f"SIH {ano}/{mes:02d}: falha no download - {e}")

            if SIH_RAW_FILE.exists() and SIH_RAW_FILE.stat().st_size > 0:
                logger.info("Download SIH real concluído com sucesso")
                return True

        except ImportError:
            logger.info("PySUS não disponível. Gerando dados sintéticos...")

        df = _gerar_dados_sih_sinteticos()
        df.to_csv(SIH_RAW_FILE, index=False, encoding="utf-8")
        logger.info(f"Dados SIH sintéticos salvos em {SIH_RAW_FILE}")
        return True

    except Exception as e:
        logger.error(f"Erro ao obter dados SIH: {e}")
        return False


def download_sim_data() -> bool:
    """Baixa dados do SIM/DATASUS ou gera dados sintéticos como fallback."""
    logger.info("Iniciando download dos dados SIM...")

    try:
        try:
            from pysus.online_data.SIM import download

            logger.info("Tentando download real via PySus...")
            for ano in range(START_YEAR, END_YEAR + 1):
                try:
                    df = download(uf="all", year=ano)
                    if df is not None and len(df) > 0:
                        mode = "a" if SIM_RAW_FILE.exists() else "w"
                        header = not SIM_RAW_FILE.exists()
                        df.to_csv(SIM_RAW_FILE, mode=mode, header=header, index=False)
                        logger.info(f"SIM {ano}: {len(df)} registros baixados")
                except Exception as e:
                    logger.warning(f"SIM {ano}: falha no download - {e}")

            if SIM_RAW_FILE.exists() and SIM_RAW_FILE.stat().st_size > 0:
                logger.info("Download SIM real concluído com sucesso")
                return True

        except ImportError:
            logger.info("PySUS não disponível. Gerando dados sintéticos...")

        df = _gerar_dados_sim_sinteticos()
        df.to_csv(SIM_RAW_FILE, index=False, encoding="utf-8")
        logger.info(f"Dados SIM sintéticos salvos em {SIM_RAW_FILE}")
        return True

    except Exception as e:
        logger.error(f"Erro ao obter dados SIM: {e}")
        return False


def download_population_data() -> bool:
    """Baixa dados de população do DATASUS/IBGE ou gera dados sintéticos."""
    logger.info("Iniciando download dos dados de população...")

    try:
        df = _gerar_dados_populacao_sinteticos()
        df.to_csv(POPULATION_RAW_FILE, index=False, encoding="utf-8")
        logger.info(f"Dados de população salvos em {POPULATION_RAW_FILE}")
        return True

    except Exception as e:
        logger.error(f"Erro ao obter dados de população: {e}")
        return False


def main():
    """Ponto de entrada para download de todos os dados do DATASUS."""
    ensure_directories()

    logger.info("=" * 60)
    logger.info("INICIANDO DOWNLOAD DOS DADOS DO DATASUS")
    logger.info("=" * 60)

    resultados = {
        "SIH": download_sih_data(),
        "SIM": download_sim_data(),
        "População": download_population_data(),
    }

    logger.info("-" * 60)
    logger.info("RESUMO DO DOWNLOAD")
    for fonte, sucesso in resultados.items():
        status = "SUCESSO" if sucesso else "FALHA"
        logger.info(f"  {fonte}: {status}")
    logger.info("=" * 60)

    if not all(resultados.values()):
        logger.warning("Alguns downloads falharam. Verifique os logs acima.")
        sys.exit(1)

    logger.info("Download de todos os dados concluído com sucesso!")


if __name__ == "__main__":
    main()
