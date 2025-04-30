import plotly.graph_objects as go
import pandas as pd

def plot_line_chart(data_dict, title, x_label, y_label):
    fig = go.Figure()
    for name, series in data_dict.items():
        fig.add_trace(go.Scatter(x=series.index, y=series.values, mode='lines', name=name))
    fig.update_layout(title=title, xaxis_title=x_label, yaxis_title=y_label)
    return fig

def export_to_csv(df: pd.DataFrame, filename: str) -> bytes:
    return df.to_csv().encode("utf-8")
