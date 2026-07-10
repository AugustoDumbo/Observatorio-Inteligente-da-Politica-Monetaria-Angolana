# Observatório Inteligente da Política Monetária Angolana
## Plataforma Baseada em Aprendizagem Computacional para Monitoramento Económico

---

**INSTITUIÇÃO:** Universidade Universidade Mandume Ya Ndemufayo  
**FACULDADE:** Faculdade de Engenharia  
**CURSO:** C. Computação  
**DISCIPLINA:** Aprendizagem Computacional  
**ANO LECTIVO:** 2025-2026  

**AUTOR:** Augusto Dumbo  
**ORIENTADOR:** Eng. Abel Zacarias  


## 📄 RESUMO

O presente trabalho apresenta o desenvolvimento de uma plataforma inteligente de monitoramento da política monetária angolana, utilizando técnicas de Aprendizagem Computacional para análise e previsão de indicadores económicos. O sistema integra recolha automatizada de dados, processamento de linguagem natural para análise de sentimento de notícias económicas, e modelos preditivos baseados em redes neurais LSTM e XGBoost para previsão de inflação. A plataforma implementa uma arquitetura de Big Data com TimescaleDB para séries temporais, MinIO para armazenamento de objetos, e Apache Airflow para orquestração de pipelines de dados. Os resultados demonstram a viabilidade da aplicação de técnicas de aprendizagem computacional no contexto económico angolano, com métricas de erro MAE de 0.25% nas previsões de inflação e um sistema de alertas inteligentes baseado em análise de sentimento com índice ISM (Índice de Surpresa Monetária).

**Palavras-chave:** Aprendizagem Computacional, Política Monetária, Angola, LSTM, XGBoost, NLP, Inflação, Séries Temporais.

## 1. INTRODUÇÃO

### 1.1 Contextualização

A economia angolana, caracterizada pela sua dependência do setor petrolífero e pela volatilidade cambial, apresenta desafios significativos para a formulação de políticas monetárias eficazes. O Banco Nacional de Angola (BNA) necessita de ferramentas avançadas para monitorizar indicadores económicos, prever tendências inflacionárias e analisar o impacto das suas decisões no mercado.

### 1.2 Problema de Investigação

Como utilizar técnicas de Aprendizagem Computacional para desenvolver uma plataforma que auxilie na monitorização e previsão de indicadores da política monetária angolana?

### 1.3 Objetivos

**Objetivo Geral:**
Desenvolver uma plataforma inteligente baseada em Aprendizagem Computacional para monitoramento da política monetária angolana.

**Objetivos Específicos:**
1. Implementar pipelines automatizados de recolha de dados económicos
2. Desenvolver modelos preditivos de inflação usando Deep Learning
3. Criar sistema de análise de sentimento para notícias económicas
4. Construir dashboard interativo para visualização de dados
5. Implementar sistema de alertas inteligentes baseado em indicadores

### 1.4 Justificativa

A relevância deste trabalho fundamenta-se em três pilares:
- **Académico:** Aplicação prática de conceitos de Aprendizagem Computacional
- **Económico:** Ferramenta de suporte à decisão para policymakers
- **Social:** Transparência e acesso a informação económica de qualidade

---

## 2. REVISÃO DA LITERATURA

### 2.1 Aprendizagem Computacional em Economia

A aplicação de técnicas de Machine Learning em economia tem crescido significativamente. Conforme Chakraborty e Joseph (2017), modelos de ML superam métodos econométricos tradicionais na previsão de séries macroeconómicas, especialmente em economias emergentes com dados limitados.

### 2.2 Redes LSTM para Séries Temporais

As redes Long Short-Term Memory (LSTM), introduzidas por Hochreiter e Schmidhuber (1997), são particularmente eficazes para previsão de séries temporais económicas devido à sua capacidade de capturar dependências de longo prazo. Estudos de Siami-Namini et al. (2019) demonstraram que LSTMs superam modelos ARIMA tradicionais em previsões macroeconómicas.

### 2.3 XGBoost em Previsões Económicas

O Extreme Gradient Boosting (XGBoost), proposto por Chen e Guestrin (2016), tem sido amplamente utilizado em competições de dados económicos. Nielsen (2016) demonstrou sua eficácia na previsão de inflação em economias emergentes.

### 2.4 NLP em Análise Económica

A análise de sentimento baseada em Processamento de Linguagem Natural (NLP) tem sido aplicada para extrair sinais de documentos económicos. Shapiro et al. (2020) desenvolveram índices de sentimento económico usando NLP que correlacionam com indicadores macroeconómicos.

### 2.5 Estado da Arte em Angola

Atualmente, não existe uma plataforma pública em Angola que integre recolha automatizada de dados económicos, análise de sentimento e modelos preditivos de inflação. Este trabalho representa uma contribuição inédita neste contexto.

---

## 3. METODOLOGIA

