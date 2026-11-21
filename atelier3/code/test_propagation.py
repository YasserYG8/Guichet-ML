"""Verifie votre fonction propagation(), sans reseau ni quota.

    python test_propagation.py
"""
from propagation import propagation

vrais   = ["facturation", "technique", "compte", "commercial", "technique", "compte"]
texte   = ["facturation", "technique", "compte", "technique",  "compte",    "compte"]
voix    = ["facturation", "compte",    "compte", "commercial", "compte",    "invalide"]

try:
    cases = propagation(vrais, texte, voix)
except NotImplementedError:
    raise SystemExit("propagation() n'est pas encore ecrite (etape 4)")

attendu = {"conserve": [0, 2], "perdu": [1, 5], "gagne": [3], "deux_faux": [4]}
ok = 0
for cle, positions in attendu.items():
    if sorted(cases.get(cle, [])) == positions:
        ok += 1
    else:
        print(f"ECHEC  case {cle!r} : attendu {positions}, obtenu {cases.get(cle)}")
total = sum(len(v) for v in cases.values())
if total != len(vrais):
    print(f"ECHEC  {total} tickets ranges au lieu de {len(vrais)} : chacun doit aller dans UNE case")
print(f"{ok}/4 cases correctes")
