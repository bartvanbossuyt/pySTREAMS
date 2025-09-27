import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import random
import math
from ineq import plot_heatmap

# Stub voor display_dataframe_to_user (niet beschikbaar buiten mijn omgeving)
def display_dataframe_to_user(title, df):
    print(title)
    print(df.head().to_string(index=False))

# --- FUNCTIE OM RANDOM POSITIES TE MAKEN ---
def generate_positions(min_val=0.5, max_val=2.2, min_distance=0.6):
    """Genereer posities voor v1 en v2, soms met gelijkheid op één as."""
    while True:
        if random.random() < 0.1:  # 10% kans op speciale situatie
            v1 = (random.uniform(min_val, max_val), random.uniform(min_val, max_val))
            v2 = (random.uniform(min_val, max_val), random.uniform(min_val, max_val))

            if random.choice(["x", "y"]) == "x":
                v2 = (v1[0], v2[1])  # zelfde x, andere y
            else:
                v2 = (v2[0], v1[1])  # zelfde y, andere x
        else:
            v1 = (random.uniform(min_val, max_val), random.uniform(min_val, max_val))
            v2 = (random.uniform(min_val, max_val), random.uniform(min_val, max_val))

        dx, dy = v1[0] - v2[0], v1[1] - v2[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance >= min_distance:
            return v1, v2

# --- INITIELE POSITIES EN HEATMAPS ---
if "positions" not in st.session_state:
    st.session_state.positions = ((2, 1), (1, 2))
if "z_d1" not in st.session_state:
    st.session_state.z_d1 = [[0, 1], [-1, 0]]
if "z_d2" not in st.session_state:
    st.session_state.z_d2 = [[0, -1], [1, 0]]

# --- CSV INLADEN ---
csv_path = "voorbeeld.csv"
if not os.path.exists(csv_path):
    print(f"Fout: bestand '{csv_path}' niet gevonden in: {os.getcwd()}")
else:
    try:
        df = pd.read_csv(csv_path, names=["con", "t", "car", "d1", "d2"], header=None)
        df_head = df.head(6)
        display_dataframe_to_user(
            "voorbeeld.csv — eerste 6 rijen (ingevoerd met header=None en vaste kolomnamen)",
            df_head,
        )
    except Exception as e:
        print("Fout bij inlezen:", e)

# --- TITEL ---
st.markdown(
    "<h1 style='text-align: left; font-size: 3rem;'>Point Descriptor Precedence</h1>",
    unsafe_allow_html=True,
)

# --- DEFINITIE ---
st.markdown(
    """
    <blockquote>
    <b>Point Descriptor Precedence (PDP)</b> is a qualitative analysis method that focuses on describing spatial and temporal relationships between objects. 
    It does not rely primarily on exact numerical data such as coordinates or distances, but instead examines qualitative relationships.
    </blockquote>
    """,
    unsafe_allow_html=True,
)

# --- POSITIES OPHALEN ---
v1, v2 = st.session_state.positions

# --- SCATTERPLOT ---
scatter_fig = go.Figure()

# v1
scatter_fig.add_trace(
    go.Scatter(
        x=[v1[0]], y=[v1[1]],
        mode="markers+text",
        marker=dict(size=14, color="white", line=dict(color="black", width=2)),
        text=["v1"], textposition="top center",
        showlegend=False,
    )
)

# v2
scatter_fig.add_trace(
    go.Scatter(
        x=[v2[0]], y=[v2[1]],
        mode="markers+text",
        marker=dict(size=14, color="black"),
        text=["v2"], textposition="top center",
        showlegend=False,
    )
)

# Assen
scatter_fig.update_xaxes(
    range=[-0.2, 2.3], showgrid=False, zeroline=False, showticklabels=False, visible=True
)
scatter_fig.update_yaxes(
    range=[-0.2, 2.4], showgrid=False, zeroline=False, showticklabels=False, visible=True
)

# Pijlen
scatter_fig.add_annotation(
    x=2.2, y=0.1, ax=0, ay=0.1,
    xref="x", yref="y", axref="x", ayref="y",
    showarrow=True, arrowhead=3, arrowwidth=2, arrowcolor="black"
)
scatter_fig.add_annotation(
    x=2.25, y=0.1, text="d1", showarrow=False,
    xref="x", yref="y", yshift=-10
)
scatter_fig.add_annotation(
    x=0.01, y=2.6, ax=0.01, ay=0,
    xref="x", yref="y", axref="x", ayref="y",
    showarrow=True, arrowhead=3, arrowwidth=2, arrowcolor="black"
)
scatter_fig.add_annotation(
    x=0.02, y=2.28, text="d2", showarrow=False,
    xref="x", yref="y", xshift=-15
)

st.plotly_chart(scatter_fig, use_container_width=True)

# --- BUTTON MET CSS ---
st.markdown(
    """
    <style>
    div[data-testid="stButton"] {
        margin-top: -20px;
    }
    div[data-testid="stButton"] > button {
        background-color: #f0f0f0;
        color: black;
        border: 1px solid black;
    }
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stButton"] > button:focus,
    div[data-testid="stButton"] > button:active {
        background-color: black;
        color: white !important;
        border: 1px solid grey;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("Shuffle positions"):
    v1, v2 = generate_positions()
    st.session_state.positions = (v1, v2)

    # --- Logica voor d1 ---
    if v1[0] < v2[0]:
        st.session_state.z_d1 = [[0, -1], [1, 0]]
    elif v1[0] == v2[0]:
        st.session_state.z_d1 = [[0, 0], [0, 0]]
    else:  # v1[0] > v2[0]
        st.session_state.z_d1 = [[0, 1], [-1, 0]]

    # --- Logica voor d2 ---
    if v2[1] > v1[1]:  # v2 ligt hoger
        st.session_state.z_d2 = [[0, -1], [1, 0]]
    elif v2[1] == v1[1]:
        st.session_state.z_d2 = [[0, 0], [0, 0]]
    else:  # v2 ligt lager
        st.session_state.z_d2 = [[0, 1], [-1, 0]]

    st.experimental_rerun()

# --- HEATMAPS ---
col1, col2 = st.columns(2)
with col1:
    plot_heatmap(z=st.session_state.z_d1,
                 x_labels=["v1", "v2"], y_labels=["v1", "v2"],
                 title="d1", width=180, height=180, show_values=True)
with col2:
    plot_heatmap(z=st.session_state.z_d2,
                 x_labels=["v1", "v2"], y_labels=["v1", "v2"],
                 title="d2", width=180, height=180, show_values=True)
