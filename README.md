# dy-st

`dy-st` provides LitCharts, an interactive chart application built with Streamlit and Plotly.
It accepts CSV or TSV files, pasted data, and a built-in sample dataset.

## Run

Use Python 3.12 or newer and uv.
Run these commands from the repository root:

```bash
uv sync --locked
uv run streamlit run app.py
```

Open the local address that Streamlit prints.

## Create a chart

1. Select a data source in the sidebar.
2. Select a chart type and its data columns.
3. Set the title, colors, theme, and legend options.
4. Open **Data preview** to inspect the source rows.

The application supports bar, line, area, scatter, pie, histogram, box, and heatmap charts.

## Excel files

The upload control also accepts `.xlsx` files.
Excel input needs `openpyxl`, which the project does not include in its dependencies.
To use Excel input, start the application with:

```bash
uv run --with openpyxl streamlit run app.py
```
