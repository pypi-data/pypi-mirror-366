# 📝 Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### ✨ Ajouté
- **Composant de carrousel d'images interactif** : Navigation fluide avec clics et flèches
- **Personnalisation complète des couleurs** : Fond, bordures, lueurs, texte, flèches
- **Gestion d'erreurs robuste** : Fallback élégant pour les images manquantes
- **Navigation infinie** : Carrousel circulaire sans fin
- **Responsive design** : S'adapte à différentes tailles d'écran
- **Paramètres configurables** : Nombre d'images visibles (3-9)
- **Flèches toujours visibles** : Navigation accessible en permanence
- **Effets visuels** : Animations fluides et effets de lueur
- **Documentation complète** : README, exemples, guide de développement

### 🎨 Fonctionnalités visuelles
- Design moderne avec animations CSS
- Effets de lueur autour de l'image active
- Gradients pour les fallbacks d'images
- Typographie élégante avec police Urbanist
- Transitions fluides entre les états

### 🔧 Configuration
- **`background_color`** : Couleur de fond du composant
- **`active_border_color`** : Couleur de la bordure de l'image active
- **`active_glow_color`** : Couleur de l'effet de lueur
- **`fallback_background`** : Couleur de fond des fallbacks
- **`fallback_gradient_end`** : Couleur de fin du gradient
- **`text_color`** : Couleur du texte
- **`arrow_color`** : Couleur des flèches de navigation
- **`max_visible`** : Nombre d'images visibles (3-9)
- **`selected_image`** : Image présélectionnée

### 📊 Format des données
- **Entrée** : Liste d'objets `{"name": "Nom", "url": "URL"}`
- **Sortie** : Objet avec `selected_image`, `selected_url`, `current_index`, `timestamp`

### 🚀 Exemples inclus
- Application complète avec interface de personnalisation
- Exemples de configurations (sombre, sportif, moderne)
- Cas d'usage (sélection de joueurs, galerie de produits)

### 🛠️ Architecture technique
- **Frontend** : React + TypeScript + Vite
- **Backend** : Python + Streamlit
- **Build** : Configuration moderne avec pyproject.toml
- **Développement** : Hot reload et mode développement

---

## [0.1.0] - 2024-01-01

### ✨ Ajouté
- Version initiale du composant
- Fonctionnalités de base de navigation
- Interface utilisateur simple

---

## Types de changements

- **✨ Ajouté** : Nouvelles fonctionnalités
- **🐛 Corrigé** : Corrections de bugs
- **💥 Changé** : Changements incompatibles avec les versions précédentes
- **🗑️ Supprimé** : Fonctionnalités supprimées
- **🔒 Sécurité** : Corrections de vulnérabilités
- **📚 Documentation** : Mises à jour de la documentation
- **🎨 Style** : Changements qui n'affectent pas le code (espacement, formatage, etc.)
- **♻️ Refactorisé** : Refactorisation du code de production
- **⚡ Performance** : Améliorations des performances
- **🧪 Test** : Ajout ou correction de tests
- **🔧 Configuration** : Changements de configuration 