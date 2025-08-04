"""
Configuration pour le composant Streamlit Image Carousel
"""

import os

# Mode de développement (True pour développement, False pour production)
DEV_MODE = os.getenv("STREAMLIT_IMAGE_CAROUSEL_DEV", "false").lower() == "true"

# URL de développement pour le frontend
DEV_URL = "http://localhost:3002"

# Configuration du composant
COMPONENT_NAME = "image_carousel"

# Paramètres par défaut
DEFAULT_MAX_VISIBLE = 5
DEFAULT_ORIENTATION = "horizontal"
DEFAULT_BACKGROUND_COLOR = "#1a1a2e"
DEFAULT_ACTIVE_BORDER_COLOR = "#ffffff"
DEFAULT_ACTIVE_GLOW_COLOR = "rgba(255, 255, 255, 0.5)"
DEFAULT_FALLBACK_BACKGROUND = "#2a2a3e"
DEFAULT_FALLBACK_GRADIENT_END = "rgb(0, 0, 0)"
DEFAULT_TEXT_COLOR = "#ffffff"
DEFAULT_ARROW_COLOR = "#ffffff" 