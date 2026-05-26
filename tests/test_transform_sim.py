"""
Testes unitários do módulo de transformação SIM.

Autora: Nathalia Adriele
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data.transform_sim import (
    transform_sim,
    _filtrar_cid_diabetes,
    _padronizar_sexo,
    _criar_tipo_diabetes,
    _criar_faixa_etaria,
)


@pytest.fixture
def df_sim_bruto():
    return pd.DataFrame({
        "ANO_OBITO": ["2020", "2021", "2022", "2020"],
        "MES_OBITO": ["3", "6", "9", "1"],
        "UF_RESID": ["SP", "RJ", "MG", "BA"],
        "MUNIC_RES": ["355030", "330455", "310620", "292740"],
        "SEXO": ["M", "F", "M", "F"],
        "IDADE": ["60", "70", "50", "40"],
        "CAUSA_BASICA": ["E11", "E14", "E10", "E13"],
        "LINHAA": ["E11", "E14", "E10", "E13"],
        "NUMERODO": ["DO001", "DO002", "DO003", "DO004"],
    })


@pytest.fixture
def df_sim_cid_invalido():
    return pd.DataFrame({
        "ANO_OBITO": ["2020"],
        "MES_OBITO": ["1"],
        "UF_RESID": ["SP"],
        "MUNIC_RES": ["355030"],
        "SEXO": ["M"],
        "IDADE": ["60"],
        "CAUSA_BASICA": ["I10"],
        "NUMERODO": ["DO005"],
    })


class TestTransformSIM:
    """Testes da transformação SIM."""

    def test_transform_sim_retorna_dataframe(self, df_sim_bruto, tmp_path):
        from src.config import settings
        original = settings.SIM_INTERIM_FILE
        settings.SIM_INTERIM_FILE = tmp_path / "sim_interim.csv"

        result = transform_sim(df_sim_bruto)
        assert isinstance(result, pd.DataFrame)

        settings.SIM_INTERIM_FILE = original

    def test_filtro_cid_diabetes_sim(self, df_sim_bruto):
        from src.data.transform_sim import _padronizar_colunas, _mapear_colunas_sim, _converter_tipos

        df = _padronizar_colunas(df_sim_bruto.copy())
        df = _mapear_colunas_sim(df)
        df = _converter_tipos(df)
        df = _filtrar_cid_diabetes(df)

        assert len(df) == 4
        assert all(df["cid10"].str.startswith(("E10", "E11", "E12", "E13", "E14")))

    def test_remove_cid_invalido_sim(self, df_sim_cid_invalido):
        from src.data.transform_sim import _padronizar_colunas, _mapear_colunas_sim, _converter_tipos

        df = _padronizar_colunas(df_sim_cid_invalido.copy())
        df = _mapear_colunas_sim(df)
        df = _converter_tipos(df)
        df = _filtrar_cid_diabetes(df)

        assert len(df) == 0

    def test_tipo_diabetes_sim(self):
        df = pd.DataFrame({"cid10": ["E10", "E11", "E12", "E13", "E14"]})
        df = _criar_tipo_diabetes(df)

        assert df["tipo_diabetes"].iloc[0] == "Insulinodependente (Tipo 1)"
        assert df["tipo_diabetes"].iloc[1] == "Não insulinodependente (Tipo 2)"
        assert df["tipo_diabetes"].iloc[2] == "Relacionado com desnutrição"
        assert df["tipo_diabetes"].iloc[3] == "Outros tipos especificados"
        assert df["tipo_diabetes"].iloc[4] == "Não especificado"

    def test_sexo_padronizado_sim(self):
        df = pd.DataFrame({"sexo": ["1", "2", "M", "F"]})
        df = _padronizar_sexo(df)
        assert "Masculino" in df["sexo"].values
        assert "Feminino" in df["sexo"].values

    def test_agrupamento_sim(self, df_sim_bruto, tmp_path):
        from src.config import settings
        original = settings.SIM_INTERIM_FILE
        settings.SIM_INTERIM_FILE = tmp_path / "sim_interim.csv"

        result = transform_sim(df_sim_bruto)
        assert "obitos_sim" in result.columns
        assert result["obitos_sim"].sum() > 0

        settings.SIM_INTERIM_FILE = original
