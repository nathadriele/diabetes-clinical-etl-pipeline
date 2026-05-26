# Dicionário de Dados

## Base Analítica Final: `diabetes_sus_processed`

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `ano` | int | Ano de referência | 2022 |
| `mes` | int | Mês de referência (1-12) | 6 |
| `regiao` | str | Região geográfica do Brasil | Sudeste |
| `uf` | str | Sigla da Unidade da Federação | SP |
| `municipio` | str | Nome do município | São Paulo |
| `codigo_municipio` | str | Código IBGE do município (6 dígitos) | 355030 |
| `sexo` | str | Sexo do paciente (Masculino/Feminino/Ignorado) | Masculino |
| `faixa_etaria` | str | Faixa etária do paciente | 50-59 anos |
| `cid10` | str | Código CID-10 principal | E11 |
| `descricao_cid10` | str | Descrição do CID-10 | Diabetes mellitus não insulinodependente |
| `tipo_diabetes` | str | Classificação do tipo de diabetes | Não insulinodependente (Tipo 2) |
| `internacoes` | int | Número total de internações hospitalares | 150 |
| `valor_total` | float | Valor total das internações em reais (R$) | 225000.00 |
| `valor_medio_internacao` | float | Valor médio por internação em reais (R$) | 1500.00 |
| `dias_permanencia` | int | Total de dias de permanência hospitalar | 1050 |
| `media_permanencia` | float | Média de dias de permanência por internação | 7.0 |
| `obitos_hospitalares` | int | Número de óbitos durante internação | 5 |
| `taxa_mortalidade_hospitalar` | float | Taxa de mortalidade hospitalar (%) | 3.33 |
| `obitos_sim` | int | Número de óbitos segundo o SIM | 45 |
| `populacao` | int | População residente no período | 12000000 |
| `taxa_internacao_100k` | float | Taxa de internação por 100 mil habitantes | 1.25 |
| `taxa_mortalidade_100k` | float | Taxa de mortalidade por 100 mil habitantes | 0.38 |
| `fonte_dados` | str | Fonte(s) de dados utilizadas | SIH/SUS + SIM + IBGE |
| `data_extracao` | str | Data da extração dos dados | 2024-01-15 |
| `data_processamento` | str | Data e hora do processamento | 2024-01-15 14:30:00 |

## Faixas Etárias

| Faixa | Intervalo |
|-------|-----------|
| 0-4 anos | 0 a 4 anos |
| 5-9 anos | 5 a 9 anos |
| 10-14 anos | 10 a 14 anos |
| 15-19 anos | 15 a 19 anos |
| 20-29 anos | 20 a 29 anos |
| 30-39 anos | 30 a 39 anos |
| 40-49 anos | 40 a 49 anos |
| 50-59 anos | 50 a 59 anos |
| 60-69 anos | 60 a 69 anos |
| 70-79 anos | 70 a 79 anos |
| 80+ anos | 80 anos ou mais |
| Ignorado | Idade não informada |

## CID-10 - Diabetes Mellitus

| Código | Descrição | Tipo |
|--------|-----------|------|
| E10 | Diabetes mellitus insulinodependente | Tipo 1 |
| E11 | Diabetes mellitus não insulinodependente | Tipo 2 |
| E12 | Diabetes mellitus relacionado com desnutrição | Relacionado à desnutrição |
| E13 | Outros tipos especificados de diabetes mellitus | Outros |
| E14 | Diabetes mellitus não especificado | Não especificado |

## Regiões e UFs

| Região | UFs |
|--------|-----|
| Norte | AC, AM, AP, PA, RO, RR, TO |
| Nordeste | AL, BA, CE, MA, PB, PE, PI, RN, SE |
| Sudeste | ES, MG, RJ, SP |
| Sul | PR, RS, SC |
| Centro-Oeste | DF, GO, MS, MT |
