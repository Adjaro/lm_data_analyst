import streamlit as st
import pandas as pd
from datetime import datetime
from app.components.visualization import VisualizationFactory
from app.components.history import QueryHistory
from app.components.examples import QueryExamples
from app.components.styles import Styles
from app.services.api import APIService
from typing import Optional

def initialize_session_state() -> None:
    """Initialise les variables de session."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'page_size' not in st.session_state:
        st.session_state.page_size = 10
    if 'last_error' not in st.session_state:
        st.session_state.last_error = None
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False

def render_sidebar(
    query_history: QueryHistory,
    query_examples: QueryExamples
) -> Optional[str]:
    """Affiche la sidebar et retourne la requête sélectionnée."""
    with st.sidebar:
        st.title("📊 Assistant d'Analyse")
        
        # Affiche les exemples
        selected_example = query_examples.render_examples()
        if selected_example:
            return selected_example
            
        # Affiche l'historique
        selected_history = query_history.render_history()
        if selected_history:
            return selected_history
            
    return None

def render_main_content(
    api_service: APIService,
    viz_factory: VisualizationFactory,
    query_history: QueryHistory
) -> None:
    """Affiche le contenu principal de l'application."""
    # Vérification de la santé du backend
    try:
        health_status = api_service.get_health_status()
        if health_status["status"] != "healthy":
            st.warning("⚠️ Le service backend est en état dégradé")
    except Exception as e:
        st.error("⚠️ Impossible de se connecter au backend")

    # Zone de saisie
    prompt = st.text_area(
        "Votre question",
        value=st.session_state.get('prompt', ''),
        height=100,
        placeholder="Ex: Montre l'évolution des ventes par mois"
    )

    # Options de pagination
    col1, col2 = st.columns(2)
    with col1:
        page_size = st.selectbox(
            "Résultats par page",
            options=[10, 25, 50, 100],
            index=st.session_state.page_size // 10 - 1
        )

    # Bouton d'analyse
    if st.button("Analyser", disabled=st.session_state.is_loading):
        if not prompt:
            st.error("Veuillez entrer une question")
        else:
            try:
                st.session_state.is_loading = True
                st.session_state.last_error = None
                
                # Ajoute à l'historique
                query_history.add_query(prompt)
                
                # Appel à l'API
                response = api_service.analyze_query(
                    prompt,
                    page=st.session_state.current_page,
                    page_size=page_size
                )
                
                # Affichage des résultats
                st.success(f"✅ Analyse terminée en {response['execution_time']:.2f} secondes")
                
                # Affichage de la requête SQL
                with st.expander("Voir la requête SQL générée"):
                    st.code(response['sql_query'], language='sql')
                
                # Création du DataFrame
                df = pd.DataFrame(response['data'])
                
                # Affichage des données
                st.subheader("Données")
                st.dataframe(df)
                
                # Visualisation
                st.subheader("Visualisation")
                fig = viz_factory.create_visualization(
                    response['data'],
                    response['visualization_type'],
                    response['title']
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Pagination
                total_pages = response['total_pages']
                if total_pages > 1:
                    st.subheader("Navigation")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if st.button("◀️ Précédent", disabled=st.session_state.current_page == 1):
                            st.session_state.current_page -= 1
                            st.experimental_rerun()
                    
                    with col2:
                        st.markdown(f"Page {st.session_state.current_page} sur {total_pages}")
                    
                    with col3:
                        if st.button("Suivant ▶️", disabled=st.session_state.current_page == total_pages):
                            st.session_state.current_page += 1
                            st.experimental_rerun()
                
                # Options de téléchargement
                st.subheader("Téléchargement")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Télécharger CSV",
                        csv,
                        "analyse.csv",
                        "text/csv"
                    )
                
                with col2:
                    png = fig.to_image(format="png")
                    st.download_button(
                        "📥 Télécharger Graphique",
                        png,
                        "graphique.png",
                        "image/png"
                    )
                
            except Exception as e:
                st.session_state.last_error = str(e)
                st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
            finally:
                st.session_state.is_loading = False

    # Affichage des erreurs
    if st.session_state.last_error:
        st.markdown(f"""
        <div class="error-message">
            <strong>Erreur:</strong> {st.session_state.last_error}
        </div>
        """, unsafe_allow_html=True)

    # Indicateur de chargement
    if st.session_state.is_loading:
        st.spinner("Analyse en cours...")

def main():
    """Point d'entrée principal de l'application."""
    # Configuration de la page
    st.set_page_config(
        page_title="Assistant d'Analyse de Données",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialisation
    initialize_session_state()
    Styles.apply_styles()
    Styles.render_title()
    
    # Initialisation des composants
    api_service = APIService()
    viz_factory = VisualizationFactory()
    query_history = QueryHistory()
    query_examples = QueryExamples()
    
    # Rendu de la sidebar
    selected_query = render_sidebar(query_history, query_examples)
    if selected_query:
        st.session_state.prompt = selected_query
        st.experimental_rerun()
    
    # Rendu du contenu principal
    render_main_content(api_service, viz_factory, query_history)

if __name__ == "__main__":
    main() 