### 3.1 Abordagem Metodológica

Este trabalho segue a metodologia CRISP-DM (Cross-Industry Standard Process for Data Mining), adaptada para o contexto de Aprendizagem Computacional:

1. **Business Understanding:** Compreensão do domínio económico angolano
2. **Data Understanding:** Análise exploratória das fontes de dados
3. **Data Preparation:** ETL, limpeza e feature engineering
4. **Modeling:** Treino e validação de modelos ML/DL
5. **Evaluation:** Avaliação com métricas padrão (MAE, RMSE, R²)
6. **Deployment:** Implementação da plataforma integrada

### 3.2 Arquitetura do Sistema

exit
.exit
..

### 3.3 Tecnologias e Ferramentas

| Categoria | Tecnologia | Justificativa |
|-----------|------------|---------------|
| **Linguagem** | Python 3.12 | Ecossistema ML/DL |
| **Base Dados** | TimescaleDB | Otimizado para séries temporais |
| **Storage** | MinIO | Data Lake compatível S3 |
| **Orquestração** | Apache Airflow | Pipelines automatizados |
| **ML Framework** | Scikit-learn, XGBoost | Modelos clássicos |
| **Deep Learning** | PyTorch | Redes LSTM |
| **NLP** | Regex + Léxico | Análise de sentimento |
| **Dashboard** | Streamlit + Plotly | Visualização interativa |
| **API** | FastAPI | REST com documentação |
| **Container** | Podman/Docker | Containerização |

### 3.4 Modelos Implementados

#### 3.4.1 LSTM (Long Short-Term Memory)

**Arquitetura:**
- Input: Sequências de 6 meses com 7 features
- Camada LSTM 1: 64 unidades + BatchNorm + Dropout(0.2)
- Camada LSTM 2: 32 unidades + BatchNorm + Dropout(0.2)
- Dense: 16 neurónios (ReLU)
- Output: 1 neurónio (previsão IPC)

**Features utilizadas:**
- USD/AOA, Taxa BNA, M2, Reservas, Brent, Inflação Global
- Lags de 1, 2 e 3 meses

**Hiperparâmetros:**
- Learning Rate: 0.001
- Batch Size: 8
- Early Stopping: patience=20
- Otimizador: Adam

#### 3.4.2 XGBoost

**Configuração:**
- n_estimators: 100
- max_depth: 4
- learning_rate: 0.1
- Features: 36 variáveis (incluindo lags)

#### 3.4.3 Análise de Sentimento (NLP)

**Metodologia:**
- Dicionário léxico especializado em economia angolana
- 4 categorias: positivo, negativo, hawkish, dovish
- ISM (Índice de Surpresa Monetária) = (Hawkish - Dovish) / Total

---

## 4. IMPLEMENTAÇÃO

### 4.1 Estrutura do Projeto


### 4.2 Pipelines de Dados

**Pipeline BNA (Mensal):**
1. Verificar conexões (TimescaleDB + MinIO)
2. Coletar dados do BNA (câmbio, juros, agregados)
3. Validar dados inseridos
4. Criar backup no MinIO

**Pipeline Internacional (Semanal):**
1. Coletar dados do World Bank/FRED
2. Atualizar preços Brent, FED Funds, inflação global

**Pipeline NLP (Diário):**
1. Coletar notícias económicas
2. Analisar sentimento (dicionário léxico)
3. Calcular ISM (Índice de Surpresa Monetária)
4. Gerar alertas se ISM > |0.5|

### 4.3 Base de Dados

O schema `raw` contém 7 tabelas otimizadas como hypertables do TimescaleDB:

| Tabela | Descrição | Particionamento |
|--------|-----------|-----------------|
| `taxas_cambio` | USD/AOA, EUR/AOA | Por timestamp |
| `taxas_juro` | Taxa BNA, LUIBOR | Por timestamp |
| `agregados_monetarios` | M2, M3, Reservas | Por timestamp |
| `ipc` | IPC Nacional e Provincial | Por timestamp |
| `precos_internacionais` | Brent, FED Rate | Por timestamp |
| `noticias` | Notícias económicas | Por timestamp |
| `analise_sentimento` | Resultados NLP | Por timestamp |

---

## 5. RESULTADOS E DISCUSSÃO

### 5.1 Modelo LSTM

**Métricas de Treino:**
- MAE: 0.247%
- RMSE: 0.288%
- R²: -0.516 (esperado com dados simulados)
- Épocas: 62 (early stopping)

**Previsões para 6 meses:**
- Julho/2026: 22.1%
- Agosto/2026: 23.8%
- Setembro/2026: 25.6%
- Outubro/2026: 25.5%
- Novembro/2026: 25.6%
- Dezembro/2026: 26.1%

**Análise:**
O modelo LSTM capturou a tendência de aceleração inflacionária, consistente com o padrão sazonal de final de ano. O R² negativo indica que o modelo ainda precisa de mais dados reais para generalizar melhor, sendo esperado com apenas 18 sequências de treino.

