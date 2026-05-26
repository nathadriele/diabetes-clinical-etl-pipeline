"""Dashboard interativo - Diabetes Mellitus no SUS. Autora: Nathalia Adriele"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config.settings import (
    PROCESSED_CSV,
    PROCESSED_PARQUET,
    DATA_QUALITY_REPORT,
    MISSING_VALUES_REPORT,
    VALIDATION_REPORT,
    FAIXAS_ETARIAS,
)

st.set_page_config(
    page_title="SUS Diabetes - Pipeline ETL",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

COR_VERDE_ESCURO = "#1A5632"
COR_VERDE_MEDIO = "#238636"
COR_VERDE_CLARO = "#2EA043"
COR_TEAL = "#1B7A6E"
COR_AZULESCO = "#1B6B93"
COR_LARANJA = "#C25E2A"
COR_BORDO = "#8B3A62"
COR_ROXO = "#6B4C9A"
COR_AMBAR = "#A67C2E"
COR_FUNDO_CARD = "#F4F6F5"
COR_TEXTO = "#2C3E50"
COR_TEXTO_EIXO = "#34495E"

PLOTLY_LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color=COR_TEXTO, family="sans-serif"),
    title=dict(font=dict(color=COR_VERDE_ESCURO, size=16)),
    legend=dict(font=dict(color=COR_TEXTO)),
    coloraxis_colorbar=dict(tickfont=dict(color=COR_TEXTO), title=dict(font=dict(color=COR_TEXTO))),
)

PLOTLY_AXES = dict(
    title=dict(font=dict(color=COR_TEXTO)),
    tickfont=dict(color=COR_TEXTO_EIXO),
    gridcolor="#E0E0E0",
)


def _style_fig(fig, showlegend=False, yaxis_order=None):
    layout_kw = dict(PLOTLY_LAYOUT, showlegend=showlegend)
    if yaxis_order:
        layout_kw["yaxis"] = {"categoryorder": yaxis_order}
    fig.update_layout(**layout_kw)
    fig.update_xaxes(**PLOTLY_AXES)
    fig.update_yaxes(**PLOTLY_AXES)
    return fig

st.markdown(f"""
<style>
    .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
    h1 {{ color: {COR_VERDE_ESCURO} !important; font-weight: 700 !important; }}
    h2, h3 {{ color: {COR_TEAL} !important; font-weight: 700 !important; }}
    .stMetric {{ background-color: {COR_FUNDO_CARD}; border-radius: 10px; padding: 1rem; border-left: 4px solid {COR_VERDE_MEDIO}; }}
    .stMetric label {{ color: {COR_VERDE_ESCURO} !important; font-weight: 600 !important; }}
    .stMetric [data-testid="stMetricValue"] {{ color: {COR_VERDE_ESCURO} !important; font-size: 1.5rem !important; font-weight: 700 !important; }}
    .badge-container {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 1.5rem; margin-bottom: 0.8rem; }}
    .badge-teste {{ background-color: {COR_LARANJA}; color: white; padding: 5px 16px; border-radius: 20px; font-weight: 700; font-size: 0.78rem; letter-spacing: 0.5px; white-space: nowrap; }}
    .badge-andamento {{ background-color: {COR_BORDO}; color: white; padding: 5px 16px; border-radius: 20px; font-weight: 700; font-size: 0.78rem; letter-spacing: 0.5px; white-space: nowrap; }}
    .info-box {{ background-color: #E8F5E9; border-left: 5px solid {COR_VERDE_MEDIO}; padding: 1rem 1.5rem; border-radius: 8px; margin: 0.8rem 0; color: #2C3E2C; font-size: 0.92rem; }}
    .info-box strong {{ color: #1A3A1A; }}
    section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0D1B2A 0%, #1B2838 50%, #2D4059 100%); }}
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {{ color: #F0FFF0 !important; }}
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{ color: #FFFFFF !important; }}
    .stSidebar .stMultiSelect label div {{ color: #F0FFF0 !important; }}
    .stSidebar .stMarkdown {{ color: #F0FFF0 !important; }}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(1) {{ border-left: 3px solid {COR_VERDE_CLARO}; padding-left: 8px; }}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(2) {{ border-left: 3px solid {COR_TEAL}; padding-left: 8px; }}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(3) {{ border-left: 3px solid {COR_AZULESCO}; padding-left: 8px; }}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(4) {{ border-left: 3px solid {COR_LARANJA}; padding-left: 8px; }}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(5) {{ border-left: 3px solid {COR_ROXO}; padding-left: 8px; }}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(6) {{ border-left: 3px solid {COR_BORDO}; padding-left: 8px; }}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"]:nth-of-type(7) {{ border-left: 3px solid {COR_AMBAR}; padding-left: 8px; }}
    .stTabs [data-testid="stTab"] {{ color: #5D6D7E; font-weight: 600; }}
    .stTabs [aria-selected="true"] {{ color: {COR_VERDE_ESCURO} !important; border-bottom-color: {COR_VERDE_MEDIO} !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="badge-container"><span class="badge-teste">PROJETO TESTE</span><span class="badge-andamento">EM ANDAMENTO</span></div>', unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align: center; margin-bottom: 0; color: #1A5632;'>
    Pipeline ETL - Diabetes Mellitus no SUS
</h1>
<p style='text-align: center; color: #5D6D7E; font-size: 1.1rem; margin-top: 0;'>
    Internações Hospitalares e Mortalidade | CID-10 E10-E14 | Dados Públicos DATASUS
</p>
<p style='text-align: center; color: #1A5632; font-size: 1rem; margin-top: 0; font-weight: 600;'>
    Desenvolvido por: Nathalia Adriele
</p>
""", unsafe_allow_html=True)

st.markdown('<div class="info-box">Este dashboard apresenta dados <strong>simulados/fictícios</strong> para fins de <strong>teste e validação do pipeline ETL</strong>. Os valores exibidos <strong>não representam dados reais</strong> do SUS. Projeto em desenvolvimento.</div>', unsafe_allow_html=True)


@st.cache_data
def load_data():
    if PROCESSED_PARQUET.exists():
        df = pd.read_parquet(PROCESSED_PARQUET)
    elif PROCESSED_CSV.exists():
        df = pd.read_csv(PROCESSED_CSV, encoding="utf-8")
    else:
        return None
    for col in ["ano", "mes"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            df[col] = df[col].astype(int)
    return df


@st.cache_data
def load_quality_report():
    if DATA_QUALITY_REPORT.exists():
        return pd.read_csv(DATA_QUALITY_REPORT)
    return None


@st.cache_data
def load_missing_report():
    if MISSING_VALUES_REPORT.exists():
        return pd.read_csv(MISSING_VALUES_REPORT)
    return None


@st.cache_data
def load_validation_report():
    if VALIDATION_REPORT.exists():
        return pd.read_csv(VALIDATION_REPORT)
    return None


df = load_data()

if df is None:
    st.error(
        "Dados processados não encontrados. "
        "Execute o pipeline ETL primeiro: `python -m src.data.pipeline`"
    )
    st.stop()

st.sidebar.markdown("""
**Fonte:** Dados públicos DATASUS/SUS (SIH, SIM, IBGE)
**CID-10:** E10-E14 (Diabetes Mellitus)
**Nota:** Projeto teste em andamento
""")

st.sidebar.markdown("---")
st.sidebar.markdown("## Filtros")

anos_disponiveis = sorted(df["ano"].dropna().unique())
anos_selecionados = st.sidebar.multiselect("Ano", options=anos_disponiveis, default=anos_disponiveis)

regioes_disponiveis = sorted(df["regiao"].dropna().unique()) if "regiao" in df.columns else []
regioes_selecionadas = st.sidebar.multiselect("Região", options=regioes_disponiveis, default=regioes_disponiveis)

ufs_disponiveis = sorted(df["uf"].dropna().unique()) if "uf" in df.columns else []
ufs_selecionados = st.sidebar.multiselect("UF", options=ufs_disponiveis, default=ufs_disponiveis)

sexos_disponiveis = sorted(df["sexo"].dropna().unique()) if "sexo" in df.columns else []
sexos_selecionados = st.sidebar.multiselect("Sexo", options=sexos_disponiveis, default=sexos_disponiveis)

faixas_disponiveis = [f for f in FAIXAS_ETARIAS if f in df["faixa_etaria"].dropna().unique()] if "faixa_etaria" in df.columns else []
faixas_selecionadas = st.sidebar.multiselect("Faixa Etária", options=faixas_disponiveis, default=faixas_disponiveis)

cid10_disponiveis = sorted(df["cid10"].dropna().unique()) if "cid10" in df.columns else []
cid10_selecionados = st.sidebar.multiselect("CID-10", options=cid10_disponiveis, default=cid10_disponiveis)

tipos_disponiveis = sorted(df["tipo_diabetes"].dropna().unique()) if "tipo_diabetes" in df.columns else []
tipos_selecionados = st.sidebar.multiselect("Tipo de Diabetes", options=tipos_disponiveis, default=tipos_disponiveis)

df_filtrado = df.copy()

if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["ano"].isin(anos_selecionados)]
if regioes_selecionadas and "regiao" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["regiao"].isin(regioes_selecionadas)]
if ufs_selecionados and "uf" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["uf"].isin(ufs_selecionados)]
if sexos_selecionados and "sexo" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["sexo"].isin(sexos_selecionados)]
if faixas_selecionadas and "faixa_etaria" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["faixa_etaria"].isin(faixas_selecionadas)]
if cid10_selecionados and "cid10" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["cid10"].isin(cid10_selecionados)]
if tipos_selecionados and "tipo_diabetes" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["tipo_diabetes"].isin(tipos_selecionados)]

with st.expander("Sobre o Projeto", expanded=False):
    st.markdown("""
    ### Pipeline ETL - Análise de Diabetes Mellitus no SUS

    **Projeto de teste em andamento** para desenvolvimento de pipeline ETL completo
    com dados públicos de internações hospitalares e mortalidade por Diabetes Mellitus
    no Sistema Único de Saúde (SUS).

    **Fontes dos dados:**
    - **SIH/SUS**: Sistema de Informações Hospitalares - internações e custos
    - **SIM**: Sistema de Informações de Mortalidade - óbitos
    - **IBGE/DATASUS**: População residente para cálculo de taxas

    **Recorte clínico:** CID-10 E10 a E14 (Diabetes Mellitus)

    **Nota sobre valores:** Os valores financeiros apresentados são aproximados,
    oriundos de dados públicos agregados do SIH/SUS. População utilizada para
    cálculo de taxas é deduplicada por município/ano para evitar contagem dupla.

    **Aviso:** Todos os dados utilizados são públicos e agregados, sem
    identificadores individuais. Fonte: DATASUS/Ministério da Saúde.
    """)

st.header("Indicadores Principais")

col1, col2, col3, col4, col5 = st.columns(5)

total_internacoes = int(df_filtrado["internacoes"].sum()) if "internacoes" in df_filtrado.columns else 0
total_obitos_hosp = int(df_filtrado["obitos_hospitalares"].sum()) if "obitos_hospitalares" in df_filtrado.columns else 0
total_obitos_sim = int(df_filtrado["obitos_sim"].sum()) if "obitos_sim" in df_filtrado.columns else 0
valor_total = df_filtrado["valor_total"].sum() if "valor_total" in df_filtrado.columns else 0
taxa_mort_hosp = round(total_obitos_hosp / total_internacoes * 100, 2) if total_internacoes > 0 else 0

with col1:
    st.metric("Total Internações", f"{total_internacoes:,}".replace(",", "."))
with col2:
    st.metric("Óbitos Hospitalares", f"{total_obitos_hosp:,}".replace(",", "."))
with col3:
    st.metric("Óbitos (SIM)", f"{total_obitos_sim:,}".replace(",", "."))
with col4:
    st.metric("Valor Total (aprox.)", f"~ R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
with col5:
    st.metric("Mortalidade Hosp. (%)", f"{taxa_mort_hosp}%")

n_total = len(df)
n_filtrado = len(df_filtrado)
pct = round(n_filtrado / n_total * 100, 1) if n_total > 0 else 0
st.markdown(
    f'<div style="text-align: center; color: #5D6D7E; font-size: 0.88rem; margin-bottom: 0.2rem;">'
    f'Exibindo <strong>{n_filtrado:,}</strong> de <strong>{n_total:,}</strong> registros ({pct}%)</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Série Temporal",
    "Ranking UF",
    "Demografia",
    "CID-10",
    "Indicadores Regionais",
    "Custos",
    "Base Processada",
    "Qualidade dos Dados",
])

with tab1:
    st.subheader("Evolução Temporal")
    col_ts1, col_ts2 = st.columns(2)

    with col_ts1:
        st.markdown("#### Internações por Ano")
        if "ano" in df_filtrado.columns and "internacoes" in df_filtrado.columns:
            ts_intern = df_filtrado.groupby("ano", as_index=False)["internacoes"].sum()
            fig = px.bar(
                ts_intern, x="ano", y="internacoes",
                title="Internações por Diabetes Mellitus",
                labels={"ano": "Ano", "internacoes": "Número de Internações"},
                color="internacoes", color_continuous_scale="Blues",
            )
            _style_fig(fig, showlegend=False)
            fig.update_xaxes(type="category")
            st.plotly_chart(fig, use_container_width=True)

    with col_ts2:
        st.markdown("#### Óbitos por Ano")
        if "ano" in df_filtrado.columns and "obitos_sim" in df_filtrado.columns:
            ts_obitos = df_filtrado.groupby("ano", as_index=False)["obitos_sim"].sum()
            fig = px.line(
                ts_obitos, x="ano", y="obitos_sim",
                title="Óbitos por Diabetes Mellitus (SIM)",
                labels={"ano": "Ano", "obitos_sim": "Número de Óbitos"},
                markers=True,
            )
            fig.update_traces(line_color=COR_LARANJA, line_width=3)
            _style_fig(fig)
            fig.update_xaxes(type="category")
            st.plotly_chart(fig, use_container_width=True)

    if "ano" in df_filtrado.columns and "mes" in df_filtrado.columns:
        st.markdown("#### Série Mensal de Internações")
        ts_mensal = df_filtrado.groupby(["ano", "mes"], as_index=False)["internacoes"].sum()
        ts_mensal["periodo"] = ts_mensal["ano"].astype(str) + "/" + ts_mensal["mes"].astype(str).str.zfill(2)
        fig = px.area(
            ts_mensal, x="periodo", y="internacoes",
            title="Internações Mensais",
            labels={"periodo": "Período", "internacoes": "Internações"},
        )
        fig.update_traces(line_color=COR_VERDE_ESCURO, fillcolor="rgba(26, 86, 50, 0.12)")
        _style_fig(fig)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Ranking por UF")
    col_uf1, col_uf2 = st.columns(2)

    with col_uf1:
        st.markdown("#### Internações por UF")
        if "uf" in df_filtrado.columns and "internacoes" in df_filtrado.columns:
            ranking_intern = df_filtrado.groupby("uf", as_index=False)["internacoes"].sum()
            ranking_intern = ranking_intern.sort_values("internacoes", ascending=False).head(27)
            fig = px.bar(
                ranking_intern, x="internacoes", y="uf", orientation="h",
                title="Total de Internações",
                labels={"uf": "UF", "internacoes": "Internações"},
                color="internacoes", color_continuous_scale="Blues",
            )
            _style_fig(fig, yaxis_order="total ascending")
            st.plotly_chart(fig, use_container_width=True)

    with col_uf2:
        st.markdown("#### Taxa de Internação por 100 mil hab. (média anual)")
        if "uf" in df_filtrado.columns and "internacoes" in df_filtrado.columns:
            pop_dedup_uf = df_filtrado.drop_duplicates(subset=["ano", "uf", "codigo_municipio"])
            pop_por_uf_ano = pop_dedup_uf.groupby(["uf", "ano"], as_index=False)["populacao"].sum()
            pop_por_uf = pop_por_uf_ano.groupby("uf", as_index=False)["populacao"].mean()
            intern_por_uf = df_filtrado.groupby("uf", as_index=False)["internacoes"].sum()
            n_anos = df_filtrado["ano"].nunique() if "ano" in df_filtrado.columns else 1
            intern_por_uf["internacoes_anual"] = (intern_por_uf["internacoes"] / n_anos).round(0).astype(int)
            ranking_taxa = intern_por_uf.merge(pop_por_uf, on="uf", how="left")
            ranking_taxa["taxa_100k"] = np.where(
                ranking_taxa["populacao"] > 0,
                (ranking_taxa["internacoes_anual"] / ranking_taxa["populacao"] * 100000).round(2), 0,
            )
            ranking_taxa = ranking_taxa.sort_values("taxa_100k", ascending=False)
            fig = px.bar(
                ranking_taxa, x="taxa_100k", y="uf", orientation="h",
                title="Taxa de Internação por 100 mil hab.",
                labels={"uf": "UF", "taxa_100k": "Taxa/100k"},
                color="taxa_100k", color_continuous_scale="Reds",
            )
            _style_fig(fig, yaxis_order="total ascending")
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Distribuição Demográfica")
    col_demo1, col_demo2 = st.columns(2)

    with col_demo1:
        st.markdown("#### Distribuição por Sexo")
        if "sexo" in df_filtrado.columns and "internacoes" in df_filtrado.columns:
            dist_sexo = df_filtrado.groupby("sexo", as_index=False)["internacoes"].sum()
            fig = px.pie(
                dist_sexo, names="sexo", values="internacoes", title="Internações por Sexo",
                color="sexo", color_discrete_map={
                    "Masculino": COR_AZULESCO,
                    "Feminino": COR_BORDO,
                    "Ignorado": "#95A5A6",
                },
                hole=0.4,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            _style_fig(fig, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

    with col_demo2:
        st.markdown("#### Distribuição por Faixa Etária")
        if "faixa_etaria" in df_filtrado.columns and "internacoes" in df_filtrado.columns:
            dist_idade = df_filtrado.groupby("faixa_etaria", as_index=False)["internacoes"].sum()
            ordem = {fa: i for i, fa in enumerate(FAIXAS_ETARIAS)}
            dist_idade["_ordem"] = dist_idade["faixa_etaria"].map(ordem).fillna(99)
            dist_idade = dist_idade.sort_values("_ordem")
            fig = px.bar(
                dist_idade, x="faixa_etaria", y="internacoes",
                title="Internações por Faixa Etária",
                labels={"faixa_etaria": "Faixa Etária", "internacoes": "Internações"},
                color_discrete_sequence=[COR_VERDE_MEDIO],
            )
            fig.update_xaxes(tickangle=45)
            _style_fig(fig, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Distribuição por CID-10")
    if "cid10" in df_filtrado.columns:
        col_cid1, col_cid2 = st.columns(2)
        with col_cid1:
            st.markdown("#### Internações por CID-10")
            dist_cid = df_filtrado.groupby("cid10", as_index=False).agg({
                "internacoes": "sum", "obitos_hospitalares": "sum", "obitos_sim": "sum",
            })
            fig = px.bar(dist_cid, x="cid10", y="internacoes", title="Internações por CID-10",
                         labels={"cid10": "CID-10", "internacoes": "Internações"},
                         color_discrete_sequence=[COR_TEAL])
            _style_fig(fig, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_cid2:
            st.markdown("#### Distribuição por Tipo de Diabetes")
            if "tipo_diabetes" in df_filtrado.columns:
                dist_tipo = df_filtrado.groupby("tipo_diabetes", as_index=False)["internacoes"].sum()
                cores_tipo = {
                    "Insulinodependente (Tipo 1)": COR_TEAL,
                    "Nao insulinodependente (Tipo 2)": COR_LARANJA,
                    "Relacionado com desnutricao": COR_AMBAR,
                    "Outros tipos especificados": COR_VERDE_MEDIO,
                    "Nao especificado": COR_ROXO,
                    "Nao classificado": "#95A5A6",
                }
                fig = px.pie(
                    dist_tipo, names="tipo_diabetes", values="internacoes",
                    title="Internações por Tipo de Diabetes",
                    color="tipo_diabetes", color_discrete_map=cores_tipo,
                    hole=0.4,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                _style_fig(fig, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Indicadores por Região")
    if "regiao" in df_filtrado.columns:
        intern_reg = df_filtrado.groupby("regiao", as_index=False).agg({
            "internacoes": "sum", "obitos_hospitalares": "sum", "obitos_sim": "sum",
            "valor_total": "sum",
        })
        pop_dedup_reg = df_filtrado.drop_duplicates(subset=["ano", "regiao", "uf", "codigo_municipio"])
        pop_reg_ano = pop_dedup_reg.groupby(["regiao", "ano"], as_index=False)["populacao"].sum()
        pop_reg = pop_reg_ano.groupby("regiao", as_index=False)["populacao"].mean()
        indicadores_reg = intern_reg.merge(pop_reg, on="regiao", how="left")
        n_anos_reg = df_filtrado["ano"].nunique() if "ano" in df_filtrado.columns else 1
        indicadores_reg["internacoes_anual"] = (indicadores_reg["internacoes"] / n_anos_reg).round(0).astype(int)
        indicadores_reg["obitos_anual"] = (indicadores_reg["obitos_sim"] / n_anos_reg).round(0).astype(int)
        indicadores_reg["taxa_internacao_100k"] = np.where(
            indicadores_reg["populacao"] > 0,
            (indicadores_reg["internacoes_anual"] / indicadores_reg["populacao"] * 100000).round(2), 0)
        indicadores_reg["taxa_mortalidade_100k"] = np.where(
            indicadores_reg["populacao"] > 0,
            (indicadores_reg["obitos_anual"] / indicadores_reg["populacao"] * 100000).round(2), 0)
        indicadores_reg["taxa_mort_hosp"] = np.where(
            indicadores_reg["internacoes"] > 0,
            (indicadores_reg["obitos_hospitalares"] / indicadores_reg["internacoes"] * 100).round(2), 0)

        st.dataframe(indicadores_reg, use_container_width=True, hide_index=True)
        col_reg1, col_reg2 = st.columns(2)
        cores_regiao = {
            "Norte": COR_TEAL, "Nordeste": COR_LARANJA, "Sudeste": COR_AZULESCO,
            "Sul": COR_ROXO, "Centro-Oeste": COR_VERDE_MEDIO,
        }
        with col_reg1:
            fig = px.bar(indicadores_reg, x="regiao", y="taxa_internacao_100k",
                         title="Taxa de Internacao por 100 mil",
                         color="regiao", color_discrete_map=cores_regiao)
            _style_fig(fig, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_reg2:
            fig = px.bar(indicadores_reg, x="regiao", y="taxa_mortalidade_100k",
                         title="Taxa de Mortalidade por 100 mil",
                         color="regiao", color_discrete_map=cores_regiao)
            _style_fig(fig, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("Análise de Custos Hospitalares")
    if "valor_total" in df_filtrado.columns:
        col_custo1, col_custo2 = st.columns(2)
        with col_custo1:
            st.markdown("#### Valor Total por Ano (aprox.)")
            if "ano" in df_filtrado.columns:
                custo_ano = df_filtrado.groupby("ano", as_index=False)["valor_total"].sum()
                fig = px.bar(custo_ano, x="ano", y="valor_total", title="Custo Total de Internações (R$)",
                             labels={"ano": "Ano", "valor_total": "Valor Total (R$)"},
                             color_discrete_sequence=[COR_VERDE_MEDIO])
                fig.update_xaxes(type="category")
                _style_fig(fig, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with col_custo2:
            st.markdown("#### Valor Medio por Internacao")
            if "ano" in df_filtrado.columns and "internacoes" in df_filtrado.columns:
                custo_medio = df_filtrado.groupby("ano", as_index=False).agg({"valor_total": "sum", "internacoes": "sum"})
                custo_medio["valor_medio"] = np.where(
                    custo_medio["internacoes"] > 0,
                    (custo_medio["valor_total"] / custo_medio["internacoes"]).round(2), 0)
                fig = px.line(custo_medio, x="ano", y="valor_medio", title="Valor Medio por Internacao (R$)", markers=True)
                fig.update_traces(line_color=COR_VERDE_MEDIO, line_width=3)
                fig.update_xaxes(type="category")
                _style_fig(fig)
                st.plotly_chart(fig, use_container_width=True)

        if "dias_permanencia" in df_filtrado.columns and "ano" in df_filtrado.columns:
            st.markdown("#### Media de Permanencia Hospitalar por Ano")
            perm_ano = df_filtrado.groupby("ano", as_index=False).agg({"dias_permanencia": "sum", "internacoes": "sum"})
            perm_ano["media_perm"] = np.where(
                perm_ano["internacoes"] > 0,
                (perm_ano["dias_permanencia"] / perm_ano["internacoes"]).round(2), 0)
            fig = px.bar(perm_ano, x="ano", y="media_perm", title="Media de Dias de Permanencia",
                         labels={"ano": "Ano", "media_perm": "Dias"},
                         color_discrete_sequence=[COR_AMBAR])
            fig.update_xaxes(type="category")
            _style_fig(fig, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

with tab7:
    st.subheader("Base de Dados Processada")
    st.markdown(f"**Registros:** {len(df_filtrado):,} | **Colunas:** {len(df_filtrado.columns)}")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(label="Download CSV", data=csv, file_name="diabetes_sus_filtered.csv", mime="text/csv")

with tab8:
    st.subheader("Relatório de Qualidade dos Dados")
    df_quality = load_quality_report()
    if df_quality is not None:
        st.markdown("#### Verificacoes de Qualidade")
        st.dataframe(df_quality, use_container_width=True, hide_index=True)
    else:
        st.info("Relatório de qualidade nao disponivel.")

    df_missing = load_missing_report()
    if df_missing is not None:
        st.markdown("#### Valores Ausentes por Coluna")
        st.dataframe(df_missing, use_container_width=True, hide_index=True)
    else:
        st.info("Relatório de ausentes nao disponivel.")

    df_validation = load_validation_report()
    if df_validation is not None:
        st.markdown("#### Relatório de Validacao")
        st.dataframe(df_validation, use_container_width=True, hide_index=True)
    else:
        st.info("Relatório de validacao nao disponivel.")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #5D6D7E; font-size: 0.9rem;'>
    <strong>Pipeline ETL - Diabetes Mellitus no SUS</strong> | Projeto teste em andamento<br>
    <strong>Fonte:</strong> Dados publicos do DATASUS/SUS (SIH, SIM, IBGE) |
    <strong>CID-10:</strong> E10-E14 |
    <strong>Nota:</strong> Valores financeiros sao aproximados |
    Dados agregados, sem identificadores individuais<br>
    <strong>Autora:</strong> Nathalia Adriele
</div>
""", unsafe_allow_html=True)
