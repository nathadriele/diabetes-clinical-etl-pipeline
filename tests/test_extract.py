"""
Testes unitários do módulo de extração de dados.

Autora: Nathalia Adriele
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data.extract import extract_sih, extract_sim, extract_population, extract_all


class TestExtract:
    """Testes unitários para as funções de extração."""

    def test_extract_sih_file_not_found(self, tmp_path):
        import src.data.extract as mod
        import src.config.settings as settings
        orig_mod = mod._settings.SIH_RAW_FILE
        orig_settings = settings.SIH_RAW_FILE
        nonexistent = tmp_path / "nonexistent.csv"
        mod._settings.SIH_RAW_FILE = nonexistent
        settings.SIH_RAW_FILE = nonexistent
        try:
            with pytest.raises(FileNotFoundError):
                extract_sih()
        finally:
            mod._settings.SIH_RAW_FILE = orig_mod
            settings.SIH_RAW_FILE = orig_settings

    def test_extract_sim_file_not_found(self, tmp_path):
        import src.data.extract as mod
        import src.config.settings as settings
        orig_mod = mod._settings.SIM_RAW_FILE
        orig_settings = settings.SIM_RAW_FILE
        nonexistent = tmp_path / "nonexistent.csv"
        mod._settings.SIM_RAW_FILE = nonexistent
        settings.SIM_RAW_FILE = nonexistent
        try:
            with pytest.raises(FileNotFoundError):
                extract_sim()
        finally:
            mod._settings.SIM_RAW_FILE = orig_mod
            settings.SIM_RAW_FILE = orig_settings

    def test_extract_population_file_not_found(self, tmp_path):
        import src.data.extract as mod
        import src.config.settings as settings
        orig_mod = mod._settings.POPULATION_RAW_FILE
        orig_settings = settings.POPULATION_RAW_FILE
        nonexistent = tmp_path / "nonexistent.csv"
        mod._settings.POPULATION_RAW_FILE = nonexistent
        settings.POPULATION_RAW_FILE = nonexistent
        try:
            with pytest.raises(FileNotFoundError):
                extract_population()
        finally:
            mod._settings.POPULATION_RAW_FILE = orig_mod
            settings.POPULATION_RAW_FILE = orig_settings

    def test_extract_sih_returns_dataframe(self, tmp_path):
        import src.data.extract as mod
        import src.config.settings as settings
        orig_mod = mod._settings.SIH_RAW_FILE
        orig_settings = settings.SIH_RAW_FILE
        test_file = tmp_path / "sih_test.csv"
        mod._settings.SIH_RAW_FILE = test_file
        settings.SIH_RAW_FILE = test_file
        df_mock = pd.DataFrame({"ANO_CMPT": [2020], "MES_CMPT": [1]})
        df_mock.to_csv(test_file, index=False)
        try:
            result = extract_sih()
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
        finally:
            mod._settings.SIH_RAW_FILE = orig_mod
            settings.SIH_RAW_FILE = orig_settings

    def test_extract_sim_returns_dataframe(self, tmp_path):
        import src.data.extract as mod
        import src.config.settings as settings
        orig_mod = mod._settings.SIM_RAW_FILE
        orig_settings = settings.SIM_RAW_FILE
        test_file = tmp_path / "sim_test.csv"
        mod._settings.SIM_RAW_FILE = test_file
        settings.SIM_RAW_FILE = test_file
        df_mock = pd.DataFrame({"ANO_OBITO": [2020], "CAUSA_BASICA": ["E11"]})
        df_mock.to_csv(test_file, index=False)
        try:
            result = extract_sim()
            assert isinstance(result, pd.DataFrame)
        finally:
            mod._settings.SIM_RAW_FILE = orig_mod
            settings.SIM_RAW_FILE = orig_settings

    def test_extract_population_returns_dataframe(self, tmp_path):
        import src.data.extract as mod
        import src.config.settings as settings
        orig_mod = mod._settings.POPULATION_RAW_FILE
        orig_settings = settings.POPULATION_RAW_FILE
        test_file = tmp_path / "pop_test.csv"
        mod._settings.POPULATION_RAW_FILE = test_file
        settings.POPULATION_RAW_FILE = test_file
        df_mock = pd.DataFrame({"ANO": [2020], "UF": ["SP"], "POPULACAO": [100000]})
        df_mock.to_csv(test_file, index=False)
        try:
            result = extract_population()
            assert isinstance(result, pd.DataFrame)
        finally:
            mod._settings.POPULATION_RAW_FILE = orig_mod
            settings.POPULATION_RAW_FILE = orig_settings

    def test_extract_all_returns_dict(self, tmp_path):
        import src.data.extract as mod
        import src.config.settings as settings
        orig_sih_mod = mod._settings.SIH_RAW_FILE
        orig_sim_mod = mod._settings.SIM_RAW_FILE
        orig_pop_mod = mod._settings.POPULATION_RAW_FILE
        orig_sih = settings.SIH_RAW_FILE
        orig_sim = settings.SIM_RAW_FILE
        orig_pop = settings.POPULATION_RAW_FILE

        sih_file = tmp_path / "sih_test.csv"
        sim_file = tmp_path / "sim_test.csv"
        pop_file = tmp_path / "pop_test.csv"

        mod._settings.SIH_RAW_FILE = sih_file
        mod._settings.SIM_RAW_FILE = sim_file
        mod._settings.POPULATION_RAW_FILE = pop_file
        settings.SIH_RAW_FILE = sih_file
        settings.SIM_RAW_FILE = sim_file
        settings.POPULATION_RAW_FILE = pop_file

        pd.DataFrame({"ANO_CMPT": [2020]}).to_csv(sih_file, index=False)
        pd.DataFrame({"ANO_OBITO": [2020]}).to_csv(sim_file, index=False)
        pd.DataFrame({"ANO": [2020]}).to_csv(pop_file, index=False)

        try:
            result = extract_all()
            assert isinstance(result, dict)
            assert "sih" in result
            assert "sim" in result
            assert "population" in result
        finally:
            mod._settings.SIH_RAW_FILE = orig_sih_mod
            mod._settings.SIM_RAW_FILE = orig_sim_mod
            mod._settings.POPULATION_RAW_FILE = orig_pop_mod
            settings.SIH_RAW_FILE = orig_sih
            settings.SIM_RAW_FILE = orig_sim
            settings.POPULATION_RAW_FILE = orig_pop
