import streamlit as st

class Styles:
    """Gère les styles CSS de l'application."""
    
    @staticmethod
    def apply_styles() -> None:
        """Applique les styles CSS à l'application."""
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
            .error-message {
                background-color: #ffebee;
                color: #c62828;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
            .success-message {
                background-color: #e8f5e9;
                color: #2e7d32;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
            .stButton>button {
                width: 100%;
                margin-top: 1rem;
            }
            .history-item {
                padding: 0.5rem;
                margin: 0.5rem 0;
                border-radius: 0.25rem;
                background-color: #f5f5f5;
                cursor: pointer;
            }
            .history-item:hover {
                background-color: #e0e0e0;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_title() -> None:
        """Affiche le titre de l'application."""
        st.markdown("""
        <h1 style='text-align: center; color: #2c3e50; margin-bottom: 2rem; font-size: 2.5rem;'>
            📊 Assistant d'Analyse de Données
        </h1>
        """, unsafe_allow_html=True) 