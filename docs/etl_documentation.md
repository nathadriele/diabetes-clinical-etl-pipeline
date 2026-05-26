# Documentação do Pipeline ETL

## Visão Geral

O pipeline ETL (Extract, Transform, Load) do projeto **sus-diabetes-etl-pipeline** coleta, trata, padroniza, valida, integra e exporta dados públicos do SUS relacionados ao Diabetes Mellitus no Brasil.

## Arquitetura

```
Dados Brutos (DATASUS)
        │
        ▼
┌──────────────────┐
│     DOWNLOAD     │  download_datasus_data.py
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     EXTRACT      │  extract.py
└────────┬─────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌────────┐ ┌──────┐ ┌──────────────┐
│  SIH   │ │ SIM  │ │  População   │
│ Transform│ │Transform│ │  Transform   │
└────┬───┘ └───┬──┘ └──────┬───────┘
     │         │            │
     └────┬────┴────────────┘
          ▼
   ┌──────────────┐
   │   INTEGRATE  │  integrate.py
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   VALIDATE   │  validate.py
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │     LOAD     │  load.py
   └──────┬───────┘
          │
          ▼
  CSV / Parquet / Excel
```

## Etapas do Pipeline

### 1. Download (`download_datasus_data.py`)

- Tenta baixar dados reais dos servidores FTP do DATASUS
- Caso não disponível, gera dados sintéticos representativos para demonstração
- Fontes: SIH/SUS, SIM, População IBGE/DATASUS

### 2. Extração (`extract.py`)

- Lê os arquivos CSV brutos
- Retorna DataFrames para processamento
- Todas as colunas são lidas como string inicialmente

### 3. Transformação SIH (`transform_sih.py`)

Operações realizadas:
1. Padronização dos nomes das colunas
2. Mapeamento para nomes internos padrão
3. Conversão de tipos (numéricos, datas, strings)
4. Filtro por CID-10 E10-E14
5. Padronização de UF e adição de região
6. Padronização de município
7. Padronização de sexo
8. Criação de faixa etária
9. Criação de tipo_diabetes
10. Remoção de duplicidades
11. Tratamento de valores ausentes
12. Agrupamento por dimensões analíticas

### 4. Transformação SIM (`transform_sim.py`)

Operações similares à transformação SIH, adaptadas para as colunas do SIM.

### 5. Transformação População (`transform_population.py`)

- Padronização de colunas e tipos
- Validação de população > 0
- Padronização de UF, região e município

### 6. Integração (`integrate.py`)

- Merge left do SIH com SIM (por ano, mês, UF, município, sexo, faixa etária, CID-10)
- Merge com população (por ano, UF, município)
- Cálculo de indicadores epidemiológicos:
  - `taxa_internacao_100k`
  - `taxa_mortalidade_100k`
  - `taxa_mortalidade_hospitalar`
  - `valor_medio_internacao`
  - `media_permanencia`

### 7. Validação (`validate.py`)

Verificações executadas:
- Colunas obrigatórias presentes
- CID-10 restritos a E10-E14
- Valores numéricos sem negativos indevidos
- População > 0
- Anos no período analisado
- Duplicidades
- Ausência de identificadores individuais
- Coerência das taxas calculadas

### 8. Carga (`load.py`)

Exportação em 3 formatos:
- **CSV**: formato universal, leitura fácil
- **Parquet**: formato colunar, compressão eficiente
- **Excel**: formato para compartilhamento

## Execução

```bash
# Download dos dados
python -m src.data.download_datasus_data

# Pipeline completo
python -m src.data.pipeline

# Testes
pytest tests/

# Dashboard
streamlit run src/app/streamlit_app.py
```

## Logs

O pipeline gera logs detalhados em:
- **Console**: nível INFO
- **Arquivo**: `logs/pipeline.log` (nível DEBUG)

## Relatórios

Gerados em `data/reports/`:
- `data_quality_report.csv`: resultado dos checks de qualidade
- `missing_values_report.csv`: análise de valores ausentes
- `validation_report.csv`: resultado das validações
- `pipeline_execution_report.md`: resumo da execução
