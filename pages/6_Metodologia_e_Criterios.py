import streamlit as st
from views.vis_calculadora import render_metodologia

st.set_page_config(
    page_title="Metodologia & Critérios",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    render_metodologia()

if __name__ == "__main__":
    main()