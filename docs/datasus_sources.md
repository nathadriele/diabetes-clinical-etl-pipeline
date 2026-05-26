# Fontes de Dados do DATASUS

## Visão Geral

Este projeto utiliza dados públicos do Sistema Único de Saúde (SUS), disponibilizados pelo Departamento de Informática do SUS (DATASUS), vinculado ao Ministério da Saúde.

Todos os dados são públicos e agregados, sem identificadores individuais de pacientes.

---

## 1. SIH/SUS - Sistema de Informações Hospitalares

### Descrição
O SIH/SUS registra todas as internações hospitalares financiadas pelo SUS, incluindo informações sobre diagnósticos, procedimentos, custos e desfechos.

### Dados Utilizados
- **Internações hospitalares** por Diabetes Mellitus (CID-10 E10-E14)
- **Valores totais** das internações
- **Dias de permanência** hospitalar
- **Óbitos hospitalares** durante a internação
- **Procedimentos realizados**

### Variáveis Principais
| Variável | Descrição |
|----------|-----------|
| ANO_CMPT | Ano de competência |
| MES_CMPT | Mês de competência |
| UF_ZI | UF da zona de internação |
| MUNIC_RES | Código do município de residência |
| SEXO | Sexo do paciente |
| IDADE | Idade do paciente |
| DIAG_PRINC | Diagnóstico principal (CID-10) |
| N_AIH | Número da AIH (Autorização de Internação Hospitalar) |
| VAL_TOTAL | Valor total da internação |
| DIAS_PERM | Dias de permanência |
| MORTE | Indicador de óbito |

### Acesso
- URL: `ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados`
- Formato: DBC (compressado, requer conversão)
- Período: A partir de 2008

---

## 2. SIM - Sistema de Informações de Mortalidade

### Descrição
O SIM registra todos os óbitos ocorridos no Brasil, incluindo causa básica e causas associadas, conforme a Classificação Internacional de Doenças (CID-10).

### Dados Utilizados
- **Óbitos** por Diabetes Mellitus (CID-10 E10-E14) como causa básica
- **Local do óbito** (hospital, domicílio, via pública, etc.)

### Variáveis Principais
| Variável | Descrição |
|----------|-----------|
| ANO_OBITO | Ano do óbito |
| MES_OBITO | Mês do óbito |
| UF_RESID | UF de residência |
| MUNIC_RES | Código do município de residência |
| SEXO | Sexo do falecido |
| IDADE | Idade do falecido |
| CAUSA_BASICA | Causa básica do óbito (CID-10) |
| DT_OBITO | Data do óbito |
| LOCOCOR | Local de ocorrência do óbito |
| NUMERODO | Número da Declaração de Óbito |

### Acesso
- URL: `ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES`
- Formato: DBC (compressado, requer conversão)
- Período: A partir de 1996 (CID-10)

---

## 3. População Residente - IBGE/DATASUS

### Descrição
Estimativas de população residente por município, utilizadas para o cálculo de taxas epidemiológicas por 100 mil habitantes.

### Fontes
- **IBGE**: Censos demográficos e estimativas intercensitárias
- **DATASUS**: Tabulação de população residente

### Variáveis Principais
| Variável | Descrição |
|----------|-----------|
| ANO | Ano de referência |
| UF | Unidade da Federação |
| MUNICIPIO | Nome do município |
| COD_MUNICIPIO | Código IBGE do município |
| POPULACAO | População residente estimada |

### Acesso
- DATASUS: `https://datasus.saude.gov.br/populacao-residente/`
- IBGE: `https://www.ibge.gov.br/estatisticas/sociais/populacao.html`

---

## Notas Importantes

1. **Dados Públicos**: Todos os dados utilizados são de acesso público e podem ser utilizados para fins de pesquisa e análise.
2. **Dados Agregados**: O pipeline trabalha exclusivamente com dados agregados, sem identificadores individuais de pacientes.
3. **Período de Análise**: 2019 a 2023 (configurável em `src/config/settings.py`).
4. **Cobertura**: Os dados do SIH e SIM cobrem todo o território nacional, porém a completude pode variar por município e ano.
5. **Atualização**: O DATASUS atualiza os dados periodicamente, podendo haver diferenças entre extrações em datas diferentes.

## Referências

- [DATASUS](https://datasus.saude.gov.br/)
- [TabNet DATASUS](http://tabnet.datasus.gov.br/)
- [Manual do SIH/SUS](http://tabnet.datasus.gov.br/cgi/sih/Descritivos_SIH.htm)
- [Manual do SIM](http://tabnet.datasus.gov.br/cgi/sim/Descritivos_SIM.htm)
