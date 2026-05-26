"""
Testes unitários do módulo de indicadores epidemiológicos.

Autora: Nathalia Adriele
"""

import pytest
import pandas as pd
import numpy as np

from src.indicators.epidemiological_indicators import calculate_indicators


@pytest.fixture
def df_base():
    return pd.DataFrame({
        "ano": [2020, 2020, 2021, 2021, 2022],
        "mes": [1, 2, 1, 2, 1],
        "regiao": ["Sudeste", "Sudeste", "Sudeste", "Sul", "Sudeste"],
        "uf": ["SP", "RJ", "SP", "PR", "MG"],
        "municipio": ["São Paulo", "Rio de Janeiro", "São Paulo", "Curitiba", "Belo Horizonte"],
        "codigo_municipio": ["355030", "330455", "355030", "410690", "310620"],
        "sexo": ["Masculino", "Feminino", "Masculino", "Feminino", "Masculino"],
        "faixa_etaria": ["50-59 anos", "60-69 anos", "50-59 anos", "60-69 anos", "40-49 anos"],
        "cid10": ["E11", "E14", "E10", "E11", "E11"],
        "tipo_diabetes": [
            "Não insulinodependente (Tipo 2)",
            "Não especificado",
            "Insulinodependente (Tipo 1)",
            "Não insulinodependente (Tipo 2)",
            "Não insulinodependente (Tipo 2)",
        ],
        "internacoes": [100, 80, 120, 90, 70],
        "valor_total": [150000.0, 120000.0, 180000.0, 135000.0, 105000.0],
        "dias_permanencia": [700, 640, 840, 720, 490],
        "obitos_hospitalares": [3, 2, 4, 2, 1],
        "obitos_sim": [50, 40, 60, 35, 25],
        "populacao": [12000000, 6000000, 12200000, 3500000, 5800000],
    })


class TestIndicators:
    """Testes dos indicadores epidemiológicos."""

    def test_calculate_indicators_retorna_dict(self, df_base):
        result = calculate_indicators(df_base)
        assert isinstance(result, dict)

    def test_indicadores_nacionais(self, df_base):
        result = calculate_indicators(df_base)
        nacionais = result["nacionais"]

        assert isinstance(nacionais, pd.DataFrame)
        assert len(nacionais) == 1
        assert nacionais["total_internacoes"].iloc[0] == 460
        assert nacionais["total_obitos_sim"].iloc[0] == 210

    def test_indicadores_por_ano(self, df_base):
        result = calculate_indicators(df_base)
        por_ano = result["por_ano"]

        assert isinstance(por_ano, pd.DataFrame)
        assert len(por_ano) == 3  # 2020, 2021, 2022
        assert 2020 in por_ano["ano"].values
        assert 2021 in por_ano["ano"].values

    def test_indicadores_por_uf(self, df_base):
        result = calculate_indicators(df_base)
        por_uf = result["por_uf"]

        assert isinstance(por_uf, pd.DataFrame)
        assert "SP" in por_uf["uf"].values
        assert "taxa_internacao_100k" in por_uf.columns

    def test_indicadores_por_regiao(self, df_base):
        result = calculate_indicators(df_base)
        por_regiao = result["por_regiao"]

        assert isinstance(por_regiao, pd.DataFrame)
        assert "Sudeste" in por_regiao["regiao"].values

    def test_indicadores_por_sexo(self, df_base):
        result = calculate_indicators(df_base)
        por_sexo = result["por_sexo"]

        assert isinstance(por_sexo, pd.DataFrame)
        assert "Masculino" in por_sexo["sexo"].values
        assert "Feminino" in por_sexo["sexo"].values

    def test_indicadores_por_faixa_etaria(self, df_base):
        result = calculate_indicators(df_base)
        por_faixa = result["por_faixa_etaria"]

        assert isinstance(por_faixa, pd.DataFrame)
        assert len(por_faixa) > 0

    def test_indicadores_por_cid10(self, df_base):
        result = calculate_indicators(df_base)
        por_cid = result["por_cid10"]

        assert isinstance(por_cid, pd.DataFrame)
        assert "E11" in por_cid["cid10"].values

    def test_taxa_internacao_100k(self, df_base):
        result = calculate_indicators(df_base)
        por_uf = result["por_uf"]

        assert all(por_uf["taxa_internacao_100k"] >= 0)

    def test_taxa_mortalidade_100k(self, df_base):
        result = calculate_indicators(df_base)
        por_uf = result["por_uf"]

        assert all(por_uf["taxa_mortalidade_100k"] >= 0)

    def test_valor_total_nacionais(self, df_base):
        result = calculate_indicators(df_base)
        nacionais = result["nacionais"]

        expected_total = df_base["valor_total"].sum()
        assert nacionais["valor_total_internacoes"].iloc[0] == expected_total
