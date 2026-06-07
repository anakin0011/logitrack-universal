import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="LogiTrack Universal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos personalizados ──────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
            color: #1a1a2e;
            margin-bottom: 0;
        }
        .sub-title {
            font-size: 1rem;
            color: #6c757d;
            margin-top: 0;
            margin-bottom: 1.5rem;
        }
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            color: white;
            text-align: center;
        }
        .kpi-card-green {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            color: white;
            text-align: center;
        }
        .kpi-card-orange {
            background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            color: white;
            text-align: center;
        }
        .kpi-number {
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
        }
        .kpi-label {
            font-size: 0.8rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .welcome-box {
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            border-radius: 0 8px 8px 0;
            padding: 1rem 1.2rem;
            margin-bottom: 1.5rem;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 0.5rem;
        }
        div[data-testid="stSidebar"] {
            background: #1a1a2e;
        }
        div[data-testid="stSidebar"] * {
            color: #e0e0e0 !important;
        }
        div[data-testid="stSidebar"] .stSelectbox label,
        div[data-testid="stSidebar"] .stRadio label {
            color: #c0c0c0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Encabezado ──────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">📊 LogiTrack Universal</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Visualizador inteligente de datos Excel — carga cualquier archivo y genera gráficos al instante</p>',
    unsafe_allow_html=True,
)

# ── Bienvenida ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="welcome-box">
        <strong>👋 ¿Cómo usar esta herramienta?</strong><br>
        <ol style="margin:0.5rem 0 0 1rem; padding:0;">
            <li>Sube tu archivo Excel (.xlsx) desde la barra lateral.</li>
            <li>Elige la <strong>columna para el eje X</strong> (categorías o fechas).</li>
            <li>Elige la <strong>columna de valores</strong> (números o totales).</li>
            <li>Selecciona el <strong>tipo de gráfico</strong> que prefieras.</li>
            <li>¡Listo! Explora los KPIs, el gráfico interactivo y descarga el resumen.</li>
        </ol>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Barra lateral ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")

    archivo = st.file_uploader(
        "📂 Sube tu archivo Excel",
        type=["xlsx"],
        help="Se aceptan archivos .xlsx de cualquier estructura.",
    )

    if archivo:
        try:
            hojas = pd.ExcelFile(archivo).sheet_names
            hoja_sel = st.selectbox("📋 Hoja de cálculo", hojas)
        except Exception:
            hojas = []
            hoja_sel = None

        st.markdown("---")
        st.markdown("### 🎨 Tipo de gráfico")
        tipo_grafico = st.radio(
            "",
            options=["Barras", "Torta", "Línea"],
            index=0,
            horizontal=False,
        )

        st.markdown("---")
        st.info("💡 Las columnas aparecerán luego de cargar el archivo.")

    st.markdown("---")
    st.markdown(
        "<small style='color:#888'>LogiTrack Universal v1.0 · 2026</small>",
        unsafe_allow_html=True,
    )

# ── Lógica principal ────────────────────────────────────────────────────────
if archivo is None:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align:center; padding:3rem 0; color:#aaa'>
                <div style='font-size:4rem'>📁</div>
                <p style='font-size:1.1rem; margin-top:0.5rem'>
                    Sube un archivo Excel desde la barra lateral para comenzar
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()

# ── Carga del DataFrame ─────────────────────────────────────────────────────
try:
    df = pd.read_excel(archivo, sheet_name=hoja_sel)
except Exception as e:
    st.error(f"No se pudo leer el archivo: {e}")
    st.stop()

if df.empty:
    st.warning("El archivo está vacío o la hoja seleccionada no tiene datos.")
    st.stop()

# ── Selectores de columnas (sidebar, después de cargar) ─────────────────────
columnas = df.columns.tolist()

with st.sidebar:
    st.markdown("### 📌 Columnas")
    col_x = st.selectbox("Eje X (categorías)", columnas, index=0)
    cols_numericas = [c for c in columnas if pd.api.types.is_numeric_dtype(df[c])]
    col_y_opciones = cols_numericas if cols_numericas else columnas
    col_y_default = 1 if len(col_y_opciones) > 1 else 0
    col_y = st.selectbox("Valores (eje Y)", col_y_opciones, index=col_y_default)

# ── KPIs ────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">📈 Resumen del dataset</p>', unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-number">{len(df):,}</div>
            <div class="kpi-label">Total de filas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card-green">
            <div class="kpi-number">{len(df.columns)}</div>
            <div class="kpi-label">Columnas detectadas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    valores_unicos = df[col_x].nunique()
    st.markdown(
        f"""
        <div class="kpi-card-orange">
            <div class="kpi-number">{valores_unicos:,}</div>
            <div class="kpi-label">Valores únicos en "{col_x}"</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Preparar datos agrupados ────────────────────────────────────────────────
try:
    df_grouped = (
        df.groupby(col_x, as_index=False)[col_y]
        .sum()
        .sort_values(col_y, ascending=False)
    )
except Exception:
    df_grouped = df[[col_x, col_y]].dropna()

# ── Gráfico ─────────────────────────────────────────────────────────────────
st.markdown(
    f'<p class="section-title">🗺️ Gráfico — {tipo_grafico}: {col_y} por {col_x}</p>',
    unsafe_allow_html=True,
)

colores = px.colors.qualitative.Vivid

try:
    if tipo_grafico == "Barras":
        fig = px.bar(
            df_grouped,
            x=col_x,
            y=col_y,
            color=col_x,
            color_discrete_sequence=colores,
            template="plotly_white",
            labels={col_x: col_x, col_y: col_y},
        )
        fig.update_layout(showlegend=False)

    elif tipo_grafico == "Torta":
        fig = px.pie(
            df_grouped,
            names=col_x,
            values=col_y,
            color_discrete_sequence=colores,
            template="plotly_white",
            hole=0.35,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")

    elif tipo_grafico == "Línea":
        df_line = df_grouped.sort_values(col_x)
        fig = px.line(
            df_line,
            x=col_x,
            y=col_y,
            markers=True,
            color_discrete_sequence=["#667eea"],
            template="plotly_white",
            labels={col_x: col_x, col_y: col_y},
        )
        fig.update_traces(line_width=3, marker_size=8)

    fig.update_layout(
        font_family="Inter, Arial, sans-serif",
        margin=dict(t=30, b=30, l=10, r=10),
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"No se pudo generar el gráfico: {e}")

# ── Tabla de datos ──────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Ver tabla de datos completa", expanded=False):
    st.dataframe(df, use_container_width=True, height=320)

# ── Descarga del resumen ─────────────────────────────────────────────────────
st.markdown('<p class="section-title">⬇️ Descargar resumen</p>', unsafe_allow_html=True)

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    df_grouped.to_excel(writer, sheet_name="Resumen", index=False)
    df.to_excel(writer, sheet_name="Datos completos", index=False)

    workbook = writer.book
    fmt_header = workbook.add_format(
        {"bold": True, "bg_color": "#667eea", "font_color": "#ffffff", "border": 1}
    )
    fmt_num = workbook.add_format({"num_format": "#,##0.00"})

    for sheet_name in ["Resumen", "Datos completos"]:
        ws = writer.sheets[sheet_name]
        target_df = df_grouped if sheet_name == "Resumen" else df
        for col_idx, col_name in enumerate(target_df.columns):
            ws.write(0, col_idx, col_name, fmt_header)
            ws.set_column(col_idx, col_idx, max(len(str(col_name)) + 4, 14))

buffer.seek(0)

st.download_button(
    label="📥 Descargar resumen en Excel",
    data=buffer,
    file_name="logitrack_resumen.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.markdown(
    "<br><small style='color:#bbb'>LogiTrack Universal · Generado con Streamlit y Plotly</small>",
    unsafe_allow_html=True,
)
