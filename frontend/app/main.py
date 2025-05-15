import streamlit as st
import pandas as pd
from components.visualization import VisualizationFactory
from services.api import APIService
import json

# Configuration de la page
st.set_page_config(
    page_title="Data Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .stTextArea textarea {
        font-size: 1.2rem;
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    .stTextArea textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 1px #4CAF50;
    }
    .stButton button {
        width: 100%;
        font-size: 1.2rem;
        padding: 0.8rem 1.5rem;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Titre de l'application avec style
st.markdown("""
    <h1 style='text-align: center; color: #2c3e50; margin-bottom: 2rem; font-size: 2.5rem;'>
        📊 Assistant d'Analyse de Données
    </h1>
""", unsafe_allow_html=True)

# Initialisation des services
api_service = APIService()
viz_factory = VisualizationFactory()

# Sidebar avec exemples de requêtes
with st.sidebar:
    st.title("💡 Exemples de requêtes")
    
    # Catégories de requêtes
    categories = {
        "📈 Analyse temporelle": [
            "Montrez-moi l'évolution des ventes par mois",
            "Quelle est la tendance des ventes par catégorie?",
            "Comment ont évolué les ventes au cours de l'année?"
        ],
        "📊 Distribution": [
            "Quelle est la distribution des âges des clients?",
            "Comment sont distribués les montants des ventes?",
            "Quelle est la répartition des ventes par catégorie?"
        ],
        "🔄 Comparaison": [
            "Comparez les performances des différents produits",
            "Quelles sont les proportions de ventes par catégorie?",
            "Quel est le produit le plus vendu par catégorie?"
        ],
        "📋 Analyse détaillée": [
            "Quels sont les produits les plus vendus?",
            "Quelle est la moyenne des ventes par catégorie?",
            "Quel est le panier moyen par catégorie?"
        ]
    }
    
    for category, examples in categories.items():
        st.subheader(category)
        for example in examples:
            if st.button(example, key=example):
                st.session_state.prompt = example

# Zone de saisie du prompt avec style amélioré
prompt = st.text_area(
    "Entrez votre demande d'analyse",
    value=st.session_state.get('prompt', ''),
    placeholder="Exemple: 'Montrez-moi l'évolution des ventes par mois' ou 'Quelle est la distribution des âges des clients?'",
    height=100
)

# Bouton d'analyse avec style
if st.button("Analyser", key="analyze_button"):
    if prompt:
        with st.spinner("Analyse en cours..."):
            try:
                # Appel à l'API
                result = api_service.analyze_query(prompt)
                
                # Affichage des données brutes
                st.subheader("📈 Données")
                df = pd.DataFrame(result["data"])
                st.dataframe(df, use_container_width=True)
                
                # Affichage de la requête SQL générée
                with st.expander("Voir la requête SQL générée"):
                    st.code(result["sql_query"], language="sql")
                
                # Création et affichage de la visualisation
                st.subheader("📊 Visualisation")
                fig = viz_factory.create_visualization(
                    result["data"],
                    result["visualization_type"],
                    result["title"]
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Options de téléchargement
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Télécharger les données (CSV)",
                        df.to_csv(index=False).encode('utf-8'),
                        "donnees_analyse.csv",
                        "text/csv"
                    )
                with col2:
                    st.download_button(
                        "📥 Télécharger le graphique (PNG)",
                        fig.to_image(format="png"),
                        "graphique_analyse.png",
                        "image/png"
                    )
                
            except Exception as e:
                st.error(f"Une erreur est survenue: {str(e)}")
    else:
        st.warning("Veuillez entrer une demande d'analyse") 