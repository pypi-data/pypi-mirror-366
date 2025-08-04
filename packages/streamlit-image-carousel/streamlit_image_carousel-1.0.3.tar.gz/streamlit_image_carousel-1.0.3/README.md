# 🎯 Streamlit Image Carousel

Un composant Streamlit moderne et personnalisable pour créer des carrousels d'images interactifs avec navigation fluide et design élégant.

## ✨ Fonctionnalités

- **🎨 Design moderne** : Interface élégante avec animations fluides
- **🔄 Navigation intuitive** : Clic sur les images ou flèches de navigation
- **♾️ Carrousel infini** : Navigation circulaire dans la liste d'images
- **🎛️ Personnalisation complète** : Couleurs, tailles, effets visuels
- **📱 Responsive** : S'adapte à différentes tailles d'écran
- **🛡️ Gestion d'erreurs** : Fallback élégant pour les images manquantes
- **⚡ Performance optimisée** : Chargement intelligent des images

## 🚀 Installation

```bash
pip install streamlit-image-carousel
```

## 📖 Utilisation rapide

```python
import streamlit as st
from streamlit_image_carousel import image_carousel

# Vos images
images = [
    {"name": "Image 1", "url": "https://example.com/image1.jpg"},
    {"name": "Image 2", "url": "https://example.com/image2.jpg"},
    # ... plus d'images
]

# Utilisation basique
result = image_carousel(images=images, key="my_carousel")

# Récupérer la sélection
if result:
    selected_image = result["selected_image"]
    selected_url = result["selected_url"]
    current_index = result["current_index"]
```

## 🎨 Personnalisation

### Paramètres disponibles

```python
result = image_carousel(
    # Paramètres obligatoires
    images=images,                    # Liste des images
    key="unique_key",                # Clé unique Streamlit
    
    # Paramètres optionnels
    selected_image=None,              # Image présélectionnée
    max_visible=5,                    # Nombre d'images visibles (3-9)
    
    # Personnalisation des couleurs
    background_color="#1a1a2e",       # Couleur de fond
    active_border_color="#ffffff",    # Bordure de l'image active
    active_glow_color="rgba(255, 255, 255, 0.5)",  # Effet de lueur
    fallback_background="#2a2a3e",    # Fond des fallbacks
    fallback_gradient_end="rgb(0, 0, 0)",  # Fin du gradient
    text_color="#ffffff",             # Couleur du texte
    arrow_color="#ffffff"             # Couleur des flèches
)
```

### Exemples de configurations

#### 🌙 Thème sombre élégant
```python
result = image_carousel(
    images=images,
    max_visible=7,
    background_color="#0f0f23",
    active_border_color="#00ff88",
    active_glow_color="rgba(0, 255, 136, 0.6)",
    fallback_background="#1a1a2e",
    fallback_gradient_end="#0a0a1a",
    text_color="#ffffff",
    arrow_color="#00ff88",
    key="dark_theme"
)
```

#### ⚽ Thème sportif
```python
result = image_carousel(
    images=images,
    max_visible=5,
    background_color="#1e3a8a",
    active_border_color="#fbbf24",
    active_glow_color="rgba(251, 191, 36, 0.7)",
    fallback_background="#3b82f6",
    fallback_gradient_end="#1e40af",
    text_color="#ffffff",
    arrow_color="#fbbf24",
    key="sport_theme"
)
```

#### ✨ Thème moderne
```python
result = image_carousel(
    images=images,
    max_visible=9,
    background_color="#f8fafc",
    active_border_color="#3b82f6",
    active_glow_color="rgba(59, 130, 246, 0.5)",
    fallback_background="#e2e8f0",
    fallback_gradient_end="#cbd5e1",
    text_color="#1e293b",
    arrow_color="#3b82f6",
    key="modern_theme"
)
```

## 📊 Format des données

### Entrée
```python
images = [
    {
        "name": "Nom de l'image",     # Texte affiché si image manquante
        "url": "https://..."          # URL de l'image
    },
    # ... plus d'images
]
```

### Sortie
```python
{
    "selected_image": "Nom de l'image sélectionnée",
    "selected_url": "https://...",
    "current_index": 0,               # Index de l'image sélectionnée
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## 🎯 Cas d'usage

### Sélection de joueurs
```python
# Exemple pour une application de football
joueurs = [
    {"name": "Lionel Messi", "url": "https://..."},
    {"name": "Cristiano Ronaldo", "url": "https://..."},
    # ...
]

joueur_selectionne = image_carousel(
    images=joueurs,
    max_visible=7,
    background_color="#1e3a8a",
    active_border_color="#fbbf24",
    arrow_color="#fbbf24",
    key="joueurs"
)
```

### Galerie de produits
```python
# Exemple pour un e-commerce
produits = [
    {"name": "Produit A", "url": "https://..."},
    {"name": "Produit B", "url": "https://..."},
    # ...
]

produit_selectionne = image_carousel(
    images=produits,
    max_visible=5,
    background_color="#f8fafc",
    active_border_color="#3b82f6",
    text_color="#1e293b",
    key="produits"
)
```

## 🔧 Développement

### Installation des dépendances
```bash
# Frontend (React + TypeScript)
cd streamlit_image_carousel/frontend
npm install

# Backend (Python)
pip install -r requirements.txt
```

### Lancement en mode développement
```bash
# Terminal 1: Frontend
cd streamlit_image_carousel/frontend
npm run dev

# Terminal 2: Backend
streamlit run example.py
```

### Build pour production
```bash
cd streamlit_image_carousel/frontend
npm run build
```

## 📝 Exemples

- **`example.py`** : Application complète avec interface de personnalisation
- **`example_image_selector.py`** : Exemples simples de différentes configurations

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [Streamlit](https://streamlit.io/) pour l'écosystème
- [React](https://reactjs.org/) pour le frontend
- [TypeScript](https://www.typescriptlang.org/) pour la sécurité des types

---

**Streamlit Image Carousel** - Créez des carrousels d'images élégants et interactifs pour vos applications Streamlit ! 🎨✨ 