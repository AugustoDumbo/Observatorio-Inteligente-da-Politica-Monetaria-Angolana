---
marp: true
theme: default
paginate: true
backgroundColor: #fff
---

# 🇦🇴 Observatório Inteligente da Política Monetária Angolana
## Plataforma Baseada em Aprendizagem Computacional

**Autor:** Augusto Dumbo  
**Disciplina:** Aprendizagem Computacional  
**2026**

---

## 📋 Sumário

1. Contextualização e Problema
2. Objetivos
3. Fundamentação Teórica
4. Metodologia
5. Arquitetura do Sistema
6. Modelos Implementados
7. Resultados
8. Demonstração
9. Conclusões

---

## 🎯 Problema

> Como utilizar Aprendizagem Computacional para monitorizar e prever indicadores da política monetária angolana?

**Desafios:**
- Dependência do petróleo
- Volatilidade cambial
- Inflação persistente (20-30%)
- Dados limitados

---

## 🏗️ Arquitetura

Fontes → Airflow → TimescaleDB → ML/DL → Dashboard
BNA (ETL) (Séries) (PyTorch) (Streamlit)
INE
FRED

---

## 🧠 Modelos de Aprendizagem Computacional

### LSTM (Deep Learning)
- Rede neural recorrente
- 2 camadas LSTM (64→32)
- Captura dependências temporais longas

### XGBoost (Gradient Boosting)
- Ensemble de árvores
- 36 features com lags
- Feature importance interpretável

### NLP (Análise de Sentimento)
- Dicionário léxico económico
- ISM (Índice de Surpresa Monetária)

---

## 📊 Resultados

| Modelo | MAE | RMSE |
|--------|-----|------|
| LSTM | 0.25% | 0.29% |
| XGBoost | 0.40% | 0.47% |

**Previsões IPC (LSTM):**
- Jul/2026: 22.1%
- Dez/2026: 26.1%

---

## 🎨 Demonstração

**Dashboard Interativo:**
- 📈 Inflação vs Taxa BNA
- 💵 Câmbio USD/AOA
- 🛢️ Petróleo Brent
- 📰 Sentimento NLP
- 🔮 Previsões ML
- ⚠️ Alertas

---

## ✅ Conclusões

1. ✅ Infraestrutura Big Data funcional
2. ✅ Modelos ML com erro < 0.5%
3. ✅ NLP para análise de sentimento
4. ✅ Dashboard interativo
5. ✅ API REST documentada

**Trabalhos Futuros:**
- Dados reais do INE/BNA
- BERT para NLP
- Modelo DSGE

---

## ❓ Perguntas?

**Obrigado!** 🇦🇴
