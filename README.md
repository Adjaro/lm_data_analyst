# Assistant d'Analyse de Données

Cette application permet d'analyser des données en langage naturel et de générer automatiquement des visualisations pertinentes.

## Fonctionnalités

- Interface utilisateur intuitive avec Streamlit
- Analyse de requêtes en langage naturel
- Génération automatique de requêtes SQL
- Visualisations interactives avec Plotly
- Support pour différents types de graphiques (lignes, barres, histogrammes, camemberts)

## Prérequis

- Docker et Docker Compose
- Une clé API Mistral (https://mistral.ai)

## Installation et Déploiement

### Option 1 : Déploiement avec Docker (Recommandé)

1. Clonez ce dépôt
2. Créez un fichier `.env` à la racine du projet avec votre clé API Mistral :
```
MISTRAL_API_KEY=votre_clé_api
```

3. Construisez et démarrez les conteneurs :
```bash
docker-compose up --build
```

4. L'application sera accessible aux adresses suivantes :
   - Frontend : http://localhost:8501
   - Backend API : http://localhost:8000

### Option 2 : Installation Manuelle

1. Clonez ce dépôt
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet avec votre clé API Mistral :
```
MISTRAL_API_KEY=votre_clé_api
```

4. Initialisez la base de données :
```bash
cd data
sqlite3 analytics.db < init.sql
```

5. Démarrez le backend FastAPI :
```bash
cd backend
uvicorn main:app --reload
```

6. Dans un autre terminal, démarrez le frontend Streamlit :
```bash
cd frontend
streamlit run app.py
```

## Structure du Projet

```
.
├── backend/
│   ├── Dockerfile
│   └── main.py
├── frontend/
│   ├── Dockerfile
│   └── app.py
├── data/
│   ├── init.sql
│   └── analytics.db
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Utilisation

1. Entrez votre demande d'analyse en langage naturel dans la zone de texte
2. Cliquez sur "Analyser"
3. Consultez les données et la visualisation générées

## Exemples de requêtes

- "Montrez-moi l'évolution des ventes par mois"
- "Quelle est la distribution des âges des clients?"
- "Quelles sont les proportions de ventes par catégorie?"
- "Comparez les performances des différents produits" 