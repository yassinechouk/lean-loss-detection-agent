# Méthodologie TIMWOODS

## Introduction

**TIMWOODS** est un acronyme mnémotechnique utilisé en **Lean Manufacturing** pour identifier les **8 types de gaspillages** (Muda) dans un système de production.

Cette méthodologie, développée par Taiichi Ohno chez Toyota, permet de détecter et éliminer systématiquement toutes les activités qui consomment des ressources sans créer de valeur pour le client.

## Les 8 Catégories TIMWOODS

### 🚛 T - Transport

**Définition** : Déplacements inutiles de matériaux, produits ou informations qui n'ajoutent pas de valeur au produit final.

**Exemples industriels** :
- Déplacements excessifs de pièces entre postes de travail éloignés
- Multiples manipulations de matériaux avant utilisation
- Flux logistiques non optimisés avec va-et-vient
- Transport vers des zones de stockage intermédiaires inutiles
- Trajets excessifs pour chercher des outils ou composants

**Indicateurs de détection** :
- Distance totale parcourue par les produits
- Nombre de manutentions par pièce
- Temps de transport entre postes
- Coût de la logistique interne
- Nombre de déplacements de chariots/transpalettes

**Comment l'agent détecte** :
- Analyse des descriptions d'événements mentionnant "transport", "déplacement", "manutention"
- Corrélation entre zones de stockage et postes de travail
- Patterns de mouvements répétitifs

---

### 📦 I - Inventory

**Définition** : Stock excédentaire de matières premières, en-cours de production ou produits finis qui immobilise du capital et masque les problèmes.

**Exemples industriels** :
- Sur-stockage de matières premières par précaution
- En-cours excessifs entre postes de travail
- Produits finis stockés avant livraison client
- Pièces obsolètes ou périmées dans les stocks
- Composants commandés en trop grande quantité

**Indicateurs de détection** :
- Taux de rotation des stocks
- Valeur du stock immobilisé
- Nombre de jours de stock disponible
- Taux d'obsolescence
- Espace de stockage utilisé

**Comment l'agent détecte** :
- Descriptions mentionnant "stock", "inventaire", "en-cours"
- Temps d'attente dus à des ruptures ou surstocks
- Analyse des flux de production vs demande

---

### 🏃 M - Motion

**Définition** : Mouvements inutiles des opérateurs qui ne créent pas de valeur ajoutée (gestes inefficaces, déplacements).

**Exemples industriels** :
- Opérateur qui se retourne pour prendre des outils mal positionnés
- Mouvements répétitifs excessifs pour atteindre des composants
- Recherche d'outils ou de documents mal rangés
- Déplacements fréquents vers imprimantes ou armoires éloignées
- Gestes inutiles dans les séquences opératoires

**Indicateurs de détection** :
- Temps de cycle opérateur
- Distance parcourue par l'opérateur
- Nombre de gestes par opération
- Temps de recherche d'outils
- Score d'ergonomie du poste

**Comment l'agent détecte** :
- Mots-clés : "mouvement", "geste", "ergonomie", "recherche"
- Temps de cycle opérateur anormalement élevé
- Problèmes d'ergonomie répétés

---

### ⏳ W - Waiting

**Définition** : Temps d'attente machines, opérateurs ou pièces sans création de valeur (attente de pièces, de décisions, de réglages).

**Exemples industriels** :
- Machine en attente de matière première
- Opérateur en attente d'autorisation de démarrage
- Attente de validation qualité avant passage au poste suivant
- File d'attente devant une machine goulot
- Attente d'informations ou de décisions
- Temps de synchronisation entre postes déséquilibrés

**Indicateurs de détection** :
- Temps d'attente cumulé
- Taux d'utilisation des machines
- Temps de cycle vs temps de valeur ajoutée
- Durée moyenne des files d'attente
- Nombre d'arrêts pour attente

**Comment l'agent détecte** :
- **Micro-arrêts répétitifs** (< 5 min mais fréquents)
- Événements mentionnant "attente", "waiting"
- Temps morts entre opérations
- Goulots identifiés par accumulation d'en-cours

---

### 🔧 O - Over-processing

**Définition** : Opérations, contrôles ou traitements qui dépassent les exigences client et n'ajoutent pas de valeur perçue.

**Exemples industriels** :
- Contrôles qualité redondants ou excessifs
- Finitions ou tolérances plus strictes que nécessaire
- Saisie multiple des mêmes informations
- Rapports détaillés jamais exploités
- Traitements de surface non demandés par le client
- Contrôles à 100% alors qu'un échantillonnage suffirait

