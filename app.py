"""
ENIGH 2022 — Dashboard Streamlit
Encuesta Nacional de Ingresos y Gastos de los Hogares · INEGI · México
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="ENIGH 2022 · Dashboard",
    page_icon="📊",
    layout="wide",
)

BASE = os.path.dirname(os.path.abspath(__file__))

PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#aec7e8",
    "#ffbb78",
    "#98df8a",
    "#ff9896",
    "#c5b0d5",
]

# ── Carga de datos (cacheada) ─────────────────────────────────────────────────


@st.cache_data
def load_gasto_letra_entidad():
    return pd.read_csv(
        os.path.join(BASE, "agg_gasto_letra_entidad.csv"), encoding="utf-8-sig"
    )


@st.cache_data
def load_gasto_por_estado():
    return pd.read_csv(
        os.path.join(BASE, "agg_gasto_por_estado.csv"), encoding="utf-8-sig"
    )


@st.cache_data
def load_gini():
    return pd.read_csv(
        os.path.join(BASE, "agg_gini_por_entidad.csv"), encoding="utf-8-sig"
    )


@st.cache_data
def load_ingreso_fuente():
    return pd.read_csv(
        os.path.join(BASE, "agg_ingreso_fuente.csv"), encoding="utf-8-sig"
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.title("📊 ENIGH 2022")
st.sidebar.caption("Encuesta Nacional de Ingresos y Gastos de los Hogares · México")
st.sidebar.markdown("---")

PAGES = {
    "🏠 Inicio": "home",
    "📦 D1 · Estructura del Gasto": "d1",
    "💰 D2 · Composición del Ingreso": "d2",
    "🗺️ D3 · Disparidades Regionales": "d3",
    "💳 D4 · Métodos de Pago": "d4",
    "🏪 D5 · Canales de Compra": "d5",
    "🏥 D6 · Gasto en Salud": "d6",
    "📐 D7 · Coeficiente de Gini": "d7",
    "📅 D8 · Estacionalidad": "d8",
}

selection = st.sidebar.radio("Navegación", list(PAGES.keys()))
page = PAGES[selection]

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Autores:** Manuel Díaz Rojo · Alejandro Chavez Garcia · Ruben Siloé Reyes Vallejo\n\n"
    "**Fuente:** INEGI · Tercer Trimestre 2022"
)

# ── Página: Inicio ────────────────────────────────────────────────────────────

if page == "home":
    st.title("Dashboard ENIGH 2022")
    st.subheader("Encuesta Nacional de Ingresos y Gastos de los Hogares")
    st.markdown("""
**Fuente:** INEGI — Instituto Nacional de Estadística y Geografía
**Periodo:** Tercer Trimestre 2022 (agosto–noviembre)
**Universo:** Hogares mexicanos a nivel nacional

---

Este dashboard presenta el análisis de los patrones de gasto e ingreso de los hogares mexicanos
a partir de los microdatos de la ENIGH 2022. Usa el menú de la izquierda para explorar cada sección.

