# 🔍 RepoCodeExtractor

Script Python pour cloner un dépôt GitHub, extraire tous les fichiers de code source, et générer un fichier `.json` contenant :

* le chemin relatif du fichier,
* son contenu,
* les auteurs ayant contribué à ce fichier via Git.

---

## 📦 Prérequis

* Python 3.8 ou plus
* `git` installé sur votre système (et accessible dans le `PATH`)

---

## 🚀 Installation

1. **Cloner ce projet (ou copier le fichier Python)**
   Tu peux simplement copier le fichier `RepoCodeExtractor.py` dans ton projet.

2. **Créer un environnement virtuel (optionnel mais recommandé)**

   ```
   python -m venv venv
   source venv/bin/activate  # Sous Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances nécessaires**

   ```
   pip install gitpython
   ```

---

## 🛠️ Utilisation

```
python RepoCodeExtractor.py
```

Par défaut, le script :

* clone le dépôt `https://github.com/KentinPaille/ChessStatePrediction` dans un dossier local nommé `ChessStatePrediction`,
* extrait tous les fichiers de code source (extensions : `.py`, `.js`, `.ipynb`, etc.),
* analyse les auteurs git de chaque fichier,
* exporte le résultat dans un fichier `ChessStatePrediction.json`.

---

## ⚙️ Personnalisation

Tu peux créer ton propre script en important la classe :

```
from RepoCodeExtractor import RepoCodeExtractor

extractor = RepoCodeExtractor(
repo\_url="[https://github.com/mon-utilisateur/mon-repo](https://github.com/mon-utilisateur/mon-repo)",
clone\_dir="mon\_dossier\_local",
output\_json="mon\_fichier\_export.json"
)
extractor.export()
```

---

## 📄 Exemple de sortie (`.json`)

```
\[
{
"file": "utils/chess\_generate.py",
"content": "import chess\nimport pandas as pd\n...",
"authors": \["Alice Dupont", "Bob Martin"]
},
...
]
```

---

## 🧽 Nettoyage

Pour supprimer le dossier cloné :

```
rm -rf ChessStatePrediction
```

---

## 🧑‍💻 Auteurs

Développé par [@KentinPaille](https://github.com/KentinPaille)

---

Souhaite-tu que je te le mette dans un `.md` téléchargeable ?
