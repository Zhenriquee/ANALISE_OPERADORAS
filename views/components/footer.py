import streamlit as st
from views.styles import load_css  # Importante importar aqui também

def render_sidebar_footer():
    """
    Renderiza o rodapé da barra lateral (LinkedIn e Créditos).
    """
    # 1. Carrega o CSS específico do Footer
    load_css("footer.css")

    st.sidebar.markdown("---")
    
    st.sidebar.html(
        """
        <div class="sidebar-footer-container">
            <p class="sidebar-footer-text">
                Desenvolvido por <br><b>Luiz Henrique</b>
            </p>
            
            <a href="https://www.linkedin.com/in/luiz-henrique-8271051b5" target="_blank" style="text-decoration: none;">
                <div class="linkedin-button">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" class="linkedin-icon">
                    Conectar no LinkedIn
                </div>
            </a>
        </div>
        """
    )