"""Verifie votre fonction normaliser(), sans reseau ni quota.

    python test_wer.py
"""
from wer import normaliser, wer

CAS = [
    ("Ça rame...", "ça rame"),
    ("Pouvez-vous m'expliquer la différence ?", "pouvez vous m expliquer la différence"),
    ("l’application plante", "l application plante"),
    ("89€", "89 euros"),
    ("89 €", "89 euros"),
    ("  Bonjour,   je  suis   là ! ", "bonjour je suis là"),
    ("Le code 'champ invalide'", "le code champ invalide"),
]

ok = 0
for entree, attendu in CAS:
    try:
        obtenu = normaliser(entree)
    except NotImplementedError:
        raise SystemExit("normaliser() n'est pas encore ecrite (etape 2)")
    if obtenu == attendu:
        ok += 1
    else:
        print(f"ECHEC  normaliser({entree!r})\n       attendu {attendu!r}\n       obtenu  {obtenu!r}")

ref = "Ma facture de mars est de 89 euros. Pouvez-vous m'expliquer ?"
hyp = "ma facture de mars et de 89 € pouvez vous m'expliquer"
w = wer([normaliser(ref)], [normaliser(hyp)])
if abs(w - 1 / 12) > 1e-9:
    print(f"ECHEC  WER apres normalisation : attendu 0.083 (1 erreur / 12 mots), obtenu {w:.3f}")
else:
    ok += 1
print(f"{ok}/{len(CAS) + 1} tests reussis")
