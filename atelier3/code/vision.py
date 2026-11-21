"""Classer une capture d'ecran avec un modele qui voit : un seul appel, de bout en bout.

    python vision.py ../data/captures/I06.png
"""
import base64
import json
import os
import sys
from pathlib import Path

from groq import Groq

from evaluation import CATEGORIES

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
MODELE_VISION = "qwen/qwen3.8-27b"     # lit le texte ET les images, palier gratuit

CONSIGNE_IMAGE = """Un client du service client a envoye cette capture d'ecran pour illustrer son probleme.
Classe-la dans exactement une categorie parmi : facturation, technique, compte, commercial.

Definitions :
- facturation : un montant, une facture, un paiement, un remboursement.
- technique : un service qui ne fonctionne pas comme prevu.
- compte : l'acces au compte ou les donnees personnelles.
- commercial : le choix d'une offre, un abonnement, une resiliation.

Si la capture montre une erreur technique (code d'erreur, page qui ne charge pas,
application qui plante), choisis technique, meme sur une page de paiement ou d'offre.

Reponds uniquement par un objet JSON de la forme {"categorie": "<une des quatre>"}."""


# ---------------------------------------------------------------- fourni
def data_url(chemin):
    """Transforme une image en texte (base64) que l'on peut glisser dans un message JSON."""
    octets = Path(chemin).read_bytes()
    type_mime = "image/png" if str(chemin).lower().endswith(".png") else "image/jpeg"
    return f"data:{type_mime};base64,{base64.b64encode(octets).decode('ascii')}"


# ---------------------------------------------------------------- a ecrire
def classer_image(chemin, modele=MODELE_VISION, consigne=CONSIGNE_IMAGE):
    """Envoie la capture au modele et renvoie une categorie, ou "invalide"."""
    reponse = client.chat.completions.create(
        model=modele,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": consigne},
                {"type": "image_url", "image_url": {"url": data_url(chemin)}},
            ],
        }],
    )
    brut = reponse.choices[0].message.content
    try:
        categorie = json.loads(brut).get("categorie", "")
    except (json.JSONDecodeError, AttributeError, TypeError):
        return "invalide"
    categorie = str(categorie).strip().lower()
    return categorie if categorie in CATEGORIES else "invalide"



if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage : python vision.py <capture.png>")
    print(classer_image(sys.argv[1]))
