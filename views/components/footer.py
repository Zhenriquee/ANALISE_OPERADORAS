import streamlit as st
from views.styles import load_css

def render_sidebar_footer():
    """
    Renderiza o rodapé da barra lateral (LinkedIn + Documentação).
    """
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

            <a href="https://docs.google.com/document/d/1FJV0IN9HOWDdnhMLS7iQu9ZFVRDOXcStqzp1U_CjhBg/edit?usp=sharing" target="_blank" style="text-decoration: none;">
                <div class="doc-button">
                    <img src="https://cdn-icons-png.flaticon.com/512/2991/2991148.png" class="doc-icon">
                    Ver Documentação
                </div>
            </a>
        </div>
        """
    )