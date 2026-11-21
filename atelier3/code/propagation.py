"""Ou se perdent les tickets ? Le texte lu et sa transcription, ticket par ticket.

    python propagation.py whisper-large-v3-turbo         # compare a resultats/texte.json
    python propagation.py whisper-large-v3-turbo auto

Sans appel reseau : on relit les resultats enregistres par evaluer_voix.py.
"""
import json
import sys


# ---------------------------------------------------------------- a ecrire
def propagation(vrais, predits_texte, predits_voix):
    """Range chaque ticket dans une des quatre cases, et renvoie leurs positions.

      "conserve"  : juste sur le texte, juste sur la voix
      "perdu"     : juste sur le texte, faux sur la voix   <- erreur venue de l'audio
      "gagne"     : faux sur le texte, juste sur la voix   <- hasard, pas un progres
      "deux_faux" : faux des deux cotes                    <- erreur du classifieur
    """
    cases = {"conserve": [], "perdu": [], "gagne": [], "deux_faux": []}
    for i, (v, t, a) in enumerate(zip(vrais, predits_texte, predits_voix)):
        texte_juste, voix_juste = (t == v), (a == v)
        if texte_juste and voix_juste:
            cases["conserve"].append(i)
        elif texte_juste:
            cases["perdu"].append(i)
        elif voix_juste:
            cases["gagne"].append(i)
        else:
            cases["deux_faux"].append(i)
    return cases


# ---------------------------------------------------------------- fourni
def charger(nom):
    with open(f"resultats/{nom}.json", encoding="utf-8") as f:
        return json.load(f)


def afficher_propagation(texte, voix):
    if texte["ids"] != voix["ids"]:
        sys.exit("les deux evaluations ne portent pas sur les memes tickets")
    vrais = texte["vrais"]
    cases = propagation(vrais, texte["predits"], voix["predits"])
    n = len(vrais)
    print(f"\n{'':<14}{'voix juste':>12}{'voix fausse':>13}")
    print(f"{'texte juste':<14}{len(cases['conserve']):>12}{len(cases['perdu']):>13}")
    print(f"{'texte faux':<14}{len(cases['gagne']):>12}{len(cases['deux_faux']):>13}")
    print(f"\n{len(cases['perdu'])} tickets perdus a cause de l'audio, "
          f"{len(cases['gagne'])} gagnes par hasard, sur {n}.")
    for i in cases["perdu"]:
        print(f"\n{voix['ids'][i]}  [{vrais[i]}]  voix -> {voix['predits'][i]}   "
              f"WER du message {voix['wer_par_message'][i]:.2f}")
        print(f"   lu      : {texte['textes'][i]}")
        print(f"   entendu : {voix['textes'][i]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage : python propagation.py <modele_whisper> [fr|auto]")
    langue = sys.argv[2] if len(sys.argv) > 2 else "fr"
    afficher_propagation(charger("texte"), charger(f"voix__{sys.argv[1]}__{langue}"))
