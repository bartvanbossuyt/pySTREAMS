import plotly.graph_objects as go
import streamlit as st

def plot_heatmap(z, x_labels=None, y_labels=None, title="Heatmap", width=180, height=180, show_values=True):
    if x_labels is None:
        x_labels = [f"x{i}" for i in range(len(z[0]))]
    if y_labels is None:
        y_labels = [f"y{i}" for i in range(len(z))]

    # Mapping van waarden naar symbolen
    symbol_map = {-1: "<", 0: "=", 1: ">"}
    if show_values:
        text_matrix = [[symbol_map.get(val, "") for val in row] for row in z]
        texttemplate = "%{text}"
    else:
        text_matrix = None
        texttemplate = None

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x_labels,
            y=y_labels,
            colorscale=[
                [0.0, "#00ff00"],  # -1 -> groen
                [0.5, "#ffff00"],  #  0 -> geel
                [1.0, "#ff0000"],  #  1 -> rood
            ],
            zmin=-1,
            zmax=1,
            text=text_matrix,
            texttemplate=texttemplate,
            showscale=False,
        )
    )

    fig_heatmap.update_xaxes(side="top", showgrid=False, zeroline=False)
    fig_heatmap.update_yaxes(autorange="reversed", showgrid=False, zeroline=False)

    fig_heatmap.update_layout(
        title=dict(text=title, x=0, xanchor="left"),
        width=width,
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    st.plotly_chart(fig_heatmap, use_container_width=False)