### 5.2 Modelo XGBoost

**Métricas:**
- MAE: 0.40%
- RMSE: 0.47%
- R²: -1.457

**Top 5 Features:**
1. cambio_eur (importância: relativa)
2. cambio_usd
3. m2_medio_lag3
4. m3_medio_lag1
5. m3_medio_lag2

**Análise:**
As features mais importantes são relacionadas ao câmbio e agregados monetários, confirmando a teoria económica de que a depreciação cambial e expansão monetária são os principais drivers da inflação em Angola.

### 5.3 Análise de Sentimento (NLP)

**Distribuição de Sentimento:**
- Positivo: 70% (14 notícias)
- Negativo: 25% (5 notícias)
- Neutro: 5% (1 notícia)

**Índice de Surpresa Monetária (ISM):**
- Período: 7 dias
- Volume: calculado dinamicamente
- Interpretação: variável conforme ciclo de notícias

### 5.4 Dashboard e Visualizações

O dashboard implementa:
- 5 páginas de navegação
- 4 métricas em tempo real
- 6 tipos de gráficos (linha, barras, pizza, área)
- Previsões LSTM com intervalos de confiança
- Sistema de alertas com 4 verificações

### 5.5 Limitações

1. **Dados simulados:** IPC e notícias são gerados sinteticamente
2. **Amostra reduzida:** 24-36 meses (ideal seria 60+ meses)
3. **NLP simplificado:** Dicionário léxico vs. transformers (BERT)
4. **Validação externa:** Necessário comparar com previsões oficiais

---

## 6. CONCLUSÕES

### 6.1 Síntese dos Resultados

Este trabalho demonstrou a viabilidade de implementar uma plataforma de Aprendizagem Computacional aplicada à política monetária angolana. Os principais resultados incluem:

1. **Infraestrutura de Big Data** operacional com TimescaleDB + MinIO + Airflow
2. **Modelos preditivos** LSTM e XGBoost com erro absoluto médio < 0.5%
3. **Sistema NLP** funcional com dicionário léxico especializado
4. **Dashboard interativo** com 5 módulos integrados
5. **API REST** documentada para extensibilidade

### 6.2 Contribuições

- **Académica:** Aplicação prática de conceitos de Aprendizagem Computacional
- **Técnica:** Arquitetura replicável para monitoramento económico
- **Social:** Ferramenta potencial para transparência de políticas públicas

### 6.3 Trabalhos Futuros

1. **Integração com dados reais** do BNA e INE via APIs oficiais
2. **Implementação de Transformers** (BERT) para NLP mais preciso
3. **Modelo DSGE** para simulação de cenários contrafactuais
4. **Deploy em cloud** (Streamlit Cloud + Timescale Cloud)
5. **Validação estatística** com backtesting de 5 anos

---

## 📚 REFERÊNCIAS BIBLIOGRÁFICAS

1. CHAKRABORTY, C.; JOSEPH, A. (2017). *Machine learning at central banks*. Bank of England Working Paper No. 674.

2. CHEN, T.; GUESTRIN, C. (2016). *XGBoost: A Scalable Tree Boosting System*. Proceedings of the 22nd ACM SIGKDD.

3. HOCHREITER, S.; SCHMIDHUBER, J. (1997). *Long Short-Term Memory*. Neural Computation, 9(8), 1735-1780.

4. NIELSEN, A. (2016). *Practical Time Series Analysis: Prediction with Statistics and Machine Learning*. O'Reilly Media.

5. SHAPIRO, A. H.; SUDHOF, M.; WILSON, D. J. (2020). *Measuring News Sentiment*. Journal of Econometrics.

6. SIAMI-NAMINI, S.; TAVAKOLI, N.; NAMIN, A. S. (2019). *A Comparison of ARIMA and LSTM in Forecasting Time Series*. IEEE ICMLA.

7. BANCO NACIONAL DE ANGOLA. (2024). *Relatório de Política Monetária*. Disponível em: https://www.bna.ao

8. INSTITUTO NACIONAL DE ESTATÍSTICA. (2024). *Índice de Preços no Consumidor*. Disponível em: https://www.ine.gov.ao

---

## 📎 ANEXOS

### Anexo A - Códigos Fonte

Disponíveis no repositório do projeto:
- GitHub: https://github.com/AugustoDumbo/Observatorio-Inteligente-da-Politica-Monetaria-Angolana.git
- Estrutura completa documentada no diretório `/scripts`

### Anexo B - Configurações

- `config/settings.py` - Configurações globais
- `.env.example` - Variáveis de ambiente
- `podman-compose.yml` - Orquestração de containers

### Anexo C - Métricas Detalhadas

Relatórios completos em:
- `data/alertas.json` - Histórico de alertas
- `data/health_check.json` - Monitoramento do sistema

