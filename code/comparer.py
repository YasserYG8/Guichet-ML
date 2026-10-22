import json
from pathlib import Path

DOSSIER_RESULTATS = Path(__file__).resolve().parent.parent / "resultats"


def charger_resultats():
    fichiers = list(DOSSIER_RESULTATS.glob("*.json"))
    if not fichiers:
        print(f"Aucun fichier de résultats trouvé dans : {DOSSIER_RESULTATS}")
        print("Veuillez d'abord exécuter : python evaluer.py <modele>")
        return []

    resultats = []
    for f in sorted(fichiers):
        try:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
                resultats.append(data)
        except Exception as e:
            print(f"Erreur de lecture de {f.name} : {e}")

    return resultats


def afficher_comparaison(resultats):
    if not resultats:
        return

    print("\n" + "=" * 70)
    print("COMPARAISON DES MODÈLES")
    print("=" * 70)
    print(f"{'Modèle':<30} {'Accuracy':>10} {'Macro-F1':>10} {'Invalides':>10} {'Durée (s)':>10}")
    print("-" * 75)

    # Tri par Macro-F1 décroissant
    resultats_tries = sorted(
        resultats, key=lambda r: r.get("macro-F1", r.get("macro_f1", 0)), reverse=True
    )

    for r in resultats_tries:
        nom = r.get("etiquette", r.get("modele", "inconnu"))
        acc = r.get("accuracy", 0.0)
        macro = r.get("macro-F1", r.get("macro_f1", 0.0))
        inv = r.get("invalides", r.get("taux_invalides", 0.0))
        duree = r.get("duree_s", 0.0)

        print(f"{nom:<30} {acc:>10.3f} {macro:>10.3f} {inv:>10.3f} {duree:>10.1f}")

    print("-" * 75)

    # Analyse de l'écart si au moins 2 modèles
    if len(resultats_tries) >= 2:
        m1 = resultats_tries[0]
        m2 = resultats_tries[1]
        nom1 = m1.get("etiquette", m1.get("modele"))
        nom2 = m2.get("etiquette", m2.get("modele"))
        f1_1 = m1.get("macro-F1", m1.get("macro_f1", 0))
        f1_2 = m2.get("macro-F1", m2.get("macro_f1", 0))
        ecart_points = (f1_1 - f1_2) * 100
        ecart_tickets = round((f1_1 - f1_2) * 72)

        print(f"\nÉcart entre premier ({nom1}) et deuxième ({nom2}) :")
        print(f"  • {ecart_points:+.1f} points de Macro-F1")
        print(f"  • {ecart_tickets:+d} tickets d'écart")
        if abs(ecart_tickets) < 5:
            print("  -> Conclusion : Moins de 5 tickets d'écart = Pas de différence mesurable.")
        else:
            print("  -> Conclusion : Au moins 5 tickets d'écart = Différence mesurable significative.")

    afficher_desaccords(resultats_tries)


def afficher_desaccords(resultats):
    if len(resultats) < 2:
        return

    ids_reference = resultats[0].get("ids", [])
    if not ids_reference:
        return

    print("\n" + "=" * 70)
    print("DÉSACCORDS ENTRE MODÈLES")
    print("=" * 70)

    desaccords_trouves = 0
    for idx, ticket_id in enumerate(ids_reference):
        preds_ticket = {}
        for r in resultats:
            nom = r.get("etiquette", r.get("modele", "inconnu"))
            predits = r.get("predits", [])
            if idx < len(predits):
                preds_ticket[nom] = predits[idx]

        # S'il y a plus d'une valeur distincte de prédiction -> désaccord
        valeurs_uniques = set(preds_ticket.values())
        if len(valeurs_uniques) > 1:
            desaccords_trouves += 1
            details = " | ".join(f"{nom} = {pred}" for nom, pred in preds_ticket.items())
            print(f"{ticket_id} : {details}")

    print(f"\nTotal des tickets en désaccord : {desaccords_trouves} / {len(ids_reference)}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    resultats = charger_resultats()
    afficher_comparaison(resultats)
