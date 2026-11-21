"""Le classifieur : un appel Groq par ticket, une categorie en retour."""
import json
import os
import time

from groq import Groq, RateLimitError

from evaluation import CATEGORIES

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

CONSIGNE = """Tu es un agent de tri du service client.
Classe le ticket dans exactement une categorie parmi : facturation, technique, compte, commercial.

Definitions :
- facturation : le ticket porte sur un montant, une facture, un paiement, un remboursement.
- technique : le ticket porte sur un service qui ne fonctionne pas comme prevu.
- compte : le ticket porte sur l'acces au compte ou les donnees personnelles.
- commercial : le ticket porte sur le choix d'une offre, un abonnement, une resiliation.

Si plusieurs categories semblent possibles, retiens l'intention principale du client :
ce qu'il veut obtenir, pas ce qu'il decrit en chemin.

Reponds uniquement par un objet JSON de la forme {"categorie": "<une des quatre>"}."""


def classer(texte, modele, consigne=CONSIGNE, temperature=0.0):
    """Renvoie une categorie, ou la chaine "invalide" si la reponse est inexploitable."""
    for tentative in range(4):
        try:
            reponse = client.chat.completions.create(
                model=modele,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": consigne},
                    {"role": "user", "content": texte},
                ],
            )
            break
        except RateLimitError:
            attente = 5 * (tentative + 1)
            print(f"  quota atteint, pause de {attente} s")
            time.sleep(attente)
    else:
        raise RuntimeError("quota toujours atteint apres 4 tentatives")

    brut = reponse.choices[0].message.content
    try:
        categorie = json.loads(brut).get("categorie", "")
    except (json.JSONDecodeError, AttributeError):
        return "invalide"
    categorie = str(categorie).strip().lower()
    return categorie if categorie in CATEGORIES else "invalide"
