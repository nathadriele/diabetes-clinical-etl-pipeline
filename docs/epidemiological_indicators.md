# Indicadores Epidemiológicos

## Visão Geral

Este documento descreve os indicadores epidemiológicos calculados pelo pipeline para análise de Diabetes Mellitus no SUS.

---

## Indicadores Calculados

### 1. Total de Internações

**Definição:** Soma do número de internações hospitalares por Diabetes Mellitus no período.

**Fórmula:**
```
total_internacoes = SUM(internacoes)
```

**Desagregação:** Por ano, UF, região, sexo, faixa etária, CID-10

---

### 2. Total de Óbitos Hospitalares

**Definição:** Soma de óbitos ocorridos durante internações hospitalares por Diabetes Mellitus.

**Fórmula:**
```
total_obitos_hospitalares = SUM(obitos_hospitalares)
```

---

### 3. Total de Óbitos SIM

**Definição:** Soma de óbitos por Diabetes Mellitus registrados no SIM.

**Fórmula:**
```
total_obitos_sim = SUM(obitos_sim)
```

---

### 4. Valor Total das Internações

**Definição:** Soma dos valores pagos pelo SUS pelas internações hospitalares.

**Fórmula:**
```
valor_total_internacoes = SUM(valor_total)
```

**Unidade:** Reais (R$)

---

### 5. Valor Médio por Internação

**Definição:** Custo médio por internação hospitalar.

**Fórmula:**
```
valor_medio_internacao = valor_total_internacoes / total_internacoes
```

**Unidade:** Reais (R$)

---

### 6. Média de Permanência Hospitalar

**Definição:** Número médio de dias de permanência por internação.

**Fórmula:**
```
media_permanencia = SUM(dias_permanencia) / total_internacoes
```

**Unidade:** Dias

---

### 7. Taxa de Mortalidade Hospitalar

**Definição:** Proporção de óbitos em relação ao total de internações.

**Fórmula:**
```
taxa_mortalidade_hospitalar = (obitos_hospitalares / internacoes) × 100
```

**Unidade:** Percentual (%)

**Interpretação:** Indica a gravidade dos casos e a qualidade da assistência hospitalar.

---

### 8. Taxa de Internação por 100 mil Habitantes

**Definição:** Número de internações por Diabetes Mellitus por 100 mil habitantes.

**Fórmula:**
```
taxa_internacao_100k = (internacoes / populacao) × 100.000
```

**Unidade:** Internações por 100 mil habitantes

**Interpretação:** Permite comparação entre regiões com diferentes tamanhos populacionais.

---

### 9. Taxa de Mortalidade por 100 mil Habitantes

**Definição:** Número de óbitos por Diabetes Mellitus por 100 mil habitantes.

**Fórmula:**
```
taxa_mortalidade_100k = (obitos_sim / populacao) × 100.000
```

**Unidade:** Óbitos por 100 mil habitantes

**Interpretação:** Indica o impacto da mortalidade por diabetes na população.

---

## Dimensões de Análise

Todos os indicadores podem ser calculados por diferentes dimensões:

| Dimensão | Descrição |
|----------|-----------|
| Ano | Série temporal (2019-2023) |
| Região | Região geográfica (N, NE, SE, S, CO) |
| UF | Unidade da Federação (27 UFs) |
| Sexo | Masculino, Feminino, Ignorado |
| Faixa Etária | 11 faixas etárias padrão |
| CID-10 | E10, E11, E12, E13, E14 |
| Tipo de Diabetes | Tipo 1, Tipo 2, Outros, Não especificado |

## Perguntas Respondidas

1. Como evoluíram as internações por Diabetes Mellitus no SUS?
2. Quais estados e regiões apresentam mais internações?
3. Qual é a distribuição por sexo e faixa etária?
4. Qual é o custo total e médio das internações?
5. Qual é a média de permanência hospitalar?
6. Qual é a mortalidade hospitalar associada às internações?
7. Como evoluíram os óbitos por Diabetes Mellitus?
8. Quais estados têm maiores taxas por 100 mil habitantes?
