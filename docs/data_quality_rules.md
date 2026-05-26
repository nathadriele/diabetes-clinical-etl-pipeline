# Regras de Qualidade dos Dados

## Visão Geral

Este documento descreve as regras de qualidade aplicadas aos dados durante o pipeline ETL.

---

## 1. Completude de Colunas

**Regra:** Todas as colunas obrigatórias devem estar presentes na base final.

**Colunas obrigatórias:**
- `ano`, `mes`, `uf`, `sexo`, `faixa_etaria`, `cid10`
- `internacoes`, `obitos_sim`, `populacao`
- `taxa_internacao_100k`, `taxa_mortalidade_100k`

**Severidade:** CRÍTICA

---

## 2. Validação de CID-10

**Regra:** Todos os registros devem ter CID-10 restrito a E10, E11, E12, E13 ou E14.

**CIDs aceitos:**
- E10 - Diabetes mellitus insulinodependente
- E11 - Diabetes mellitus não insulinodependente
- E12 - Diabetes mellitus relacionado com desnutrição
- E13 - Outros tipos especificados de diabetes mellitus
- E14 - Diabetes mellitus não especificado

**Severidade:** CRÍTICA

---

## 3. Valores Numéricos

**Regra:** Colunas numéricas não devem conter valores negativos indevidos.

**Colunas verificadas:**
- `internacoes`, `valor_total`, `dias_permanencia`
- `obitos_hospitalares`, `obitos_sim`, `populacao`
- `taxa_internacao_100k`, `taxa_mortalidade_100k`

**Severidade:** CRÍTICA

---

## 4. População

**Regra:** A população deve ser maior que zero para cálculo de taxas.

**Severidade:** CRÍTICA

---

## 5. Range de Anos

**Regra:** Os anos devem estar dentro do período configurado (padrão: 2019-2023).

**Severidade:** ALERTA

---

## 6. UFs Válidas

**Regra:** As UFs devem ser siglas válidas das 27 Unidades da Federação.

**UFs válidas:** AC, AL, AM, AP, BA, CE, DF, ES, GO, MA, MG, MS, MT, PA, PB, PE, PI, PR, RJ, RN, RO, RR, RS, SC, SE, SP, TO

**Severidade:** CRÍTICA

---

## 7. Sexo Válido

**Regra:** Os valores de sexo devem ser "Masculino", "Feminino" ou "Ignorado".

**Severidade:** ALERTA

---

## 8. Duplicidades

**Regra:** Não deve haver registros duplicados na combinação de:
- ano, mês, UF, município, sexo, faixa etária e CID-10

**Severidade:** CRÍTICA

---

## 9. Identificadores Individuais

**Regra:** A base final não deve conter identificadores individuais de pacientes.

**Colunas proibidas:** nome, cpf, cns, cartao_sus, telefone, endereco, nome_paciente, nome_mae

**Severidade:** CRÍTICA

---

## 10. Coerência das Taxas

**Regra:** As taxas calculadas devem estar em ranges coerentes:
- Taxa de mortalidade hospitalar: 0% a 100%
- Taxa de internação: até 10.000 por 100k
- Taxa de mortalidade: até 5.000 por 100k

**Severidade:** ALERTA

---

## 11. Consistência Referencial

**Regra:** Óbitos hospitalares não devem exceder o número de internações.

**Severidade:** ALERTA

---

## 12. Distribuição Temporal

**Regra:** Verifica a distribuição dos registros por ano para identificar possíveis lacunas.

**Severidade:** INFORMATIVA

---

## Processamento de Erros

| Severidade | Ação |
|------------|------|
| CRÍTICA | O pipeline gera alerta e pode falhar |
| ALERTA | O pipeline continua com registro do problema |
| INFORMATIVA | Apenas log para referência |
