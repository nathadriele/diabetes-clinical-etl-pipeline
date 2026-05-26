"""
Testes unitários do módulo de integração.

Autora: Nathalia Adriele
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.integrate import integrate_data, _classificar_diabetes, _calcular_indicadores


@pytest.fixture
def df_sih_transformado():
    return pd.DataFrame({
        "ano": [2020, 2020, 2021, 2021],
        "mes": [1, 2, 1, 2],
        "regiao": ["Sudeste", "Sudeste", "Sudeste", "Sudeste"],
        "uf": ["SP", "RJ", "SP", "MG"],
        "municipio": ["São Paulo", "Rio de Janeiro", "São Paulo", "Belo Horizonte"],
        "codigo_municipio": ["355030", "330455", "355030", "310620"],
        "sexo": ["Masculino", "Feminino", "Masculino", "Feminino"],
        "faixa_etaria": ["50-59 anos", "60-69 anos", "50-59 anos", "60-69 anos"],
        "cid10": ["E11", "E14", "E10", "E11"],
        "tipo_diabetes": [
            "Não insulinodependente (Tipo 2)",
            "Não especificado",
            "Insulinodependente (Tipo 1)",
            "Não insulinodependente (Tipo 2)",
        ],
        "descricao_cid10": [
            "Diabetes mellitus não insulinodependente",
            "Diabetes mellitus não especificado",
            "Diabetes mellitus insulinodependente",
            "Diabetes mellitus não insulinodependente",
        ],
        "internacoes": [100, 80, 120, 90],
        "valor_total": [150000.00, 120000.00, 180000.00, 135000.00],
        "valor_medio_internacao": [1500.00, 1500.00, 1500.00, 1500.00],
        "dias_permanencia": [700, 640, 840, 720],
        "media_permanencia": [7.0, 8.0, 7.0, 8.0],
        "obitos_hospitalares": [3, 2, 4, 2],
        "taxa_mortalidade_hospitalar": [3.0, 2.5, 3.33, 2.22],
    })


@pytest.fixture
def df_sim_transformado():
    return pd.DataFrame({
        "ano": [2020, 2020, 2021, 2021],
        "mes": [1, 2, 1, 2],
        "regiao": ["Sudeste", "Sudeste", "Sudeste", "Sudeste"],
        "uf": ["SP", "RJ", "SP", "MG"],
        "municipio": ["São Paulo", "Rio de Janeiro", "São Paulo", "Belo Horizonte"],
        "codigo_municipio": ["355030", "330455", "355030", "310620"],
        "sexo": ["Masculino", "Feminino", "Masculino", "Feminino"],
        "faixa_etaria": ["50-59 anos", "60-69 anos", "50-59 anos", "60-69 anos"],
        "cid10": ["E11", "E14", "E10", "E11"],
        "tipo_diabetes": [
            "Não insulinodependente (Tipo 2)",
            "Não especificado",
            "Insulinodependente (Tipo 1)",
            "Não insulinodependente (Tipo 2)",
        ],
        "descricao_cid10": [
            "Diabetes mellitus não insulinodependente",
            "Diabetes mellitus não especificado",
            "Diabetes mellitus insulinodependente",
            "Diabetes mellitus não insulinodependente",
        ],
        "obitos_sim": [50, 40, 60, 35],
    })


@pytest.fixture
def df_pop_transformado():
    return pd.DataFrame({
        "ano": [2020, 2020, 2021, 2021],
        "regiao": ["Sudeste", "Sudeste", "Sudeste", "Sudeste"],
        "uf": ["SP", "RJ", "SP", "MG"],
        "municipio": ["São Paulo", "Rio de Janeiro", "São Paulo", "Belo Horizonte"],
        "codigo_municipio": ["355030", "330455", "355030", "310620"],
        "populacao": [12000000, 6000000, 12200000, 5800000],
    })


class TestIntegrate:
    """Testes da integração de dados."""

    def test_integrate_retorna_dataframe(
        self, df_sih_transformado, df_sim_transformado, df_pop_transformado
    ):
        result = integrate_data(df_sih_transformado, df_sim_transformado, df_pop_transformado)
        assert isinstance(result, pd.DataFrame)

    def test_integrate_tem_colunas_obrigatorias(
        self, df_sih_transformado, df_sim_transformado, df_pop_transformado
    ):
        result = integrate_data(df_sih_transformado, df_sim_transformado, df_pop_transformado)

        colunas_obrigatorias = [
            "ano", "uf", "cid10", "internacoes", "obitos_sim",
            "populacao", "taxa_internacao_100k", "taxa_mortalidade_100k",
        ]
        for col in colunas_obrigatorias:
            assert col in result.columns, f"Coluna '{col}' ausente"

    def test_integrate_tem_populacao(
        self, df_sih_transformado, df_sim_transformado, df_pop_transformado
    ):
        result = integrate_data(df_sih_transformado, df_sim_transformado, df_pop_transformado)
        assert "populacao" in result.columns
        assert result["populacao"].sum() > 0

    def test_integrate_tem_taxas(
        self, df_sih_transformado, df_sim_transformado, df_pop_transformado
    ):
        result = integrate_data(df_sih_transformado, df_sim_transformado, df_pop_transformado)
        assert "taxa_internacao_100k" in result.columns
        assert "taxa_mortalidade_100k" in result.columns

    def test_taxa_internacao_100k_positiva(
        self, df_sih_transformado, df_sim_transformado, df_pop_transformado
    ):
        result = integrate_data(df_sih_transformado, df_sim_transformado, df_pop_transformado)
        assert all(result["taxa_internacao_100k"] >= 0)

    def test_taxa_mortalidade_100k_positiva(
        self, df_sih_transformado, df_sim_transformado, df_pop_transformado
    ):
        result = integrate_data(df_sih_transformado, df_sim_transformado, df_pop_transformado)
        assert all(result["taxa_mortalidade_100k"] >= 0)


class TestClassificarDiabetes:
    """Testes da classificação de diabetes."""

    def test_e10(self):
        assert _classificar_diabetes("E10") == "Insulinodependente (Tipo 1)"

    def test_e11(self):
        assert _classificar_diabetes("E11") == "Não insulinodependente (Tipo 2)"

    def test_e12(self):
        assert _classificar_diabetes("E12") == "Relacionado com desnutrição"

    def test_e13(self):
        assert _classificar_diabetes("E13") == "Outros tipos especificados"

    def test_e14(self):
        assert _classificar_diabetes("E14") == "Não especificado"


class TestCalcularIndicadores:
    """Testes do cálculo de indicadores."""

    def test_taxa_internacao_100k(self):
        df = pd.DataFrame({
            "internacoes": [100],
            "obitos_sim": [20],
            "populacao": [100000],
            "obitos_hospitalares": [5],
        })
        result = _calcular_indicadores(df)
        assert result["taxa_internacao_100k"].iloc[0] == 100.0

    def test_taxa_mortalidade_100k(self):
        df = pd.DataFrame({
            "internacoes": [100],
            "obitos_sim": [20],
            "populacao": [100000],
            "obitos_hospitalares": [5],
        })
        result = _calcular_indicadores(df)
        assert result["taxa_mortalidade_100k"].iloc[0] == 20.0

    def test_taxa_mortalidade_hospitalar(self):
        df = pd.DataFrame({
            "internacoes": [100],
            "obitos_hospitalares": [5],
            "obitos_sim": [20],
            "populacao": [100000],
        })
        result = _calcular_indicadores(df)
        assert result["taxa_mortalidade_hospitalar"].iloc[0] == 5.0

    def test_populacao_zero_retorna_zero(self):
        df = pd.DataFrame({
            "internacoes": [100],
            "obitos_sim": [20],
            "populacao": [0],
            "obitos_hospitalares": [5],
        })
        result = _calcular_indicadores(df)
        assert result["taxa_internacao_100k"].iloc[0] == 0.0
