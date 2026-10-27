import pandas as pd
import streamlit as st


# Cache: o CSV é lido uma vez só, e não a cada interação com os widgets
@st.cache_data
def load_data(path="data/clean/dataset.csv"):
    """Lê o dataset já tratado (exportado ao final do notebook de EDA)."""
    return pd.read_csv(path)
