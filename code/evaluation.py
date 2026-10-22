CATEGORIES = ["facturation", "technique", "compte", "commercial"]


def accuracy(vrais, predits):
    return sum(1 for v, p in zip(vrais, predits) if v == p) / len(vrais)


def scores_par_classe(vrais, predits, classes=CATEGORIES):
    resultat = {}
    for c in classes:
        vp = sum(1 for v, p in zip(vrais, predits) if v == c and p == c)
        fp = sum(1 for v, p in zip(vrais, predits) if v != c and p == c)
        fn = sum(1 for v, p in zip(vrais, predits) if v == c and p != c)
        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0
        f1 = (
            (2 * precision * recall / (precision + recall))
            if (precision + recall)
            else 0.0
        )
        resultat[c] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "support": vp + fn,
        }
    return resultat


def f1_macro(scores):
    return sum(d["f1"] for d in scores.values()) / len(scores)


def taux_invalides(predits):
    return sum(1 for p in predits if p == "invalide") / len(predits) if predits else 0.0


def matrice_confusion(vrais, predits):
    colonnes = CATEGORIES + ["invalide"]
    matrice = {v: {p: 0 for p in colonnes} for v in CATEGORIES}
    for v, p in zip(vrais, predits):
        if v in matrice and p in colonnes:
            matrice[v][p] += 1
    return matrice


def afficher_rapport(etiquette, vrais, predits):
    acc = accuracy(vrais, predits)
    scores = scores_par_classe(vrais, predits)
    macro = f1_macro(scores)
    invalides = taux_invalides(predits)
    matrice = matrice_confusion(vrais, predits)

    print(f"\n=== {etiquette} ===")
    print(f"accuracy   : {acc:.3f}")
    print(f"macro-F1   : {macro:.3f}")
    print(f"invalides  : {invalides:.3f}\n")

    print(f"{'categorie':<13} {'precision':>9} {'recall':>9} {'F1':>9} {'n':>5}")
    for cat, sc in scores.items():
        print(
            f"{cat:<13} {sc['precision']:>9.3f} {sc['recall']:>9.3f} {sc['f1']:>9.3f} {sc['support']:>5}"
        )

    print("\nConfusion matrix (lignes = vérité, colonnes = prédiction)")
    abreviations = ["factur", "techni", "compte", "commer", "invali"]
    print(f"{'':<13} " + " ".join(f"{col:>6}" for col in abreviations))
    colonnes_completes = CATEGORIES + ["invalide"]
    for v in CATEGORIES:
        valeurs = [matrice[v].get(c, 0) for c in colonnes_completes]
        print(f"{v:<13} " + " ".join(f"{val:>6}" for val in valeurs))
    print()

    return {
        "accuracy": round(acc, 3),
        "macro-F1": round(macro, 3),
        "invalides": round(invalides, 3),
        "scores_par_classe": scores,
        "matrice_confusion": matrice,
    }
