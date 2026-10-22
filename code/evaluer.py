import csv, json, os, sys, time
from pathlib import Path
from classifieur import CONSIGNE, classer
from evaluation import afficher_rapport

PAUSE = 2.1  # 30 requêtes/minute au maximum


def charger(chemin=None):  # lit le CSV
    if chemin is None:
        chemin = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"
    with open(chemin, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def evaluer(modele, lignes, consigne=CONSIGNE, etiquette=None):
    etiquette = etiquette or modele
    vrais, predits, debut = [], [], time.time()

    for idx, ligne in enumerate(lignes, 1):
        pred = classer(ligne["texte"], modele, consigne=consigne)
        predits.append(pred)
        vrais.append(ligne["categorie"])
        print(f"[{idx:>2}/{len(lignes)}] Ticket {ligne['id']} -> {pred}")
        time.sleep(PAUSE)

    resume = afficher_rapport(etiquette, vrais, predits)
    resume.update(
        modele=modele,
        etiquette=etiquette,
        duree_s=round(time.time() - debut, 1),
        predits=predits,
        ids=[l["id"] for l in lignes],
    )

    # Chemin vers le dossier resultats
    DOSSIER_RESULTATS = Path(__file__).resolve().parent.parent / "resultats"
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    nom_fichier = f"{modele.replace('/', '_')}.json"
    fichier_sortie = DOSSIER_RESULTATS / nom_fichier

    # Enregistrer le résumé
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=2)

    print(f"Résultats enregistrés dans : {fichier_sortie}")
    return resume


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluer.py <modele>")
        sys.exit(1)
    evaluer(sys.argv[1], charger())
