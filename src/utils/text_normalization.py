"""Normalização de texto e nomes de colunas. Autora: Nathalia Adriele"""

import re
import unicodedata


def normalize_column_name(name: str) -> str:
    """Normaliza nome de coluna: minúsculas, sem acentos, underscore."""
    if not isinstance(name, str):
        return str(name)

    name = name.strip()
    name = remove_accents(name)
    name = name.lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")

    return name


def remove_accents(text: str) -> str:
    """Remove acentos de uma string."""
    if not isinstance(text, str):
        return str(text)

    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_uf(uf: str) -> str:
    """Normaliza sigla da UF para maiúsculas sem acentos."""
    if not isinstance(uf, str):
        return ""

    uf = remove_accents(uf).strip().upper()

    if len(uf) == 2:
        return uf

    from src.config.settings import UF_NOME

    nome_to_sigla = {remove_accents(v).upper(): k for k, v in UF_NOME.items()}
    return nome_to_sigla.get(uf, uf)


def normalize_whitespace(text: str) -> str:
    """Remove espaços extras e normaliza whitespace."""
    if not isinstance(text, str):
        return str(text)
    return re.sub(r"\s+", " ", text).strip()


def clean_numeric_string(value) -> str:
    """Limpa string numérica removendo caracteres não numéricos."""
    if value is None:
        return ""
    s = str(value).strip()
    s = re.sub(r"[^\d.,\-]", "", s)
    s = s.replace(",", ".")
    parts = s.split(".")
    if len(parts) > 2:
        s = "".join(parts[:-1]) + "." + parts[-1]
    return s
