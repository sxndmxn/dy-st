import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="LitCharts", layout="wide", page_icon="📊")

st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; }
    h1 { background: linear-gradient(90deg, #ff6ec7, #7873f5, #00d4ff);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent;
         font-size: 3rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("LitCharts")

# ── Sidebar: data source ──────────────────────────────────────────────
with st.sidebar:
    st.header("Data")
    source = st.radio("Source", ["Upload CSV", "Paste data", "Sample data"])

    if source == "Upload CSV":
        f = st.file_uploader("CSV file", type=["csv", "tsv", "xlsx"])
        if f:
            df = (
                pd.read_excel(f)
                if f.name.endswith(".xlsx")
                else pd.read_csv(f, sep="\t" if f.name.endswith(".tsv") else ",")
            )
        else:
            df = None
    elif source == "Paste data":
        raw = st.text_area("Paste CSV / TSV", height=200, placeholder="name,score\nAlice,90\nBob,75")
        if raw.strip():
            import io
            sep = "\t" if "\t" in raw else ","
            df = pd.read_csv(io.StringIO(raw), sep=sep)
        else:
            df = None
    else:
        df = pd.DataFrame(
            {
                "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "Revenue": [12, 19, 14, 25, 22, 30, 35, 28, 40, 38, 45, 50],
                "Expenses": [10, 14, 11, 18, 17, 22, 25, 21, 30, 28, 33, 37],
                "Headcount": [5, 5, 6, 6, 7, 8, 8, 9, 10, 10, 12, 14],
            }
        )

if df is None:
    st.info("Load some data to get started →")
    st.stop()

# ── Sidebar: chart config ─────────────────────────────────────────────
with st.sidebar:
    st.header("Chart config")

    chart_type = st.selectbox(
        "Chart type",
        ["Bar", "Line", "Area", "Scatter", "Pie", "Histogram", "Box", "Heatmap"],
    )

    cols = list(df.columns)
    num_cols = list(df.select_dtypes("number").columns)

    x_col = st.selectbox("X axis", cols, index=0)

    if chart_type == "Pie":
        y_col = st.selectbox("Values", num_cols, index=0 if num_cols else 0)
    elif chart_type == "Histogram":
        y_col = st.selectbox("Column", cols, index=min(1, len(cols) - 1))
    elif chart_type == "Heatmap":
        y_col = st.selectbox("Y axis", cols, index=min(1, len(cols) - 1))
        z_col = st.selectbox("Z (values)", num_cols, index=0 if num_cols else 0)
    else:
        default_y = min(1, len(cols) - 1)
        y_col = st.multiselect("Y axis", cols, default=[cols[default_y]])

    st.header("Style")
    title = st.text_input("Chart title", "")
    palette = st.selectbox(
        "Color palette",
        ["plotly", "D3", "Set2", "Pastel", "Dark2", "Vivid", "Bold", "Antique"],
    )
    template = st.selectbox(
        "Theme", ["plotly_dark", "plotly", "plotly_white", "seaborn", "ggplot2"]
    )
    show_legend = st.checkbox("Show legend", value=True)
    log_y = st.checkbox("Log Y scale", value=False)

# ── Build chart ────────────────────────────────────────────────────────
color_map = {
    "plotly": px.colors.qualitative.Plotly,
    "D3": px.colors.qualitative.D3,
    "Set2": px.colors.qualitative.Set2,
    "Pastel": px.colors.qualitative.Pastel,
    "Dark2": px.colors.qualitative.Dark2,
    "Vivid": px.colors.qualitative.Vivid,
    "Bold": px.colors.qualitative.Bold,
    "Antique": px.colors.qualitative.Antique,
}
colors = color_map[palette]

common = dict(template=template, title=title or None)

if chart_type == "Pie":
    fig = px.pie(df, names=x_col, values=y_col, color_discrete_sequence=colors, **common)

elif chart_type == "Histogram":
    fig = px.histogram(df, x=y_col, color_discrete_sequence=colors, **common)

elif chart_type == "Heatmap":
    pivot = df.pivot_table(index=y_col, columns=x_col, values=z_col, aggfunc="mean")
    fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale="Viridis", **common)

elif chart_type == "Box":
    if isinstance(y_col, list) and len(y_col) > 0:
        melted = df.melt(id_vars=[x_col], value_vars=y_col)
        fig = px.box(melted, x=x_col, y="value", color="variable",
                     color_discrete_sequence=colors, **common)
    else:
        fig = px.box(df, x=x_col, color_discrete_sequence=colors, **common)

else:
    plot_fn = {"Bar": px.bar, "Line": px.line, "Area": px.area, "Scatter": px.scatter}[chart_type]

    if isinstance(y_col, list) and len(y_col) == 1:
        fig = plot_fn(df, x=x_col, y=y_col[0], color_discrete_sequence=colors, **common)
    elif isinstance(y_col, list) and len(y_col) > 1:
        melted = df.melt(id_vars=[x_col], value_vars=y_col)
        fig = plot_fn(melted, x=x_col, y="value", color="variable",
                      color_discrete_sequence=colors, **common)
    else:
        fig = go.Figure()

if log_y and chart_type not in ("Pie", "Heatmap"):
    fig.update_yaxes(type="log")

fig.update_layout(showlegend=show_legend, margin=dict(t=60, b=40, l=40, r=40))

st.plotly_chart(fig, use_container_width=True)

# ── Data preview ───────────────────────────────────────────────────────
with st.expander("Data preview"):
    st.dataframe(df, use_container_width=True)
