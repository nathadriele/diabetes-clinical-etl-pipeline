"""
Testes de integração do pipeline ETL completo.

Autora: Nathalia Adriele
"""

import pytest
import pandas as pd
from pathlib import Path


def _criar_dados_teste(raw_dir):
    sih_data = []
    for ano in [2020, 2021]:
        for mes in [1, 6]:
            for uf in ["SP", "MG"]:
                for cid in ["E10", "E11"]:
                    for sexo in ["M", "F"]:
                        sih_data.append({
                            "ANO_CMPT": str(ano),
                            "MES_CMPT": str(mes),
                            "UF_ZI": uf,
                            "MUNIC_RES": "355030" if uf == "SP" else "310620",
                            "SEXO": sexo,
                            "IDADE": "55",
                            "DIAG_PRINC": cid,
                            "DIAG_SECUN": "",
                            "N_AIH": f"AIH{ano}{uf}{cid}{mes}{sexo}",
                            "VAL_TOTAL": "1500.00",
                            "VAL_SERV_HOSP": "1050.00",
                            "VAL_SERV_PROF": "450.00",
                            "DIAS_PERM": "7",
                            "MORTE": "0",
                            "DT_INTER": f"{ano}{mes:02d}01",
                            "DT_SAIDA": f"{ano}{mes:02d}08",
                        })

    pd.DataFrame(sih_data).to_csv(raw_dir / "sih_diabetes_raw.csv", index=False)

    sim_data = []
    for ano in [2020, 2021]:
        for uf in ["SP", "MG"]:
            for cid in ["E10", "E11"]:
                for sexo in ["M", "F"]:
                    sim_data.append({
                        "ANO_OBITO": str(ano),
                        "MES_OBITO": "3",
                        "UF_RESID": uf,
                        "MUNIC_RES": "355030" if uf == "SP" else "310620",
                        "SEXO": sexo,
                        "IDADE": "60",
                        "CAUSA_BASICA": cid,
                        "LINHAA": cid,
                        "NUMERODO": f"DO{ano}{uf}{cid}{sexo}",
                    })

    pd.DataFrame(sim_data).to_csv(raw_dir / "sim_diabetes_raw.csv", index=False)

    pop_data = [
        {"ANO": 2020, "UF": "SP", "MUNICIPIO": "São Paulo", "COD_MUNICIPIO": "355030", "POPULACAO": 12000000},
        {"ANO": 2020, "UF": "MG", "MUNICIPIO": "Belo Horizonte", "COD_MUNICIPIO": "310620", "POPULACAO": 5800000},
        {"ANO": 2021, "UF": "SP", "MUNICIPIO": "São Paulo", "COD_MUNICIPIO": "355030", "POPULACAO": 12200000},
        {"ANO": 2021, "UF": "MG", "MUNICIPIO": "Belo Horizonte", "COD_MUNICIPIO": "310620", "POPULACAO": 5900000},
    ]
    pd.DataFrame(pop_data).to_csv(raw_dir / "population_raw.csv", index=False)


def _setup_temp_dirs(tmp_path):
    import src.config.settings as settings
    import src.data.extract as extract_mod
    import src.data.transform_sih as sih_mod
    import src.data.transform_sim as sim_mod
    import src.data.transform_population as pop_mod
    import src.data.load as load_mod
    import src.data.validate as validate_mod
    import src.data.pipeline as pipeline_mod
    import src.quality.quality_report as qr_mod

    raw = tmp_path / "raw"
    interim = tmp_path / "interim"
    processed = tmp_path / "processed"
    reports = tmp_path / "reports"

    for d in [raw, interim, processed, reports]:
        d.mkdir(parents=True, exist_ok=True)

    _criar_dados_teste(raw)

    patches = {}

    new_paths = {
        'SIH_RAW_FILE': raw / "sih_diabetes_raw.csv",
        'SIM_RAW_FILE': raw / "sim_diabetes_raw.csv",
        'POPULATION_RAW_FILE': raw / "population_raw.csv",
        'SIH_INTERIM_FILE': interim / "sih_interim.csv",
        'SIM_INTERIM_FILE': interim / "sim_interim.csv",
        'POPULATION_INTERIM_FILE': interim / "pop_interim.csv",
        'PROCESSED_CSV': processed / "processed.csv",
        'PROCESSED_PARQUET': processed / "processed.parquet",
        'PROCESSED_XLSX': processed / "processed.xlsx",
        'PROCESSED_DIR': processed,
        'INTERIM_DIR': interim,
        'RAW_DIR': raw,
        'DATA_DIR': tmp_path / "data",
        'REPORTS_DIR': reports,
        'VALIDATION_REPORT': reports / "validation.csv",
        'DATA_QUALITY_REPORT': reports / "quality.csv",
        'MISSING_VALUES_REPORT': reports / "missing.csv",
        'PIPELINE_EXECUTION_REPORT': reports / "execution.md",
    }

    modules_to_patch = [
        settings, extract_mod, sih_mod, sim_mod,
        pop_mod, load_mod, validate_mod, pipeline_mod, qr_mod,
    ]

    for module in modules_to_patch:
        patches[id(module)] = {}
        for attr, new_val in new_paths.items():
            if hasattr(module, attr):
                old_val = getattr(module, attr)
                patches[id(module)][attr] = old_val
                setattr(module, attr, new_val)

    return patches, modules_to_patch


