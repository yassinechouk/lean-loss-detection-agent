# Guide Utilisateur

## 🚀 Démarrage rapide

### Installation

#### 1. Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- (Optionnel) Clé API OpenAI pour le mode LLM

#### 2. Cloner le repository
```bash
git clone https://github.com/yassinechouk/lean-loss-detection-agent.git
cd lean-loss-detection-agent
```

#### 3. Créer un environnement virtuel
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

#### 5. Configuration
Copier le fichier d'exemple de configuration :
```bash
cp .env.example .env
```

Éditer le fichier `.env` avec vos paramètres :
```bash
# Clé API OpenAI (optionnel)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Modèle LLM (si clé API fournie)
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.2

# Chemins des données
DATA_DIR=data/synthetic
OUTPUT_DIR=data/output
```

#### 6. Générer les données synthétiques
```bash
python -m src.data.synthetic_generator
```

#### 7. Lancer l'application
```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : **http://localhost:8501**

---

## 🎯 Utilisation du Dashboard

### Page d'accueil

Au lancement, vous voyez la page d'accueil avec :
- 👋 Message de bienvenue
- 📋 Description des fonctionnalités
- 🚀 Instructions de démarrage
- 📊 Aperçu des données synthétiques

### Sidebar

La sidebar (à gauche) contient :

#### ⚙️ Configuration
- Statut de la clé API (✅ configurée ou ⚠️ mode heuristique)
- Modèle LLM utilisé
- Température du modèle

#### 📁 Données
- **Option 1** : Utiliser les données synthétiques (par défaut)
- **Option 2** : Uploader vos propres fichiers CSV
  - `production_logs.csv`
  - `quality_records.csv`
  - `incident_reports.csv`

#### 🚀 Lancement
- Bouton **"Lancer l'analyse"** pour démarrer

### Lancement de l'analyse

1. Cliquez sur **🚀 Lancer l'analyse**
2. Patientez pendant :
   - 🔄 Chargement des données (~2s)
   - 🧠 Analyse en cours (~10-30s selon le mode)
3. ✅ Une fois terminé, les résultats s'affichent dans 5 onglets

---

## 📊 Onglets du Dashboard

### 1. 📊 Vue d'ensemble

**KPIs principaux** (4 métriques) :
- 🔍 **Pertes détectées** : Nombre total de pertes identifiées
- 💰 **Coût estimé** : Impact financier total en EUR
- 💡 **Recommandations** : Nombre d'actions proposées (+ quick wins)
- 📈 **Gain potentiel** : Économies estimées + ROI %

**Graphiques** :
- **Distribution TIMWOODS** : Barres colorées par catégorie
- **Timeline des pertes** : Top 15 par fréquence

### 2. 🔍 Pertes détectées

**Filtres disponibles** :
- Par catégorie TIMWOODS (Toutes / Transport / Inventory / ...)
- Par sévérité (Toutes / critical / high / medium / low)
- Tri (Coût / Fréquence / Sévérité)

**Affichage** :
- Liste expandable de toutes les pertes
- Pour chaque perte :
  - ✏️ Titre et catégorie TIMWOODS
  - 📊 Métriques : Fréquence, Durée, Coût
  - 📝 Description détaillée
  - 🔧 Machines et lignes concernées
  - 📈 Score de confiance (0-100%)

### 3. 🧠 Analyse des causes

**Contenu** :
- Pour chaque perte majeure :
  - 🎯 **Catégorie TIMWOODS** avec justification
  - 🔄 **Méthode des 5 Pourquoi** :
    - Pourquoi 1 ? → Cause immédiate
    - Pourquoi 2 ? → ...
    - Pourquoi 5 ? → Cause racine
  - 🎯 **Cause racine identifiée**
  - 📋 **Facteurs contributifs**

### 4. 💡 Recommandations

**Matrice Effort/Impact** :
- Scatter plot interactif
- Bulles colorées par priorité (P1 à P5)
- Taille proportionnelle au gain
- Quadrants :
  - ✨ **Quick Wins** (faible effort, fort gain)
  - 🎯 **Projets majeurs** (fort effort, fort gain)

**Liste des recommandations** :
Groupées par priorité (1 = haute, 5 = basse)

Pour chaque recommandation :
- ✏️ Titre et département responsable
- 📝 Description détaillée de l'action
- 📊 Métriques :
  - 💰 Gain estimé (EUR)
  - 🎯 Effort (low/medium/high)
  - ⏱️ Timeline (semaines)
  - 🔢 Priorité (1-5)

### 5. 📈 Statistiques

**Graphiques détaillés** :
- 🔥 **Heatmap Sévérité** : Matrice catégorie × sévérité
- 📊 **Pareto des coûts** : Top 10 + courbe de cumul

**Statistiques résumées** :
- Distribution TIMWOODS (nombre par catégorie)
- Distribution Sévérité (critical/high/medium/low)
- Métriques clés (coût total, ROI, quick wins)

**Export** :
- 💾 Bouton "Télécharger le rapport JSON"
- Format JSON complet avec toutes les données

---

## 🔧 Mode Heuristique (sans API)

### Pourquoi ?
Si vous n'avez pas de clé API OpenAI ou souhaitez un mode plus rapide.

### Comment ça marche ?
L'agent utilise des **règles statistiques** au lieu d'un LLM :

#### Parser Heuristic
| Condition | Perte détectée |
|-----------|----------------|
| Micro-arrêts > 30 | Perte "Waiting" |
| Temps d'arrêt > 8h | Perte majeure |
| Rebuts > 30 | Perte "Defects" |
| Sur-contrôle > 15 | Perte "Over-processing" |
| Shift nuit problématique | Perte "Skills" |

#### Analyzer Heuristic
- Classification par **mots-clés** (attente → Waiting, rebut → Defects)
- 5 Pourquoi **génériques** par catégorie TIMWOODS
- Estimation coût : `durée × taux horaire`

#### Recommender Heuristic
- **Templates** de recommandations par catégorie
- Priorisation selon sévérité
- Gains estimés : pourcentage du coût de la perte

### Activation
Automatique si :
- Pas de `OPENAI_API_KEY` dans `.env`
- Erreur de connexion à l'API OpenAI

Vous verrez dans la sidebar : **⚠️ Pas de clé API - Mode heuristique activé**

---

## 📁 Format des fichiers CSV

Si vous souhaitez utiliser vos propres données, voici les formats requis :

### production_logs.csv
```csv
timestamp,machine_id,event_type,duration_minutes,description,line_id,operator_id,shift
2024-01-15T10:30:00,CNC-01,micro_arret,3.5,Bourrage convoyeur,L1,OP001,matin
2024-01-15T11:00:00,CNC-01,arret,25.0,Changement de série,L1,OP001,matin
```

**Colonnes requises** :
- `timestamp` : ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
- `machine_id` : Identifiant machine (ex: CNC-01, PRESS-01)
- `event_type` : `arret`, `micro_arret`, `ralentissement`, `normal`
- `duration_minutes` : Durée en minutes (float)
- `description` : Description de l'événement
- `line_id` : Ligne de production (ex: L1, L2)
- `operator_id` : ID opérateur (optionnel)
- `shift` : `matin`, `apres-midi`, `nuit`

### quality_records.csv
```csv
timestamp,product_id,defect_type,quantity,severity,description,machine_id,line_id
2024-01-15T11:00:00,PROD1234,rebut,5,high,Dimension hors tolérance,CNC-01,L1
```

**Colonnes requises** :
- `timestamp` : ISO 8601
- `product_id` : Référence produit
- `defect_type` : `rebut`, `retouche`, `sur_controle`, `non_conformite`
- `quantity` : Nombre de pièces (int)
- `severity` : `low`, `medium`, `high`, `critical`
- `description` : Description du défaut
- `machine_id` : Machine concernée
- `line_id` : Ligne de production

### incident_reports.csv
```csv
timestamp,incident_id,category,description,impact_level,resolution_time_hours,root_cause,machine_id,line_id
2024-01-15T12:00:00,INC0001,panne_mecanique,Rupture courroie,3,2.5,Usure normale,CNC-01,L1
```

**Colonnes requises** :
- `timestamp` : ISO 8601
- `incident_id` : ID unique (ex: INC0001)
- `category` : `panne_mecanique`, `panne_electrique`, `defaut_qualite`, `probleme_logistique`, `erreur_operateur`
- `description` : Description de l'incident
- `impact_level` : 1 à 5 (int)
- `resolution_time_hours` : Temps de résolution (float)
- `root_cause` : Cause racine identifiée
- `machine_id` : Machine concernée
- `line_id` : Ligne de production

---

## ❓ FAQ

### Q1 : L'analyse est-elle précise sans clé API ?
**R :** Oui ! Le mode heuristique utilise des règles éprouvées basées sur des seuils statistiques. Il est moins contextuel que le mode LLM mais tout à fait utilisable.

### Q2 : Puis-je utiliser mes propres données ?
**R :** Oui, uploadez vos fichiers CSV au format spécifié ci-dessus via la sidebar.

### Q3 : Les données synthétiques sont-elles réalistes ?
**R :** Oui, elles incluent des patterns intentionnels (ex: CNC-01 avec 3x plus de micro-arrêts) pour simuler un environnement industriel réel.

### Q4 : Comment exporter les résultats ?
**R :** Allez dans l'onglet "📈 Statistiques" et cliquez sur "Télécharger le rapport JSON".

### Q5 : Combien de temps prend l'analyse ?
**R :** 
- Mode LLM : ~20-30 secondes
- Mode heuristique : ~5-10 secondes

### Q6 : Puis-je modifier les seuils heuristiques ?
**R :** Oui, modifiez les fichiers dans `src/agents/` (parser_agent.py, analyzer_agent.py, recommender_agent.py).

### Q7 : Comment améliorer la précision du mode LLM ?
**R :** 
- Utilisez GPT-4 (meilleur que GPT-3.5)
- Ajustez la température (0.2 = déterministe, 0.8 = créatif)
- Fournissez plus de contexte dans les descriptions

### Q8 : L'application est-elle sécurisée ?
**R :** 
- ✅ Toutes les données restent locales
- ✅ Clé API stockée uniquement dans `.env` (non versionnée)
- ✅ Pas d'envoi de données vers des serveurs tiers (sauf OpenAI API si configuré)

---

## 🐛 Résolution de problèmes

### Erreur : "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur : "FileNotFoundError: data/synthetic/..."
```bash
# Régénérer les données synthétiques
python -m src.data.synthetic_generator
```

### Erreur OpenAI API
```bash
# Vérifier la clé API dans .env
cat .env | grep OPENAI_API_KEY

