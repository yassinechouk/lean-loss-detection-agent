# 🏭 Agent IA – Détection des Pertes Lean Invisibles

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Agent d'intelligence artificielle multi-étapes pour la détection, la classification et l'analyse des pertes Lean invisibles dans les systèmes industriels, basé sur LangChain et LangGraph.

## 📋 Table des matières

- [Description](#-description)
- [Architecture](#-architecture)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Données](#-données)
- [Technologies](#-technologies)
- [Roadmap](#-roadmap)
- [Licence](#-licence)

## 🎯 Description

Dans un environnement industriel, de nombreuses pertes restent **invisibles** aux indicateurs classiques (TRS, taux de rebut, etc.). Ces pertes — micro-arrêts, attentes organisationnelles, sur-contrôle, retouches répétitives — impactent fortement la performance sans être détectées par les outils traditionnels.

Cet agent IA analyse les données de production et de qualité pour :

1. **Détecter** les pertes cachées dans les logs de production
2. **Classifier** selon la typologie Lean **TIMWOODS**
3. **Analyser** les causes racines par raisonnement multi-étapes
4. **Recommander** des actions d'amélioration concrètes et priorisées

### Qu'est-ce que TIMWOODS ?

| Lettre | Catégorie | Description |
|--------|-----------|-------------|
| **T** | Transport | Déplacements inutiles de matériaux |
| **I** | Inventaire | Stock excédentaire |
| **M** | Mouvement | Mouvements inutiles des opérateurs |
| **W** | Waiting | Attentes (machines, pièces, décisions) |
| **O** | Over-processing | Sur-qualité, contrôles excessifs |
| **O** | Over-production | Production au-delà de la demande |
| **D** | Defects | Défauts, rebuts, retouches |
| **S** | Skills | Sous-utilisation des compétences humaines |

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│              Interface Utilisateur                │
│           (Streamlit Dashboard)                   │
└────────────────────┬─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│           LangGraph Orchestration                 │
│                                                   │
│  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │  Parsing │──▶│ Analysis  │──▶│Recommendation│  │
│  │  Agent   │  │  Agent    │  │    Agent      │  │
│  └──────────┘  └───────────┘  └───────────────┘  │
│       │              │               │            │
│       ▼              ▼               ▼            │
│  Extraction    Classification   Plan d'action     │
│  des pertes     TIMWOODS       & priorisation     │
└────────────────────┬─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│              Couche de Données                    │
│                                                   │
│  📄 Logs d'arrêts    📊 Données qualité          │
│  📋 Rapports          🔧 Données synthétiques     │
└──────────────────────────────────────────────────┘
```

## ✨ Fonctionnalités

- 🔍 **Détection automatique** des micro-arrêts et pertes cachées
- 📊 **Classification TIMWOODS** intelligente par LLM
- 🧠 **Analyse de causes racines** par raisonnement multi-étapes (5 Pourquoi, Ishikawa)
- 💡 **Recommandations** d'amélioration priorisées par impact et faisabilité
- 📈 **Dashboard interactif** avec visualisations Plotly
- 🗃️ **Données synthétiques** réalistes pour démonstration et tests
- 🔄 **Architecture modulaire** extensible via LangGraph

## 🚀 Installation

### Prérequis

- Python 3.10+
- Clé API OpenAI (ou compatible)

### Étapes

```bash
# 1. Cloner le repository
git clone https://github.com/yassinechouk/lean-loss-detection-agent.git
cd lean-loss-detection-agent

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditez .env avec votre clé API OpenAI

# 5. Générer les données synthétiques
python -m src.data.synthetic_generator

# 6. Lancer l'application
streamlit run app.py
```

## 💻 Utilisation

### En ligne de commande

```python
from src.agents.graph import LeanLossDetectionGraph
from src.data.loader import DataLoader

# Charger les données
loader = DataLoader("data/synthetic/production_logs.csv")
data = loader.load()

# Initialiser et exécuter l'agent
agent = LeanLossDetectionGraph()
results = agent.run(data)

# Afficher les résultats
for loss in results["detected_losses"]:
    print(f"  Catégorie: {loss['timwoods_category']}")
    print(f"  Impact: {loss['estimated_impact']}")
    print(f"  Actions: {loss['recommendations']}")
```

### Via le Dashboard

```bash
streamlit run app.py
```

Accédez à `http://localhost:8501` pour utiliser l'interface interactive.

## 📁 Structure du projet

```
lean-loss-detection-agent/
├── app.py                          # Point d'entrée Streamlit
├── requirements.txt                # Dépendances Python
├── pyproject.toml                  # Configuration du projet
├── .env.example                    # Variables d'environnement template
├── LICENSE                         # Licence MIT
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── agents/                     # Agents LangChain/LangGraph
│   │   ├── __init__.py
│   │   ├── graph.py                # Orchestration LangGraph
│   │   ├── parser_agent.py         # Agent d'extraction des pertes
│   │   ├── analyzer_agent.py       # Agent d'analyse TIMWOODS
│   │   └── recommender_agent.py    # Agent de recommandations
│   ├── models/                     # Modèles de données
│   │   ├── __init__.py
│   │   ├── schemas.py              # Schémas Pydantic
│   │   └── timwoods.py             # Définitions TIMWOODS
│   ├── data/                       # Gestion des données
│   │   ├── __init__.py
│   │   ├── loader.py               # Chargement des données
│   │   ├── preprocessor.py         # Prétraitement
│   │   └── synthetic_generator.py  # Générateur de données
│   ├── prompts/                    # Templates de prompts
│   │   ├── __init__.py
│   │   └── templates.py            # Prompts des agents
│   ├── utils/                      # Utilitaires
│   │   ├── __init__.py
│   │   └── config.py               # Configuration globale
│   └── visualization/              # Visualisations
│       ├── __init__.py
│       └── charts.py               # Graphiques Plotly
│
├── data/
│   ├── synthetic/                  # Données synthétiques générées
│   └── examples/                   # Exemples de données
│
├── tests/                          # Tests unitaires et intégration
│   ├── __init__.py
│   ├── test_parser_agent.py
│   ├── test_analyzer_agent.py
│   ├── test_recommender_agent.py
│   └── test_data_loader.py
│
├── notebooks/                      # Notebooks Jupyter
│   ├── 01_data_exploration.ipynb
│   ├── 02_agent_testing.ipynb
│   └── 03_results_analysis.ipynb
│
└── docs/                           # Documentation
    ├── architecture.md
    ├── timwoods_methodology.md
    └── user_guide.md
```

## 📊 Données

Le projet utilise des **données synthétiques réalistes** simulant un environnement de production industrielle :

- **Logs de production** : arrêts machines, temps de cycle, micro-arrêts
- **Données qualité** : rebuts, retouches, contrôles
- **Rapports d'incidents** : pannes, anomalies, observations

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| Agents IA | LangChain, LangGraph |
| LLM | OpenAI GPT-4 (configurable) |
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly, Streamlit |
| Validation | Pydantic |
| Tests | Pytest |
| Environnement | Python 3.10+ |

## 📈 Roadmap

- [x] Architecture de base LangGraph
- [x] Générateur de données synthétiques
- [x] Agent Parser (extraction des pertes)
- [x] Agent Analyzer (classification TIMWOODS)
- [x] Agent Recommender (plan d'action)
- [x] Dashboard Streamlit
- [ ] Intégration données MES/ERP réelles
- [ ] Export PDF des rapports
- [ ] Mode temps réel (streaming)
- [ ] API REST

## 👤 Auteur

**Yassine Chouk** — [@yassinechouk](https://github.com/yassinechouk)

---

*Projet académique — Intelligence Artificielle & Performance Industrielle*
