import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Data Analysis Assistant",
    page_icon="📊",
    layout="wide"
)

# Titre de l'application
st.title("📊 Assistant d'Analyse de Données")

# Zone de saisie du prompt
prompt = st.text_area(
    "Entrez votre demande d'analyse",
    placeholder="Exemple: 'Montrez-moi l'évolution des ventes par mois' ou 'Quelle est la distribution des âges des clients?'",
    height=100
)

def create_visualization(data, viz_type, title):
    df = pd.DataFrame(data)
    
    if viz_type == "line":
        fig = px.line(df, title=title)
    elif viz_type == "bar":
        fig = px.bar(df, title=title)
    elif viz_type == "histogram":
        fig = px.histogram(df, title=title)
    elif viz_type == "pie":
        fig = px.pie(df, title=title)
    else:
        fig = px.bar(df, title=title)  # Par défaut
    
    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        title_font_size=20
    )
    return fig

if st.button("Analyser"):
    if prompt:
        with st.spinner("Analyse en cours..."):
            try:
                # Appel à l'API backend
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"prompt": prompt}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Affichage des données brutes
                    st.subheader("Données")
                    st.dataframe(pd.DataFrame(result["data"]))
                    
                    # Création et affichage de la visualisation
                    st.subheader("Visualisation")
                    fig = create_visualization(
                        result["data"],
                        result["visualization_type"],
                        result["title"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Erreur lors de l'analyse des données")
            except Exception as e:
                st.error(f"Une erreur est survenue: {str(e)}")
    else:
        st.warning("Veuillez entrer une demande d'analyse")

# Ajout d'exemples de requêtes
st.sidebar.title("Exemples de requêtes")
st.sidebar.markdown("""
- Montrez-moi l'évolution des ventes par mois
- Quelle est la distribution des âges des clients?
- Quelles sont les proportions de ventes par catégorie?
- Comparez les performances des différents produits
""") 