def _restore_dirs(patches, modules_to_patch):
    for module in modules_to_patch:
        module_id = id(module)
        if module_id in patches:
            for attr, old_val in patches[module_id].items():
                setattr(module, attr, old_val)


class TestPipelineIntegration:
    """Testes de integração do pipeline ETL."""

    def test_pipeline_completo(self, tmp_path):
        from src.data.pipeline import run_pipeline
        patches, modules = _setup_temp_dirs(tmp_path)
        try:
            result = run_pipeline()
            assert isinstance(result, dict)
            assert result["extracao"]["status"] == "SUCESSO"
            assert result["transformacao_sih"]["status"] == "SUCESSO"
            assert result["transformacao_sim"]["status"] == "SUCESSO"
            assert result["transformacao_populacao"]["status"] == "SUCESSO"
            assert result["integracao"]["status"] == "SUCESSO"
            assert result["carga"]["status"] == "SUCESSO"
        finally:
            _restore_dirs(patches, modules)

    def test_arquivos_processados_gerados(self, tmp_path):
        from src.data.pipeline import run_pipeline
        import src.data.load as load_mod
        patches, modules = _setup_temp_dirs(tmp_path)
        try:
            run_pipeline()
            assert load_mod.PROCESSED_CSV.exists()
            assert load_mod.PROCESSED_PARQUET.exists()
            assert load_mod.PROCESSED_XLSX.exists()
        finally:
            _restore_dirs(patches, modules)

    def test_arquivos_interim_gerados(self, tmp_path):
        from src.data.pipeline import run_pipeline
        import src.data.transform_sih as sih_mod
        import src.data.transform_sim as sim_mod
        import src.data.transform_population as pop_mod
        patches, modules = _setup_temp_dirs(tmp_path)
        try:
            run_pipeline()
            assert sih_mod.SIH_INTERIM_FILE.exists()
            assert sim_mod.SIM_INTERIM_FILE.exists()
            assert pop_mod.POPULATION_INTERIM_FILE.exists()
        finally:
            _restore_dirs(patches, modules)

    def test_base_final_tem_colunas_esperadas(self, tmp_path):
        from src.data.pipeline import run_pipeline
        import src.data.load as load_mod
        patches, modules = _setup_temp_dirs(tmp_path)
        try:
            run_pipeline()
            df = pd.read_csv(load_mod.PROCESSED_CSV)
            colunas_esperadas = [
                "ano", "uf", "cid10", "internacoes",
                "obitos_sim", "populacao",
                "taxa_internacao_100k", "taxa_mortalidade_100k",
            ]
            for col in colunas_esperadas:
                assert col in df.columns, f"Coluna '{col}' ausente"
        finally:
            _restore_dirs(patches, modules)

    def test_base_final_cid10_validos(self, tmp_path):
        from src.data.pipeline import run_pipeline
        import src.data.load as load_mod
        patches, modules = _setup_temp_dirs(tmp_path)
        try:
            run_pipeline()
            df = pd.read_csv(load_mod.PROCESSED_CSV)
            cid10_validos = all(
                str(c).upper().startswith(("E10", "E11", "E12", "E13", "E14"))
                for c in df["cid10"].dropna().unique()
            )
            assert cid10_validos
        finally:
            _restore_dirs(patches, modules)

    def test_base_final_sem_valores_negativos(self, tmp_path):
        from src.data.pipeline import run_pipeline
        import src.data.load as load_mod
        patches, modules = _setup_temp_dirs(tmp_path)
        try:
            run_pipeline()
            df = pd.read_csv(load_mod.PROCESSED_CSV)
            for col in ["internacoes", "valor_total", "obitos_sim", "populacao"]:
                if col in df.columns:
                    assert all(df[col] >= 0), f"Valores negativos em {col}"
        finally:
            _restore_dirs(patches, modules)