# Le mode heuristique sera automatiquement activé
```

### Streamlit ne démarre pas
```bash
# Vérifier l'installation de Streamlit
pip install --upgrade streamlit

# Vérifier les ports
streamlit run app.py --server.port 8502
```

### Performances lentes
```bash
# Utiliser le mode heuristique (plus rapide)
# Ou réduire la température du LLM (plus déterministe = plus rapide)
LLM_TEMPERATURE=0.1
```

---

## 📞 Support

- 📧 Email : yassine.chouk@insat.ucar.tn
- 🐛 Issues GitHub : [github.com/yassinechouk/lean-loss-detection-agent/issues](https://github.com/yassinechouk/lean-loss-detection-agent/issues)
- 📖 Documentation complète : Voir `/docs`

---

## 🎓 Ressources complémentaires

### Lean Manufacturing
- 📚 "The Toyota Way" - Jeffrey Liker
- 📚 "Lean Thinking" - Womack & Jones
- 🎥 [Toyota Production System](https://www.youtube.com/results?search_query=toyota+production+system)

### LangChain & LangGraph
- 📖 [Documentation LangChain](https://python.langchain.com/)
- 📖 [Documentation LangGraph](https://langchain-ai.github.io/langgraph/)
- 🎥 [Tutoriels LangChain](https://www.youtube.com/results?search_query=langchain+tutorial)

### Streamlit
- 📖 [Documentation Streamlit](https://docs.streamlit.io/)
- 🎨 [Galerie d'applications](https://streamlit.io/gallery)
