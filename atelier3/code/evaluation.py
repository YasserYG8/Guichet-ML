"""Metriques d'evaluation, ecrites a la main pour que rien ne reste opaque.

Vocabulaire, pour une categorie C :
  VP (vrai positif)  : le ticket est C, le modele a dit C.
  FP (faux positif)  : le ticket n'est pas C, le modele a dit C quand meme.
  FN (faux negatif)  : le ticket est C, le modele a dit autre chose.

  precision(C) = VP / (VP + FP)   -> quand le modele dit C, a quel point a-t-il raison ?
  recall(C)    = VP / (VP + FN)   -> parmi les vrais C, combien en a-t-il trouve ?
  F1(C)        = moyenne harmonique de precision et recall.
"""

CATEGORIES = ["facturation", "technique", "compte", "commercial"]


def accuracy(vrais, predits):
    """Part de tickets correctement classes. Aveugle au desequilibre des classes."""
    bons = sum(1 for v, p in zip(vrais, predits) if v == p)
    return bons / len(vrais)


def scores_par_classe(vrais, predits, classes=CATEGORIES):
    resultat = {}
    for c in classes:
        vp = sum(1 for v, p in zip(vrais, predits) if v == c and p == c)
        fp = sum(1 for v, p in zip(vrais, predits) if v != c and p == c)
        fn = sum(1 for v, p in zip(vrais, predits) if v == c and p != c)
        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        resultat[c] = {"precision": precision, "recall": recall, "f1": f1, "support": vp + fn}
    return resultat


def f1_macro(scores):
    """Moyenne simple des F1. Chaque categorie pese pareil, meme la plus rare."""
    return sum(d["f1"] for d in scores.values()) / len(scores)


def taux_invalides(predits, classes=CATEGORIES):
    """Part de reponses hors nomenclature : JSON casse ou categorie inventee."""
    return sum(1 for p in predits if p not in classes) / len(predits)


def matrice_confusion(vrais, predits, classes=CATEGORIES):
    colonnes = list(classes) + ["invalide"]
    m = {v: {p: 0 for p in colonnes} for v in classes}
    for v, p in zip(vrais, predits):
        m[v][p if p in classes else "invalide"] += 1
    return m, colonnes


def afficher_rapport(nom, vrais, predits, classes=CATEGORIES):
    scores = scores_par_classe(vrais, predits, classes)
    print(f"\n=== {nom} ===")
    print(f"accuracy    : {accuracy(vrais, predits):.3f}")
    print(f"macro-F1    : {f1_macro(scores):.3f}")
    print(f"invalides   : {taux_invalides(predits, classes):.3f}")
    print(f"\n{'categorie':<13}{'precision':>11}{'recall':>9}{'F1':>8}{'n':>6}")
    for c, d in scores.items():
        print(f"{c:<13}{d['precision']:>11.3f}{d['recall']:>9.3f}{d['f1']:>8.3f}{d['support']:>6d}")
    m, colonnes = matrice_confusion(vrais, predits, classes)
    largeur = max(len(c) for c in colonnes) + 2
    print("\nConfusion matrix (lignes = verite, colonnes = prediction)")
    print(" " * 13 + "".join(f"{c[:6]:>{largeur}}" for c in colonnes))
    for v in classes:
        print(f"{v:<13}" + "".join(f"{m[v][p]:>{largeur}d}" for p in colonnes))

    return {"accuracy": accuracy(vrais, predits), "f1_macro": f1_macro(scores),
            "invalides": taux_invalides(predits, classes), "par_classe": scores}
