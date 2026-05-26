"""Configurações centralizadas do pipeline ETL. Autora: Nathalia Adriele"""

from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

SIH_RAW_FILE = RAW_DIR / "sih_diabetes_raw.csv"
SIM_RAW_FILE = RAW_DIR / "sim_diabetes_raw.csv"
POPULATION_RAW_FILE = RAW_DIR / "population_raw.csv"

SIH_INTERIM_FILE = INTERIM_DIR / "sih_diabetes_interim.csv"
SIM_INTERIM_FILE = INTERIM_DIR / "sim_diabetes_interim.csv"
POPULATION_INTERIM_FILE = INTERIM_DIR / "population_interim.csv"

PROCESSED_CSV = PROCESSED_DIR / "diabetes_sus_processed.csv"
PROCESSED_PARQUET = PROCESSED_DIR / "diabetes_sus_processed.parquet"
PROCESSED_XLSX = PROCESSED_DIR / "diabetes_sus_processed.xlsx"

DATA_QUALITY_REPORT = REPORTS_DIR / "data_quality_report.csv"
MISSING_VALUES_REPORT = REPORTS_DIR / "missing_values_report.csv"
VALIDATION_REPORT = REPORTS_DIR / "validation_report.csv"
PIPELINE_EXECUTION_REPORT = REPORTS_DIR / "pipeline_execution_report.md"
LOG_FILE = LOGS_DIR / "pipeline.log"

START_YEAR = 2019
END_YEAR = 2023
ANOS_VALIDOS = list(range(START_YEAR, END_YEAR + 1))

CID10_DIABETES = {
    "E10": "Diabetes mellitus insulinodependente",
    "E11": "Diabetes mellitus não insulinodependente",
    "E12": "Diabetes mellitus relacionado com desnutrição",
    "E13": "Outros tipos especificados de diabetes mellitus",
    "E14": "Diabetes mellitus não especificado",
}

CID10_CODES = list(CID10_DIABETES.keys())
CID10_PREFIXES = tuple(CID10_DIABETES.keys())

REGIOES_UF = {
    "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
}

UF_NOME = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AM": "Amazonas",
    "AP": "Amapá",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso",
    "PA": "Pará",
    "PB": "Paraíba",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "PR": "Paraná",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RO": "Rondônia",
    "RR": "Roraima",
    "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina",
    "SE": "Sergipe",
    "SP": "São Paulo",
    "TO": "Tocantins",
}

UF_REGIAO = {}
for regiao, ufs in REGIOES_UF.items():
    for uf in ufs:
        UF_REGIAO[uf] = regiao

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

SEXO_MAP = {
    "M": "Masculino",
    "F": "Feminino",
    "1": "Masculino",
    "2": "Feminino",
    "3": "Ignorado",
    "9": "Ignorado",
    "0": "Ignorado",
    "I": "Ignorado",
    "masculino": "Masculino",
    "feminino": "Feminino",
    "ignorado": "Ignorado",
}

FAIXAS_ETARIAS = [
    "0-4 anos",
    "5-9 anos",
    "10-14 anos",
    "15-19 anos",
    "20-29 anos",
    "30-39 anos",
    "40-49 anos",
    "50-59 anos",
    "60-69 anos",
    "70-79 anos",
    "80+ anos",
    "Ignorado",
]


def classificar_faixa_etaria(idade: int) -> str:
    """Classifica a idade em faixa etária padrão."""
    if idade is None or (isinstance(idade, float) and idade != idade):
        return "Ignorado"
    try:
        idade = int(idade)
    except (ValueError, TypeError):
        return "Ignorado"

    if idade < 0:
        return "Ignorado"
    elif idade <= 4:
        return "0-4 anos"
    elif idade <= 9:
        return "5-9 anos"
    elif idade <= 14:
        return "10-14 anos"
    elif idade <= 19:
        return "15-19 anos"
    elif idade <= 29:
        return "20-29 anos"
    elif idade <= 39:
        return "30-39 anos"
    elif idade <= 49:
        return "40-49 anos"
    elif idade <= 59:
        return "50-59 anos"
    elif idade <= 69:
        return "60-69 anos"
    elif idade <= 79:
        return "70-79 anos"
    else:
        return "80+ anos"


COLUNAS_BASE_FINAL = [
    "ano",
    "mes",
    "regiao",
    "uf",
    "municipio",
    "codigo_municipio",
    "sexo",
    "faixa_etaria",
    "cid10",
    "descricao_cid10",
    "tipo_diabetes",
    "internacoes",
    "valor_total",
    "valor_medio_internacao",
    "dias_permanencia",
    "media_permanencia",
    "obitos_hospitalares",
    "taxa_mortalidade_hospitalar",
    "obitos_sim",
    "populacao",
    "taxa_internacao_100k",
    "taxa_mortalidade_100k",
    "fonte_dados",
    "data_extracao",
    "data_processamento",
]

COLUNAS_OBRIGATORIAS_SIH = [
    "ano",
    "mes",
    "uf",
    "municipio",
    "codigo_municipio",
    "sexo",
    "faixa_etaria",
    "cid10",
    "internacoes",
    "valor_total",
    "dias_permanencia",
    "obitos_hospitalares",
]

COLUNAS_OBRIGATORIAS_SIM = [
    "ano",
    "mes",
    "uf",
    "municipio",
    "codigo_municipio",
    "sexo",
    "faixa_etaria",
    "cid10",
    "obitos",
]

COLUNAS_OBRIGATORIAS_POP = [
    "ano",
    "uf",
    "municipio",
    "codigo_municipio",
    "populacao",
]

DATASUS_BASE_URL = "https://datasus.saude.gov.br"

SIH_DATASUS_SYSTEM = "SIH/SUS"
SIM_DATASUS_SYSTEM = "SIM"

# SIH: Sistema de Informações Hospitalares
SIH_FTP_BASE = "ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados"

# SIM: Sistema de Informações de Mortalidade
SIM_FTP_BASE = "ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES"

POPULATION_URL = "https://datasus.saude.gov.br/populacao-residente/"

DATA_EXTRACAO = datetime.now().strftime("%Y-%m-%d")
DATA_PROCESSAMENTO = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
