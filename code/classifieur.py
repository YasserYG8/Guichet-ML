import json, os, time
from groq import Groq, RateLimitError
from dotenv import load_dotenv

load_dotenv()
CATEGORIES = ["facturation", "technique", "compte", "commercial"]
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CONSIGNE = """Tu es un agent de tri du service client.
Classe le ticket dans exactement une catégorie :
- facturation : montant, facture, paiement, remboursement.
- technique : un service ne fonctionne pas comme prévu.
- compte : accès au compte ou données personnelles.
- commercial : choix d'offre, abonnement, résiliation.
Si plusieurs catégories semblent possibles, retiens l'intention
principale du client : ce qu'il veut obtenir.
Réponds uniquement par un objet JSON de la forme
{"categorie": "<une des quatre>"}."""


def classer(texte, modele, consigne=CONSIGNE, temperature=0.0):
    while True:
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
            print("Limite de débit atteinte (429), pause de 5 secondes...")
            time.sleep(5)
        except Exception as e:
            print(f"Erreur API ({type(e).__name__}) : {e}")
            return "invalide"

    try:
        categorie = json.loads(reponse.choices[0].message.content).get("categorie", "")
    except (json.JSONDecodeError, AttributeError):
        return "invalide"

    categorie = str(categorie).strip().lower()
    return categorie if categorie in CATEGORIES else "invalide"
