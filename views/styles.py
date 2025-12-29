import streamlit as st
import os

def aplicar_estilo_ranking(df):
    """
    Aplica a lógica de cores nas linhas do ranking para o Pandas Styler.
    """
    def colorir_linhas(row):
        # Garante que temos a coluna Rank ou usa o índice
        rank = row.get('Rank', row.name + 1)
        
        if rank <= 10:
            color = '#d4edda' # Verde (Top 10)
        elif rank <= 20:
            color = '#fff3cd' # Amarelo (Top 20)
        elif rank <= 30:
            color = '#ffeeba' # Laranja (Top 30)
        else:
            color = 'white'
            
        return [f'background-color: {color}; color: black'] * len(row)

    return df.style.apply(colorir_linhas, axis=1)

def load_css(file_name):
    """
    Carrega um arquivo CSS da pasta assets/css e injeta na página.
    """
    # Constroi o caminho relativo: assets/css/nome_do_arquivo.css
    css_path = os.path.join("assets", "css", file_name)
    
    try:
        with open(css_path) as f:
            css = f.read()
            # Usa o st.html com a tag <style> conforme documentação nova
            st.html(f"<style>{css}</style>")
    except FileNotFoundError:
        st.warning(f"Arquivo de estilo não encontrado: {css_path}")   