| Dashboard | Descripción |
|-----------|-------------|
| D1 | Estructura del gasto por grandes rubros (alimentación, vivienda, salud…) |
| D2 | Composición del ingreso por fuente (trabajo, transferencias, capital…) |
| D3 | Disparidades regionales del gasto entre estados |
| D4 | Distribución de métodos de pago utilizados |
| D5 | Canales de compra (mercados, tiendas de conveniencia, internet…) |
| D6 | Gasto en salud por institución |
| D7 | Desigualdad económica (Coeficiente de Gini por entidad) |
| D8 | Estacionalidad del gasto por mes |
    """)

    col1, col2, col3 = st.columns(3)
    df_estado = load_gasto_por_estado()
    df_fuente = load_ingreso_fuente()
    df_gini = load_gini()

    col1.metric(
        "Total gasto ponderado",
        f"${df_estado['gasto_pond'].sum() / 1e12:.2f} bill. MXN",
    )
    col2.metric(
        "Total ingreso ponderado",
        f"${df_fuente['ingreso_pond'].sum() / 1e12:.2f} bill. MXN",
    )
    col3.metric("Gini promedio nacional", f"{df_gini['gini'].mean():.3f}")

# ── D1: Estructura del Gasto ──────────────────────────────────────────────────

elif page == "d1":
    st.title("D1 · Estructura del Gasto por Grandes Rubros")
    st.caption("Gasto trimestral ponderado por factor de expansión · ENIGH 2022")

    df = load_gasto_letra_entidad()
    d1 = (
        df[df["clave_letra"] != "T"]
        .groupby("categoria")["gasto_pond"]
        .sum()
        .reset_index()
        .sort_values("gasto_pond", ascending=False)
    )
    d1["pct"] = d1["gasto_pond"] / d1["gasto_pond"].sum() * 100
    d1["gasto_mmd"] = d1["gasto_pond"] / 1e9  # miles de millones

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            d1,
            names="categoria",
            values="gasto_pond",
            color_discrete_sequence=PALETTE,
            title="Distribución porcentual del gasto",
            hole=0,
        )
        fig_pie.update_traces(
            textposition="inside", textinfo="percent+label", textfont_size=11
        )
        fig_pie.update_layout(showlegend=False, height=480)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            d1.sort_values("gasto_mmd"),
            x="gasto_mmd",
            y="categoria",
            orientation="h",
            color="categoria",
            color_discrete_sequence=PALETTE,
            text=d1.sort_values("gasto_mmd")["pct"].map(lambda p: f"{p:.1f}%"),
            title="Monto absoluto por rubro (miles de millones MXN)",
            labels={"gasto_mmd": "Gasto (miles de mill. MXN)", "categoria": ""},
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False, height=480)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Tabla de datos")
    st.dataframe(
        d1[["categoria", "gasto_mmd", "pct"]]
        .rename(
            columns={
                "categoria": "Rubro",
                "gasto_mmd": "Gasto (miles de mill. MXN)",
                "pct": "% del total",
            }
        )
        .sort_values("Gasto (miles de mill. MXN)", ascending=False)
        .reset_index(drop=True)
        .style.format(
            {"Gasto (miles de mill. MXN)": "{:.1f}", "% del total": "{:.1f}%"}
        ),
        use_container_width=True,
    )

# ── D2: Composición del Ingreso ───────────────────────────────────────────────

elif page == "d2":
    st.title("D2 · Composición del Ingreso por Fuente")
    st.caption("Ingreso trimestral ponderado · ENIGH 2022")

    d2 = load_ingreso_fuente().sort_values("ingreso_pond", ascending=False)
    d2["pct"] = d2["ingreso_pond"] / d2["ingreso_pond"].sum() * 100
    d2["ingreso_mmd"] = d2["ingreso_pond"] / 1e9

    col1, col2 = st.columns(2)

    with col1:
        fig_donut = px.pie(
            d2,
            names="fuente",
            values="ingreso_pond",
            color_discrete_sequence=PALETTE,
            title="Distribución porcentual del ingreso",
            hole=0.5,
        )
        fig_donut.update_traces(
            textposition="outside", textinfo="percent+label", textfont_size=11
        )
        fig_donut.update_layout(showlegend=False, height=480)
        total = d2["ingreso_pond"].sum()
        fig_donut.add_annotation(
            text=f"<b>${total / 1e12:.2f}</b><br>bill. MXN",
            x=0.5,
            y=0.5,
            showarrow=False,
            font_size=14,
            align="center",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            d2.sort_values("ingreso_mmd"),
            x="ingreso_mmd",
            y="fuente",
            orientation="h",
            color="fuente",
            color_discrete_sequence=PALETTE,
            text=d2.sort_values("ingreso_mmd")["pct"].map(lambda p: f"{p:.1f}%"),
            title="Monto por fuente de ingreso (miles de millones MXN)",
            labels={"ingreso_mmd": "Ingreso (miles de mill. MXN)", "fuente": ""},
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False, height=480)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Tabla de datos")
    st.dataframe(
        d2[["fuente", "ingreso_mmd", "pct"]]
        .rename(
            columns={
                "fuente": "Fuente",
                "ingreso_mmd": "Ingreso (miles de mill. MXN)",
                "pct": "% del total",
            }
        )
        .reset_index(drop=True)
        .style.format(
            {"Ingreso (miles de mill. MXN)": "{:.1f}", "% del total": "{:.1f}%"}
        ),
        use_container_width=True,
    )

# ── D3: Disparidades Regionales ───────────────────────────────────────────────

elif page == "d3":
    st.title("D3 · Disparidades Regionales del Gasto")
    st.caption("Gasto trimestral ponderado total por entidad federativa · ENIGH 2022")

    df_estado = load_gasto_por_estado().sort_values("gasto_pond", ascending=False)
    df_estado["gasto_mmd"] = df_estado["gasto_pond"] / 1e9

    fig = px.bar(
        df_estado.sort_values("gasto_mmd"),
        x="gasto_mmd",
        y="estado",
        orientation="h",
        color="gasto_mmd",
        color_continuous_scale="Blues",
        title="Gasto total por entidad federativa (miles de millones MXN)",
        labels={"gasto_mmd": "Gasto (miles de mill. MXN)", "estado": ""},
        text="gasto_mmd",
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=750)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Composición del gasto por rubro y estado")
    df_letra = load_gasto_letra_entidad()
    df_letra = df_letra[df_letra["clave_letra"] != "T"].copy()

    estados = sorted(df_letra["estado"].dropna().unique())
    selected = st.multiselect("Filtrar estados", estados, default=estados[:8])

    if selected:
        df_filtered = df_letra[df_letra["estado"].isin(selected)]
        fig2 = px.bar(
            df_filtered.groupby(["estado", "categoria"])["gasto_pond"]
            .sum()
            .reset_index()
            .assign(gasto_mmd=lambda x: x["gasto_pond"] / 1e9),
            x="estado",
            y="gasto_mmd",
            color="categoria",
            color_discrete_sequence=PALETTE,
            title="Gasto por rubro y entidad",
            labels={
                "gasto_mmd": "Gasto (miles de mill. MXN)",
                "estado": "",
                "categoria": "Rubro",
            },
        )
        fig2.update_layout(height=480)
        st.plotly_chart(fig2, use_container_width=True)

# ── D4: Métodos de Pago ───────────────────────────────────────────────────────

elif page == "d4":
    st.title("D4 · Métodos de Pago")
    st.caption("Distribución del gasto por forma de pago · ENIGH 2022")
    img_path = os.path.join(BASE, "d4_metodos_pago.png")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning("Imagen no encontrada. Ejecuta el notebook para generarla.")

# ── D5: Canales de Compra ─────────────────────────────────────────────────────

elif page == "d5":
    st.title("D5 · Canales de Compra")
    st.caption("Distribución del gasto por lugar de compra · ENIGH 2022")
    img_path = os.path.join(BASE, "d5_canales_compra.png")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning("Imagen no encontrada. Ejecuta el notebook para generarla.")

# ── D6: Gasto en Salud ────────────────────────────────────────────────────────

elif page == "d6":
    st.title("D6 · Gasto en Salud por Institución")
    st.caption("Gasto ponderado en el rubro J (Salud) por institución · ENIGH 2022")
    img_path = os.path.join(BASE, "d6_gasto_salud.png")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning("Imagen no encontrada. Ejecuta el notebook para generarla.")

# ── D7: Coeficiente de Gini ───────────────────────────────────────────────────

elif page == "d7":
    st.title("D7 · Coeficiente de Gini por Entidad")
    st.caption("Desigualdad del ingreso a nivel estatal · ENIGH 2022")

    df_gini = load_gini().sort_values("gini", ascending=False)

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Gini más alto", df_gini.iloc[0]["estado"], f"{df_gini.iloc[0]['gini']:.3f}"
    )
    col2.metric("Gini promedio nacional", "", f"{df_gini['gini'].mean():.3f}")
    col3.metric(
        "Gini más bajo", df_gini.iloc[-1]["estado"], f"{df_gini.iloc[-1]['gini']:.3f}"
    )

    fig = px.bar(
        df_gini.sort_values("gini"),
        x="gini",
        y="estado",
        orientation="h",
        color="gini",
        color_continuous_scale="RdYlGn_r",
        title="Coeficiente de Gini por entidad federativa (0 = igualdad perfecta, 1 = desigualdad máxima)",
        labels={"gini": "Coeficiente de Gini", "estado": ""},
        text="gini",
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(height=750, coloraxis_showscale=True)

    # Línea promedio
    fig.add_vline(
        x=df_gini["gini"].mean(),
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Promedio: {df_gini['gini'].mean():.3f}",
        annotation_position="top",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Lorenz/Gini image if available
    img_path = os.path.join(BASE, "d7_lorenz_gini.png")
    if os.path.exists(img_path):
        st.markdown("---")
        st.subheader("Curva de Lorenz")
        st.image(img_path, use_container_width=True)

# ── D8: Estacionalidad ────────────────────────────────────────────────────────

elif page == "d8":
    st.title("D8 · Estacionalidad del Gasto")
    st.caption("Distribución mensual del gasto por categoría · ENIGH 2022")
    img_path = os.path.join(BASE, "d8_estacionalidad.png")
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning("Imagen no encontrada. Ejecuta el notebook para generarla.")
