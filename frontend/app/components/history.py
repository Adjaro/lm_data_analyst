from typing import List, Tuple, Optional
from datetime import datetime
import streamlit as st

class QueryHistory:
    """Gère l'historique des requêtes."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
    
    def add_query(self, query: str) -> None:
        """Ajoute une requête à l'historique."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.query_history.insert(0, (query, timestamp))
        if len(st.session_state.query_history) > self.max_history:
            st.session_state.query_history.pop()
    
    def get_history(self) -> List[Tuple[str, str]]:
        """Retourne l'historique des requêtes."""
        return st.session_state.query_history
    
    def clear_history(self) -> None:
        """Efface l'historique des requêtes."""
        st.session_state.query_history = []
    
    def render_history(self) -> Optional[str]:
        """Affiche l'historique dans la sidebar et retourne la requête sélectionnée."""
        st.subheader("Historique des requêtes")
        
        if not st.session_state.query_history:
            st.info("Aucun historique disponible")
            return None
            
        for i, (query, timestamp) in enumerate(st.session_state.query_history):
            if st.button(
                f"{query[:30]}... ({timestamp})",
                key=f"history_{i}",
                help=query
            ):
                return query
                
        return None 