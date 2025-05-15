from typing import Dict, List, Optional
import streamlit as st

class QueryExamples:
    """Gère les exemples de requêtes."""
    
    def __init__(self):
        self.examples = {
            "Analyse temporelle": [
                "Montre l'évolution des ventes par mois",
                "Analyse la tendance des prix sur les 6 derniers mois"
            ],
            "Distribution": [
                "Distribution des âges des clients",
                "Répartition des ventes par catégorie"
            ],
            "Comparaison": [
                "Compare les performances des différents produits",
                "Analyse comparative des ventes par région"
            ],
            "Analyse détaillée": [
                "Détaille les ventes par produit et par région",
                "Analyse approfondie des comportements clients"
            ]
        }
    
    def render_examples(self) -> Optional[str]:
        """Affiche les exemples dans la sidebar et retourne l'exemple sélectionné."""
        st.subheader("Exemples de requêtes")
        
        for category, queries in self.examples.items():
            with st.expander(category):
                for query in queries:
                    if st.button(query, key=f"example_{query}"):
                        return query
                        
        return None
    
    def add_example(self, category: str, query: str) -> None:
        """Ajoute un nouvel exemple."""
        if category not in self.examples:
            self.examples[category] = []
        self.examples[category].append(query)
    
    def get_examples(self) -> Dict[str, List[str]]:
        """Retourne tous les exemples."""
        return self.examples 