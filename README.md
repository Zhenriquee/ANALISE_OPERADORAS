# 🏥 Health Market Vision (HMV)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-ff4b4b?style=for-the-badge&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-Data_Warehouse-003B57?style=for-the-badge&logo=sqlite)
![Pandas](https://img.shields.io/badge/Pandas-ETL_&_Analytics-150458?style=for-the-badge&logo=pandas)
![Pandera](https://img.shields.io/badge/Pandera-Data_Contracts-green?style=for-the-badge)

**Health Market Vision** é uma plataforma de Inteligência de Mercado (Market Intelligence) projetada para analisar, comparar e prever tendências no setor de Saúde Suplementar do Brasil (ANS).

O sistema processa dados públicos da Agência Nacional de Saúde Suplementar, aplicando algoritmos de normalização proprietários (Power Score, Revenue Score) para permitir a comparação justa entre operadoras de diferentes portes.

---

## 🚀 Funcionalidades Principais

### 📊 Inteligência de Negócios
- **Panorama Estratégico:** Visão macro do mercado com rankings dinâmicos e identificação de líderes.
- **Diagnóstico 360º:** Dossiê completo de qualquer operadora (Financeiro, Operacional, Cadastral).
- **Benchmarking Competitivo:** Comparação "Head-to-Head" entre operadoras com gráficos de radar.
- **Brand Intelligence:** Algoritmo capaz de agrupar operadoras por conglomerados econômicos (ex: Sistema Unimed, Grupo Hapvida-GNDI) para análise consolidada.
- **Movimentação de Mercado:** Monitoramento de M&A (Fusões e Aquisições), novos entrantes e operadoras que deixaram o mercado (solvência).

### 🤖 Ciência de Dados
- **Clustering (K-Means):** Segmentação automática de operadoras em grupos estratégicos baseados em comportamento financeiro e operacional.
- **Análise de Correlação:** Matriz estatística para identificar alavancas de crescimento.

---

## 🏗️ Arquitetura Técnica

O projeto segue rigorosamente os princípios de **Clean Architecture** e **Engenharia de Software Moderna**, garantindo escalabilidade, testabilidade e manutenibilidade.

### Destaques de Engenharia
1.  **Modularidade em Camadas:**
    - **Views:** Componentes de UI isolados e reutilizáveis (Polimorfismo para renderização de KPIs).
    - **Use Cases:** Regras de negócio puras, orquestrando o fluxo de dados.
    - **Core Services:** Motores de processamento desacoplados da infraestrutura.
    - **Infrastructure:** Conectores de banco de dados e gestão de arquivos.

2.  **Padrões de Projeto (Design Patterns):**
    - **Repository Pattern:** Abstração da camada de dados. O sistema não sabe se está acessando SQLite ou Snowflake, facilitando migrações futuras.
    - **Dependency Injection:** Inversão de controle onde as dependências são injetadas no `app.py` (Composition Root), facilitando testes unitários.
    - **Factory & Strategy:** Utilizados para seleção dinâmica de algoritmos de cálculo.

3.  **Performance & Otimização:**
    - **SQL Push-down Predicates:** Filtros temporais e de escopo são aplicados diretamente no banco de dados via queries parametrizadas (`.sql`), reduzindo drasticamente o uso de memória RAM e tráfego de I/O.
    - **Pandas Vectorization:** Transformações de dados otimizadas utilizando operações vetoriais nativas (C-level).

4.  **Qualidade de Dados (Data Quality):**
    - **Data Contracts (Pandera):** Validação de Schema em tempo de execução (Runtime). O sistema garante que os dados entregues ao dashboard respeitam tipos e restrições de negócio, prevenindo erros silenciosos.
    - **Logging Estruturado:** Sistema de logs robusto para rastreabilidade de execução.

---

## 📂 Estrutura do Projeto

```text
HEALTH_MARKET_VISION/
├── app.py                   # Entry Point & Composition Root
├── backend/
│   ├── analytics/           # Algoritmos de Ciência de Dados e Brand Intelligence
│   ├── processing/          # Lógica Pura de Transformação (Pandas)
│   ├── services/            # Orquestradores (DataEngine, FilterService)
│   ├── use_cases/           # Regras de Negócio Específicas (Clean Arch)
│   ├── config.py            # Configuração Centralizada
│   ├── constants.py         # Constantes de Colunas (No Magic Strings)
│   ├── contracts.py         # Contratos de Dados (Pandera Schemas)
│   ├── interfaces.py        # Protocolos e Interfaces
│   ├── logger.py            # Configuração de Logs
│   └── repository.py        # Implementação do Repositório
├── data/                    # Banco de Dados SQLite
├── infra/                   # Conectores de Infraestrutura (DB Connector)
├── queries/                 # SQL Puro (Separado do Código)
│   ├── etl/                 # Queries de Carga Pesada
│   └── filtros/             # Queries de Listagem
├── views/                   # Interface do Usuário (Streamlit)
│   ├── components/          # Componentes Reutilizáveis (Cards, Gráficos)
│   └── styles.py            # CSS e Estilização
└── requirements.txt         # Dependências do Projeto

⚙️ Instalação e Execução
Pré-requisitos
Python 3.10 ou superior.

Passo a Passo
Clone o repositório:

Bash

git clone [https://github.com/seu-usuario/health-market-vision.git](https://github.com/seu-usuario/health-market-vision.git)
cd health-market-vision
Crie um ambiente virtual (Recomendado):

Bash

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
Instale as dependências:

Bash

pip install -r requirements.txt
Execute a aplicação:

Bash

streamlit run app.py
📐 Metodologia de Cálculo (Resumo)
O sistema utiliza metodologias proprietárias para análise justa:

Normalização Logarítmica (Log1p): Reduz a distorção entre operadoras gigantes e pequenas.

Power Score: Métrica composta que avalia Volume de Vidas (40%), Volume Financeiro (40%) e Velocidade de Crescimento (20%).

Brand Grouping: Algoritmo heurístico que identifica grupos econômicos baseando-se em Razão Social e ID ANS, normalizando nomes como "Unimed Rio" e "Central Nacional Unimed" sob a mesma marca.

📄 Licença
Este projeto é proprietário e desenvolvido para fins de Inteligência de Mercado.

Desenvolvido com Engenharia de Dados Avançada.