from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class VisualizationFactory:
    """Factory pour créer des visualisations Plotly."""
    
    @staticmethod
    def create_visualization(
        data: List[Dict[str, Any]],
        viz_type: str,
        title: str
    ) -> go.Figure:
        """Crée une visualisation Plotly basée sur le type et les données."""
        df = pd.DataFrame(data)
        
        if viz_type == 'line':
            return px.line(df, title=title)
        elif viz_type == 'bar':
            return px.bar(df, title=title)
        elif viz_type == 'pie':
            return px.pie(df, title=title)
        elif viz_type == 'histogram':
            return px.histogram(df, title=title)
        else:
            return px.scatter(df, title=title)
    
    @staticmethod
    def get_visualization_options() -> Dict[str, str]:
        """Retourne les options de visualisation disponibles."""
        return {
            'line': 'Graphique linéaire',
            'bar': 'Graphique en barres',
            'pie': 'Graphique circulaire',
            'histogram': 'Histogramme',
            'scatter': 'Nuage de points'
        }

    @staticmethod
    def create_multiple_visualizations(data: list, viz_types: List[str], title: str) -> List[go.Figure]:
        """Crée plusieurs visualisations pour les mêmes données"""
        return [VisualizationFactory.create_visualization(data, viz_type, title) 
                for viz_type in viz_types] 