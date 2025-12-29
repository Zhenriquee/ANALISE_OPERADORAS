# 🏥 Health Market Vision
### Inteligência Estratégica para o Mercado de Saúde Suplementar (ANS)

![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![Data Science](https://img.shields.io/badge/Sklearn-KMeans%20%7C%20PCA-orange)

---

## 🎯 Sobre o Projeto

O **Health Market Vision** é uma plataforma de Business Intelligence (BI) e Ciência de Dados desenvolvida para transformar os dados brutos e complexos da **Agência Nacional de Saúde Suplementar (ANS)** em insights estratégicos acionáveis.

Diferente de dashboards tradicionais que apenas mostram tabelas, este projeto aplica algoritmos proprietários para criar rankings justos (Scores), identificar concorrentes ocultos (Clusterização) e prever tendências de mercado.

### 🚀 Destaques Principais
* **Rankings Inteligentes:** Algoritmos de pontuação (*Power Score*) que normalizam operadoras de diferentes portes.
* **Data Science Avançado:** Clusterização de mercado utilizando **K-Means** e projeção vetorial em **Cubo 3D (PCA)**.
* **Benchmarking Competitivo:** Comparação "Head-to-Head" com gráficos de radar e análise de gaps.
* **Storytelling Automatizado:** Geração de textos analíticos que interpretam os dados para o usuário.
* **Engenharia de Dados Robusta:** Pipeline de extração paralela (Multiprocessing) para lidar com gigabytes de dados históricos.

---

## 📊 Funcionalidades e Telas

### 1. Panorama Estratégico
Visão macro do mercado. Ranking dinâmico das maiores operadoras, análise de Market Share e identificação de líderes por modalidade.

### 2. Diagnóstico 360º
Um "Raio-X" completo de qualquer operadora. Analisa a saúde financeira, crescimento da carteira e calcula o **Spread (Alpha)** — métrica que isola o desempenho da empresa da "maré" do mercado.

### 3. Performance Financeira & Vidas
Análises profundas sobre sustentabilidade:
* **Ticket Médio:** Evolução do preço médio.
* **CAGR:** Crescimento Anual Composto (Tendência estrutural).
* **Volatilidade:** Cálculo de risco e estabilidade de receita.

### 4. Clusterização (Machine Learning)
O sistema agrupa operadoras automaticamente baseando-se em comportamento matemático, não apenas em tamanho.
* **Algoritmo:** K-Means Clustering.
* **Visualização:** Projeção 3D interativa (PCA) mostrando a distância estratégica entre os grupos.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12
* **Frontend/Framework:** Streamlit
* **Manipulação de Dados:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (StandardScaler, KMeans, PCA)
* **Visualização:** Plotly Express & Graph Objects
* **Banco de Dados:** SQLite (Alta performance para leitura)
* **ETL:** Requests, BeautifulSoup, Multiprocessing

---

## 🧠 Metodologia de Cálculo (Scores)

Para garantir comparações justas entre uma operadora gigante (ex: Amil) e uma regional (ex: Unimed Local), utilizamos **Normalização Logarítmica (`np.log1p`)**:

* **⭐ Power Score (Nota Geral):**
    * 40% Tamanho (Vidas)
    * 40% Financeiro (Receita)
    * 20% Velocidade (Crescimento Recente)
* **💰 Revenue Score:** Foco em geração de caixa e solidez financeira.
* **👥 Lives Score:** Foco em capilaridade e expansão de mercado.

---

## 📂 Estrutura do Projeto

O projeto segue uma arquitetura modular para facilitar a manutenção e escalabilidade:

```text
/
├── backend/               # Cérebro do sistema
│   ├── analytics/         # Algoritmos (Clustering, Scores, Estatística)
│   ├── services/          # Conexão com Dados e Filtros
│   └── use_cases/         # Regras de Negócio
├── views/                 # Camada Visual (Frontend)
│   ├── components/        # Gráficos, Tabelas, Cards, Header/Footer
│   └── vis_*.py           # Montagem das páginas
├── pages/                 # Rotas da aplicação (Streamlit)
├── assets/                # Imagens e CSS
├── data/                  # Banco de Dados SQLite
└── Dashboard_Estrategico.py # Ponto de Entrada (Main)