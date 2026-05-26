# Limitações

## Visão Geral

Este documento lista as limitações conhecidas do pipeline e dos dados utilizados.

---

## Limitações dos Dados

### 1. Qualidade dos Dados Originais

Os dados do DATASUS estão sujeitos a problemas de qualidade inerentes aos sistemas de informação em saúde:
- **Sub-registro**: Nem todos os eventos de saúde são registrados, especialmente em regiões mais carentes.
- **Atraso na notificação**: Pode haver atraso na digitação e processamento dos dados.
- **Erros de preenchimento**: Erros na codificação de diagnósticos, sexo, idade e outros campos.
- **Dados incompletos**: Alguns campos podem não ser preenchidos corretamente.

### 2. Cobertura Geográfica

- A qualidade dos dados pode variar significativamente entre municípios e estados.
- Municípios menores podem ter sistemas de informação menos estruturados.
- A cobertura do SIM e SIH não é uniforme em todo o território nacional.

### 3. População Residente

- As estimativas populacionais do IBGE são interpoladas entre censos.
- Podem não refletir com precisão a população real em anos intercensitários.
- Migrações e movimentações populacionais podem não ser capturadas adequadamente.

### 4. Dados Sintéticos

- Quando o download dos dados reais não está disponível, o pipeline gera dados sintéticos.
- Os dados sintéticos são representativos apenas para fins de demonstração e teste.
- **NÃO devem ser utilizados para análises epidemiológicas reais.**

---

## Limitações Técnicas

### 1. Download dos Dados

- O download dos dados do DATASUS depende de conectividade com os servidores FTP.
- O formato DBC (derivado de DBF) requer bibliotecas específicas para conversão.
- Alguns arquivos podem estar indisponíveis temporariamente.

### 2. Desempenho

- O processamento pode ser lento para grandes volumes de dados.
- A exportação em Excel pode ser limitada pelo tamanho da planilha.
- O Parquet é recomendado para volumes grandes de dados.

### 3. Formato dos Dados

- O pipeline foi projetado para dados no formato atual do DATASUS.
- Mudanças no formato dos dados podem requerer ajustes no código.
- A codificação de caracteres pode variar entre arquivos.

---

## Limitações Analíticas

### 1. Dados Agregados

- Os dados são agregados por dimensões analíticas.
- Não é possível realizar análises individuais (nível paciente).
- Não há informação sobre comorbidades associadas ao diabetes.

### 2. Causalidade

- A presença de diabetes como diagnóstico principal não estabelece relação causal direta.
- O diabetes pode ser diagnóstico secundário em internações por outras causas.
- Os dados do SIM registram apenas a causa básica do óbito.

### 3. Comparabilidade Temporal

- Mudanças na codificação CID podem afetar a comparabilidade temporal.
- Alterações nos sistemas de informação podem introduzir artefatos nas séries temporais.

### 4. Indicadores

- As taxas por 100 mil habitantes são aproximadas, baseadas em estimativas populacionais.
- A taxa de mortalidade hospitalar não considera a gravidade dos casos.
- Os valores financeiros não são ajustados por inflação.

---

## Recomendações

1. Sempre verificar a data de extração dos dados.
2. Considerar as limitações na interpretação dos resultados.
3. Utilizar dados reais do DATASUS para análises epidemiológicas.
4. Complementar com outras fontes de dados quando possível.
5. Consultar a documentação oficial do DATASUS para detalhes sobre os sistemas.
6. Validar os resultados com especialistas em epidemiologia.
