"""Mesurer les erreurs de transcription : le WER (Word Error Rate).

On aligne la transcription sur la reference, mot a mot, et on compte :
  S  substitutions : un mot remplace par un autre   (facture -> fracture)
  D  deletions     : un mot oublie                  (je ne recois -> je recois)
  I  insertions    : un mot en trop                 (... merci d'avoir regarde)

  WER = (S + D + I) / N      N = nombre de mots de la reference

WER = 0 : transcription parfaite. Il peut depasser 1 si Whisper invente beaucoup.
"""
import re

import jiwer


# ---------------------------------------------------------------- a ecrire
def normaliser(texte):
    """Met reference et transcription dans la meme forme avant de les comparer.

    Ce qui n'est pas une erreur d'ecoute ne doit pas compter comme une erreur :
    majuscules, ponctuation, apostrophes, tirets, symbole euro.
    """
    # minuscules, apostrophe typographique, euro -> euros,
    # apostrophes et tirets -> espace, ponctuation -> espace, espaces multiples

    texte = texte.lower()

    texte = texte.replace("\u2019", "'") 
    texte = texte.replace("\u20ac", " euros ")

    texte = re.sub(r"['-]", " ", texte)
    texte = re.sub(r"[^\w\s]", "", texte)

    return " ".join(texte.split())
   

# ---------------------------------------------------------------- fourni
def wer(references, hypotheses):
    """WER d'un corpus : toutes les erreurs divisees par tous les mots de reference.

    Ce n'est PAS la moyenne des WER par message : un message de 2 mots ne pese
    pas autant qu'un message de 40 mots.
    """
    return jiwer.wer(list(references), list(hypotheses))


def detail(reference, hypothese):
    """S, D, I et WER d'un seul message."""
    m = jiwer.process_words(reference, hypothese)
    return {"S": m.substitutions, "D": m.deletions, "I": m.insertions,
            "N": len(reference.split()), "wer": m.wer}


def afficher_alignement(reference, hypothese):
    """Montre l'alignement mot a mot : REF au-dessus, transcription dessous."""
    m = jiwer.process_words(reference, hypothese)
    lignes = jiwer.visualize_alignment(m, show_measures=False).splitlines()
    print("\n".join(l for l in lignes if l.strip() and not l.startswith("===")))


if __name__ == "__main__":
    ref = "Ma facture de mars est de 89 euros. Pouvez-vous m'expliquer ?"
    hyp = "ma facture de mars et de 89 € pouvez vous m'expliquer"
    print("brut       :", round(wer([ref], [hyp]), 3))
    print("normalise  :", round(wer([normaliser(ref)], [normaliser(hyp)]), 3))
    afficher_alignement(normaliser(ref), normaliser(hyp))
