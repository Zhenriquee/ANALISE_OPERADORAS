import streamlit as st
from views.styles import load_css

def render_sidebar_header():
    """
    Renderiza o Cabeçalho do Sidebar com cores ajustadas para Dark Mode.
    """
    # 1. Carrega o CSS específico do Header
    load_css("header.css")
    
    # 2. HTML com as classes (o conteúdo visual é controlado pelo CSS agora)
    st.sidebar.html(
        """
        <div class="sidebar-header-container">
            <h1 class="sidebar-title">
                Health Market<br>
                <span>Vision</span>
            </h1>
            
            <div class="sidebar-divider"></div>
            
            <p class="sidebar-subtitle">
                Inteligência Estratégica
            </p>
        </div>
        """
    )