**Indicateurs de détection** :
- Nombre de contrôles par pièce
- Temps de contrôle qualité
- Nombre d'opérations vs exigences client
- Taux de sur-qualité
- Temps de traitement administratif

**Comment l'agent détecte** :
- **Événements de type "sur_controle"** dans les données qualité
- Contrôles redondants identifiés
- Temps de process supérieur aux standards

---

### 📊 O - Over-production

**Définition** : Production en quantité supérieure à la demande immédiate ou production trop précoce par rapport aux besoins.

**Exemples industriels** :
- Production par lots trop importants pour lisser la charge
- Fabrication anticipée de pièces non commandées
- Production continue malgré une commande client en attente
- Lancement de séries avant confirmation de commande
- Stocks de sécurité surdimensionnés

**Indicateurs de détection** :
- Taux de rotation des produits finis
- Écart entre production et ventes
- Taille des lots de production
- Délai de fabrication vs délai de livraison
- Stock de produits finis en jours

**Comment l'agent détecte** :
- Stock excessif de produits finis
- Production en avance sur commandes
- Taille de lots disproportionnée

---

### ❌ D - Defects

**Définition** : Rebuts, retouches, non-conformités qui nécessitent du travail supplémentaire et impactent la qualité.

**Exemples industriels** :
- Pièces rebutées pour non-conformité dimensionnelle
- Retouches après contrôle qualité
- Réparations sur produits finis
- Réclamations clients pour défauts
- Tests échoués nécessitant un re-travail
- Dérogations qualité fréquentes

**Indicateurs de détection** :
- Taux de rebut
- Taux de retouche
- Nombre de non-conformités
- Coût de la non-qualité
- Taux de réclamation client
- First Pass Yield (FPY)

**Comment l'agent détecte** :
- **Événements qualité** : rebut, retouche, non_conformite
- Corrélation machine/défaut
- Tendance croissante des rebuts

---

### 💡 S - Skills

**Définition** : Sous-utilisation du potentiel humain : compétences, créativité, idées d'amélioration ignorées.

**Exemples industriels** :
- Opérateurs qualifiés affectés à des tâches simples
- Suggestions d'amélioration non écoutées
- Formation insuffisante sur les nouveaux équipements
- Polyvalence inexploitée
- Absence d'implication dans la résolution de problèmes
- Expertise métier non valorisée dans les projets d'amélioration

**Indicateurs de détection** :
- Taux de participation aux groupes d'amélioration
- Nombre de suggestions d'amélioration déposées
- Écart entre compétences disponibles et utilisées
- Heures de formation par opérateur
- Taux de polyvalence
- Turnover du personnel qualifié

**Comment l'agent détecte** :
- Problèmes liés aux shifts (compétences variables)
- Erreurs opérateur répétées
- Temps de formation insuffisant
- Manque de standardisation

---

## Comment utiliser TIMWOODS

### 1. Observation du terrain (Gemba Walk)
Aller sur le terrain pour observer les processus réels, pas théoriques.

### 2. Cartographie de la chaîne de valeur (VSM)
Documenter chaque étape du processus et identifier où se trouvent les gaspillages.

### 3. Quantification de l'impact
Estimer le coût de chaque type de gaspillage identifié.

### 4. Priorisation
Utiliser la matrice Impact/Effort pour prioriser les actions.

### 5. Plan d'action
Mettre en place des actions d'amélioration ciblées par catégorie.

## Outils Lean associés

| Gaspillage | Outils Lean recommandés |
|------------|-------------------------|
| Transport | Value Stream Mapping, Implantation en flux |
| Inventory | Kanban, Just-in-Time (JIT) |
| Motion | 5S, Ergonomie, MTM |
| Waiting | SMED, TPM, Équilibrage de ligne |
| Over-processing | Analyse de la valeur, Standardisation |
| Over-production | Production tirée (Pull), Takt time |
| Defects | Poka-Yoke, SPC, Jidoka |
| Skills | Kaizen, Formation, Polyvalence |

## Références bibliographiques

1. **Taiichi Ohno** - "Toyota Production System: Beyond Large-Scale Production" (1988)
2. **Jeffrey Liker** - "The Toyota Way" (2004)
3. **James Womack & Daniel Jones** - "Lean Thinking" (1996)
4. **Mike Rother** - "Toyota Kata" (2009)

## Pour aller plus loin

- 🎯 **5S** : Méthode d'organisation de l'espace de travail
- 🔄 **PDCA** : Plan-Do-Check-Act pour l'amélioration continue
- 📊 **Six Sigma** : Méthodologie complémentaire axée sur la réduction de variabilité
- 🤖 **Jidoka** : Automatisation intelligente avec arrêt automatique
- 🔧 **TPM** : Maintenance Productive Totale
