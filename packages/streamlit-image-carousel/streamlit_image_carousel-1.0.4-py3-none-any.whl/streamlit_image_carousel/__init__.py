import os
import streamlit.components.v1 as components
from pathlib import Path

# Déclarer le composant
_RELEASE = True  # Mode production

if not _RELEASE:
    _component_func = components.declare_component(
        "image_carousel",
        url="http://localhost:3001",
    )
else:
    # Utiliser le chemin absolu pour que ça fonctionne après installation
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component("image_carousel", path=build_dir)

def image_carousel(
    images: list, 
    selected_image: str = None, 
    max_visible: int = 5,
    orientation: str = 'horizontal',
    background_color: str = '#1a1a2e',
    active_border_color: str = '#ffffff',
    active_glow_color: str = 'rgba(255, 255, 255, 0.5)',
    fallback_background: str = '#2a2a3e',
    fallback_gradient_end: str = 'rgb(0, 0, 0)',
    text_color: str = '#ffffff',
    arrow_color: str = '#ffffff',
    key=None
):
    """
    Un composant Streamlit moderne pour créer des carrousels d'images interactifs.
    
    Parameters:
    -----------
    images : list
        Liste des images avec format: [{"name": "nom_image", "url": "url_image"}, ...]
    selected_image : str
        Image actuellement sélectionnée (optionnel)
    max_visible : int
        Nombre maximum d'images visibles à la fois (défaut: 5)
    orientation : str
        Orientation du carousel: 'horizontal' ou 'vertical' (défaut: 'horizontal')
    background_color : str
        Couleur de fond du composant (défaut: '#1a1a2e')
    active_border_color : str
        Couleur de la bordure du joueur actif (défaut: '#ffffff')
    active_glow_color : str
        Couleur de l'effet de lueur (défaut: 'rgba(255, 255, 255, 0.5)')
    fallback_background : str
        Couleur de fond des fallbacks (défaut: '#2a2a3e')
    fallback_gradient_end : str
        Couleur de fin du gradient (défaut: 'rgb(0, 0, 0)')
    text_color : str
        Couleur du texte (défaut: '#ffffff')
    arrow_color : str
        Couleur des flèches de navigation (défaut: '#ffffff')
    key : str
        Une clé unique pour le composant
    
    Returns:
    --------
    dict
        Les données retournées par le composant frontend
        {"selected_image": "nom_image", "selected_url": "url_image", "current_index": 0}
    """
    component_value = _component_func(
        images=images,
        selected_image=selected_image,
        max_visible=max_visible,
        orientation=orientation,
        background_color=background_color,
        active_border_color=active_border_color,
        active_glow_color=active_glow_color,
        fallback_background=fallback_background,
        fallback_gradient_end=fallback_gradient_end,
        text_color=text_color,
        arrow_color=arrow_color,
        key=key,
        default=None
    )
    
    return component_value 