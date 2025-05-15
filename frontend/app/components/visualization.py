import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List

class VisualizationFactory:
    @staticmethod
    def create_visualization(data: list, viz_type: str, title: str) -> go.Figure:
        df = pd.DataFrame(data)
        
        # Configuration des couleurs
        colors = px.colors.qualitative.Set3
        
        # Configuration commune
        common_layout = dict(
            template="plotly_white",
            title_x=0.5,
            title_font_size=20,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=100, l=50, r=50, b=50),
            font=dict(family="Arial, sans-serif")
        )
        
        if viz_type == "line":
            fig = px.line(
                df,
                title=title,
                color_discrete_sequence=colors,
                markers=True
            )
            fig.update_traces(line=dict(width=3))
            
        elif viz_type == "bar":
            fig = px.bar(
                df,
                title=title,
                color_discrete_sequence=colors,
                barmode="group"
            )
            fig.update_traces(marker=dict(line=dict(width=1, color='white')))
            
        elif viz_type == "histogram":
            fig = px.histogram(
                df,
                title=title,
                color_discrete_sequence=colors,
                nbins=30
            )
            fig.update_traces(marker=dict(line=dict(width=1, color='white')))
            
        elif viz_type == "pie":
            fig = px.pie(
                df,
                title=title,
                color_discrete_sequence=colors,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
        else:
            fig = px.bar(
                df,
                title=title,
                color_discrete_sequence=colors
            )
        
        # Application du layout commun
        fig.update_layout(**common_layout)
        
        # Ajout d'une grille pour les graphiques linéaires et en barres
        if viz_type in ["line", "bar"]:
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        
        return fig

    @staticmethod
    def create_multiple_visualizations(data: list, viz_types: List[str], title: str) -> List[go.Figure]:
        """Crée plusieurs visualisations pour les mêmes données"""
        return [VisualizationFactory.create_visualization(data, viz_type, title) 
                for viz_type in viz_types] 