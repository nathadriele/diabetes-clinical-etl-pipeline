"""
Testes unitários do módulo de validação.

Autora: Nathalia Adriele
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data.validate import validate_data


@pytest.fixture
def df_valido():
    return pd.DataFrame({
        "ano": [2020, 2021, 2022],
        "mes": [1, 2, 3],
        "uf": ["SP", "RJ", "MG"],
        "codigo_municipio": ["355030", "330455", "310620"],
        "sexo": ["Masculino", "Feminino", "Masculino"],
        "faixa_etaria": ["50-59 anos", "60-69 anos", "40-49 anos"],
        "cid10": ["E10", "E11", "E14"],
        "internacoes": [100, 80, 90],
        "valor_total": [15000.0, 12000.0, 13500.0],
        "dias_permanencia": [700, 640, 720],
        "obitos_hospitalares": [3, 2, 1],
        "obitos_sim": [50, 40, 35],
        "populacao": [12000000, 6000000, 5800000],
        "taxa_internacao_100k": [0.83, 1.33, 1.55],
        "taxa_mortalidade_100k": [0.42, 0.67, 0.60],
        "taxa_mortalidade_hospitalar": [3.0, 2.5, 1.11],
    })


@pytest.fixture
def df_com_problemas():
    return pd.DataFrame({
        "ano": [2010, 2030, 2021],
        "mes": [1, 2, 3],
        "uf": ["SP", "XX", "MG"],
        "cid10": ["A01", "E11", "E14"],
        "sexo": ["Masculino", "Feminino", "Masculino"],
        "internacoes": [-5, 80, 90],
        "obitos_sim": [50, 40, 35],
        "populacao": [0, -100, 5800000],
        "obitos_hospitalares": [3, 2, 1],
        "taxa_internacao_100k": [0.0, 0.0, 1.55],
        "taxa_mortalidade_100k": [0.0, 0.0, 0.60],
        "taxa_mortalidade_hospitalar": [3.0, 2.5, 1.11],
    })


class TestValidate:
    """Testes de validação dos dados."""

    def test_validate_data_retorna_dict(self, df_valido, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        result = validate_data(df_valido)
        assert isinstance(result, dict)

        settings.VALIDATION_REPORT = original

    def test_validacao_colunas_passa(self, df_valido, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        result = validate_data(df_valido)
        assert result["colunas_obrigatorias"]["status"] == "PASS"

        settings.VALIDATION_REPORT = original

    def test_validacao_cid10_passa(self, df_valido, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        result = validate_data(df_valido)
        assert result["cid10_validos"]["status"] == "PASS"

        settings.VALIDATION_REPORT = original

    def test_validacao_cid10_falha(self, df_com_problemas, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        result = validate_data(df_com_problemas)
        assert result["cid10_validos"]["status"] == "FAIL"

        settings.VALIDATION_REPORT = original

    def test_validacao_anos_passa(self, df_valido, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        result = validate_data(df_valido)
        assert result["anos"]["status"] == "PASS"

        settings.VALIDATION_REPORT = original

    def test_validacao_anos_falha(self, df_com_problemas, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        result = validate_data(df_com_problemas)
        assert result["anos"]["status"] == "FAIL"

        settings.VALIDATION_REPORT = original

    def test_validacao_identificadores_passa(self, df_valido, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        result = validate_data(df_valido)
        assert result["identificadores"]["status"] == "PASS"

        settings.VALIDATION_REPORT = original

    def test_validacao_identificadores_falha(self, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        df = pd.DataFrame({
            "ano": [2020], "uf": ["SP"], "cid10": ["E11"],
            "nome": ["João da Silva"],
            "internacoes": [10], "obitos_sim": [5], "populacao": [100000],
        })
        result = validate_data(df)
        assert result["identificadores"]["status"] == "FAIL"

        settings.VALIDATION_REPORT = original

    def test_validacao_duplicidades(self, tmp_path):
        from src.config import settings
        original = settings.VALIDATION_REPORT
        settings.VALIDATION_REPORT = tmp_path / "validation.csv"

        df = pd.DataFrame({
            "ano": [2020, 2020],
            "mes": [1, 1],
            "uf": ["SP", "SP"],
            "codigo_municipio": ["355030", "355030"],
            "sexo": ["M", "M"],
            "faixa_etaria": ["50-59", "50-59"],
            "cid10": ["E11", "E11"],
            "internacoes": [10, 10],
            "obitos_sim": [5, 5],
            "populacao": [100000, 100000],
        })
        result = validate_data(df)
        assert result["duplicidades"]["status"] == "FAIL"

        settings.VALIDATION_REPORT = original
