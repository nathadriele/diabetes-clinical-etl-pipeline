"""
Testes unitários do módulo de transformação SIH.

Autora: Nathalia Adriele
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.transform_sih import (
    transform_sih,
    _padronizar_colunas,
    _mapear_colunas_sih,
    _converter_tipos,
    _filtrar_cid_diabetes,
    _padronizar_sexo,
    _criar_faixa_etaria,
    _criar_tipo_diabetes,
    _remover_duplicidades,
)


@pytest.fixture
def df_sih_bruto():
    return pd.DataFrame({
        "ANO_CMPT": ["2020", "2021", "2022"],
        "MES_CMPT": ["1", "2", "3"],
        "UF_ZI": ["SP", "RJ", "MG"],
        "MUNIC_RES": ["355030", "330455", "310620"],
        "SEXO": ["M", "F", "M"],
        "IDADE": ["55", "65", "45"],
        "DIAG_PRINC": ["E10", "E11", "E14"],
        "DIAG_SECUN": ["", "", ""],
        "N_AIH": ["AIH001", "AIH002", "AIH003"],
        "VAL_TOTAL": ["1500.50", "2300.75", "980.30"],
        "VAL_SERV_HOSP": ["1050.35", "1610.53", "686.21"],
        "VAL_SERV_PROF": ["450.15", "690.22", "294.09"],
        "DIAS_PERM": ["7", "10", "4"],
        "MORTE": ["0", "1", "0"],
        "DT_INTER": ["20200101", "20210201", "20220301"],
        "DT_SAIDA": ["20200108", "20210211", "20220305"],
    })


@pytest.fixture
def df_sih_com_cid_invalido():
    return pd.DataFrame({
        "ANO_CMPT": ["2020"],
        "MES_CMPT": ["1"],
        "UF_ZI": ["SP"],
        "MUNIC_RES": ["355030"],
        "SEXO": ["M"],
        "IDADE": ["55"],
        "DIAG_PRINC": ["A01"],
        "N_AIH": ["AIH004"],
        "VAL_TOTAL": ["1000.00"],
        "DIAS_PERM": ["5"],
        "MORTE": ["0"],
    })


class TestPadronizarColunas:
    """Testes de padronização de colunas."""

    def test_normalize_column_names(self, df_sih_bruto):
        df = _padronizar_colunas(df_sih_bruto.copy())
        assert "ano_cmpt" in df.columns
        assert "mes_cmpt" in df.columns
        assert "diag_princ" in df.columns

    def test_colunas_sem_espacos(self):
        df = pd.DataFrame({" Nome Coluna ": [1], "Outra Coluna": [2]})
        df = _padronizar_colunas(df)
        assert "nome_coluna" in df.columns
        assert "outra_coluna" in df.columns


class TestMapearColunas:
    """Testes de mapeamento de colunas SIH."""

    def test_mapeamento_basico(self, df_sih_bruto):
        df = _padronizar_colunas(df_sih_bruto.copy())
        df = _mapear_colunas_sih(df)
        assert "ano" in df.columns
        assert "mes" in df.columns
        assert "uf" in df.columns
        assert "cid10" in df.columns


class TestConverterTipos:
    """Testes de conversão de tipos."""

    def test_conversao_numerica(self, df_sih_bruto):
        df = _padronizar_colunas(df_sih_bruto.copy())
        df = _mapear_colunas_sih(df)
        df = _converter_tipos(df)
        assert pd.api.types.is_numeric_dtype(df["ano"])
        assert pd.api.types.is_numeric_dtype(df["valor_total"])


class TestFiltrarCID:
    """Testes de filtro de CID-10."""

    def test_filtra_apenas_diabetes(self, df_sih_bruto):
        df = _padronizar_colunas(df_sih_bruto.copy())
        df = _mapear_colunas_sih(df)
        df = _converter_tipos(df)
        df = _filtrar_cid_diabetes(df)
        assert len(df) == 3
        assert all(df["cid10"].str.startswith(("E10", "E11", "E12", "E13", "E14")))

    def test_remove_cid_invalido(self, df_sih_com_cid_invalido):
        df = _padronizar_colunas(df_sih_com_cid_invalido.copy())
        df = _mapear_colunas_sih(df)
        df = _converter_tipos(df)
        df = _filtrar_cid_diabetes(df)
        assert len(df) == 0


class TestPadronizarSexo:
    """Testes de padronização de sexo."""

    def test_sexo_masc_fem(self):
        df = pd.DataFrame({"sexo": ["M", "F", "1", "2"]})
        df = _padronizar_sexo(df)
        assert df["sexo"].iloc[0] == "Masculino"
        assert df["sexo"].iloc[1] == "Feminino"
        assert df["sexo"].iloc[2] == "Masculino"
        assert df["sexo"].iloc[3] == "Feminino"


class TestCriarFaixaEtaria:
    """Testes de criação de faixa etária."""

    def test_faixa_etaria_correta(self):
        df = pd.DataFrame({"idade": [5, 15, 35, 55, 75, 85]})
        df = _criar_faixa_etaria(df)
        assert df["faixa_etaria"].iloc[0] == "5-9 anos"
        assert df["faixa_etaria"].iloc[1] == "15-19 anos"
        assert df["faixa_etaria"].iloc[2] == "30-39 anos"
        assert df["faixa_etaria"].iloc[3] == "50-59 anos"
        assert df["faixa_etaria"].iloc[4] == "70-79 anos"
        assert df["faixa_etaria"].iloc[5] == "80+ anos"

    def test_idade_none_retorna_ignorado(self):
        df = pd.DataFrame({"idade": [None]})
        df = _criar_faixa_etaria(df)
        assert df["faixa_etaria"].iloc[0] == "Ignorado"


class TestCriarTipoDiabetes:
    """Testes de classificação do tipo de diabetes."""

    def test_classificacao_e10(self):
        df = pd.DataFrame({"cid10": ["E10"]})
        df = _criar_tipo_diabetes(df)
        assert df["tipo_diabetes"].iloc[0] == "Insulinodependente (Tipo 1)"

    def test_classificacao_e11(self):
        df = pd.DataFrame({"cid10": ["E11"]})
        df = _criar_tipo_diabetes(df)
        assert df["tipo_diabetes"].iloc[0] == "Não insulinodependente (Tipo 2)"

    def test_classificacao_e14(self):
        df = pd.DataFrame({"cid10": ["E14"]})
        df = _criar_tipo_diabetes(df)
        assert df["tipo_diabetes"].iloc[0] == "Não especificado"


class TestRemoverDuplicidades:
    """Testes de remoção de duplicidades."""

    def test_remove_duplicatas(self):
        df = pd.DataFrame({
            "ano": [2020, 2020],
            "mes": [1, 1],
            "uf": ["SP", "SP"],
            "cid10": ["E11", "E11"],
        })
        df = _remover_duplicidades(df)
        assert len(df) == 1


class TestTransformSihIntegration:
    """Teste de integração da transformação SIH completa."""

    def test_transform_sih_completo(self, df_sih_bruto, tmp_path):
        from src.config import settings
        original = settings.SIH_INTERIM_FILE
        settings.SIH_INTERIM_FILE = tmp_path / "sih_interim.csv"

        result = transform_sih(df_sih_bruto)

        assert isinstance(result, pd.DataFrame)
        assert "cid10" in result.columns
        assert "tipo_diabetes" in result.columns
        assert all(result["cid10"].str.startswith(("E10", "E11", "E14")))

        settings.SIH_INTERIM_FILE = original
