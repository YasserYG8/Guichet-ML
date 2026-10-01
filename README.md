# Guichet ML — Service de Détection de Langue

Ce projet constitue la première brique du **Guichet ML** (Machine Learning Appliqué — Licence 3 DSI) : une API REST construite avec **FastAPI** qui reçoit un texte utilisateur, identifie sa langue (français, arabe, anglais), et renvoie une réponse normalisée selon un contrat strict, indépendamment du fournisseur d'inférence utilisé.

---

## Fonctionnalités Principales

- **Contrat d'API robuste et agnostique** : Schémas Pydantic stricts pour découpler l'application des spécificités du fournisseur de modèle.
- **Fournisseur simulé (Mode Mock)** : Composant déterministe hors ligne permettant de développer et d'exécuter l'intégralité des tests sans compte, sans GPU et sans connexion Internet.
- **Fournisseur réel (Mode Real)** : Client d'inférence Hugging Face (`huggingface_hub`) avec mécanisme de repli automatique (fallback) vers le mock en cas de défaillance.
- **Résilience & Sécurité** :
  - Validation automatique des entrées avec code HTTP `422`.
  - Gestion sécurisée des pannes distantes avec code HTTP `503` (aucun jeton ni trace interne exposés au client).
  - Protection des secrets via variable d'environnement (`.env` exclu du versionnement Git).
- **Mesure de performance** : Calcul précis de la latence (`latency_ms`) pour chaque requête.
- **Indicateur de révision** : Champ `requires_review` alertant lorsqu'un score de confiance est inférieur au seuil configuré (`REVIEW_THRESHOLD`).

---

## Structure du Projet

```text
guichet-ml/
├── app/
│   ├── __init__.py        # Marqueur de package Python
│   ├── config.py          # Centralisation des variables d'environnement (.env)
│   ├── main.py            # Application FastAPI et routes (/health, /detect-language)
│   ├── providers.py       # MockProvider, HfProvider et fabrique get_provider()
│   └── schemas.py         # Modèles de données Pydantic (Prediction, Request, Response)
├── tests/
│   ├── __init__.py
│   └── test_api.py        # Suite de tests unitaires et d'intégration (pytest)
├── .env.example           # Gabarit documentant les variables nécessaires
├── .gitignore             # Exclusion de .venv/, .env, caches et fichiers temporaires
├── pytest.ini             # Configuration de découverte des modules pour pytest
├── README.md              # Documentation du projet et guide d'installation
└── requirements.txt       # Versions figées des dépendances Python
```

---

## Prérequis

- **Python 3.10 ou supérieur** (vérifiable avec `python --version` ou `py --version`)
- **Git**

---

## Installation et Démarrage

### 1. Cloner le projet
```bash
git clone <url-du-depot>
cd guichet-ml
```

### 2. Créer et activer l'environnement virtuel

- **Sous Windows (PowerShell) :**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
  *(Si l'activation de script est restreinte : `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **Sous Linux / macOS :**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Installer les dépendances
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
Créez votre fichier local `.env` à partir de `.env.example` :

- **Sous Windows (PowerShell) :**
  ```powershell
  Copy-Item .env.example .env
  ```
- **Sous Linux / macOS :**
  ```bash
  cp .env.example .env
  ```

Le fichier `.env` par défaut est configuré en mode **MOCK** (recommandé pour les tests et l'évaluation) :
```env
INFERENCE_MODE=mock
HF_TOKEN=
MODEL_ID=papluca/xlm-roberta-base-language-detection
REVIEW_THRESHOLD=0.60
```

---

## Lancement de l'Application

Démarrez le serveur avec rechargement automatique :
```bash
uvicorn app.main:app --reload
```

Le serveur sera disponible sur : **http://127.0.0.1:8000**

- **Documentation Swagger interactive** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Vérification de l'état** : [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Endpoints de l'API

### 1. `GET /health`
Vérifie la disponibilité du service et indique le mode actif.

**Réponse exemple (200 OK) :**
```json
{
  "status": "ok",
  "mode": "mock",
  "provider": "mock"
}
```

---

### 2. `POST /detect-language`
Reçoit un texte brut et renvoie la prédiction de langue normalisée.

**Exemple de requête :**
```json
{
  "text": "Je souhaite reinitialiser mon mot de passe."
}
```

**Exemple de réponse (200 OK) :**
```json
{
  "provider": "mock",
  "model": "papluca/xlm-roberta-base-language-detection",
  "latency_ms": 1.3,
  "language": "fr",
  "requires_review": false,
  "predictions": [
    {
      "label": "fr",
      "score": 0.95
    },
    {
      "label": "it",
      "score": 0.03
    }
  ]
}
```

#### Test rapide via ligne de commande :

- **PowerShell :**
  ```powershell
  $body = @{ text = "Je souhaite reinitialiser mon mot de passe." } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/detect-language" -ContentType "application/json" -Body $body
  ```

- **cURL :**
  ```bash
  curl -X POST http://127.0.0.1:8000/detect-language \
    -H "Content-Type: application/json" \
    -d '{"text": "Je souhaite reinitialiser mon mot de passe."}'
  ```

---

## Codes d'Erreur & Réponses HTTP

| Code HTTP | Cas d'utilisation | Explication |
| :--- | :--- | :--- |
| **`200 OK`** | Requête valide | Traitement réussi avec prédictions et latence calculée. |
| **`422 Unprocessable Entity`** | Texte $< 3$ car., $> 1000$ car. ou champ manquant | Entrée non conforme au schéma validé par Pydantic. |
| **`503 Service Unavailable`** | Fournisseur d'inférence en panne / erreur réseau | Le backend intercepte l'erreur et protège les secrets internes. |

---

## Exécution des Tests Automatisés

Les tests s'exécutent entièrement hors ligne en moins de 2 secondes :
```bash
pytest -q
```

**Résultat attendu :**
```text
....                                                                     [100%]
4 passed in 1.70s
```

---

## Mode Réel (Bonus Hugging Face)

Pour tester l'appel vers le vrai modèle Hugging Face :
1. Installez le client officiel :
   ```bash
   python -m pip install huggingface_hub
   ```
2. Créez un jeton d'accès (Read ou avec permission *Inference API*) sur [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
3. Modifiez votre `.env` local :
   ```env
   INFERENCE_MODE=real
   HF_TOKEN=votre_jeton_ici
   ```
4. Relancez le serveur : `uvicorn app.main:app --reload`.

---


