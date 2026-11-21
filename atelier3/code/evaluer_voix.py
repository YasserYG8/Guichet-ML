"""La chaine complete : message vocal -> Whisper -> texte -> classifieur -> categorie.

    python evaluer_voix.py texte                            # point de reference : le texte lu
    python evaluer_voix.py whisper-large-v3-turbo           # francais impose
    python evaluer_voix.py whisper-large-v3-turbo auto      # Whisper devine la langue
    python evaluer_voix.py whisper-large-v3
    python evaluer_voix.py whisper-large-v3-turbo fr reelles   # vos enregistrements

Transcriptions et classifications sont gardees en cache : relancer ne coute rien.
"""
import csv
import json
import sys
import time
from pathlib import Path

import mutagen

from classifieur import classer
from evaluation import afficher_rapport
from transcription import transcription_en_cache
from verifier_enregistrements import verifier_fichier
from wer import detail, normaliser, wer

MODELE_TEXTE = "qwen/qwen3.8-27b"   # le classifieur retenu a l'atelier 2
PAUSE_WHISPER = 3.5                 # 20 requetes / minute sur le palier gratuit
PAUSE_TEXTE = 2.5                   # 30 requetes / minute et 8 000 tokens / minute
DATA = Path("../data")


def charger_messages():
    with open(DATA / "messages.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def nom_fichier(texte):
    return "".join(c if c.isalnum() or c in "-._" else "_" for c in texte)


# ------------------------------------------------------------ classification
def classer_avec_cache(textes):
    """Classe chaque texte ; un texte deja vu n'est pas renvoye au modele."""
    chemin = DATA / "classifications" / f"{nom_fichier(MODELE_TEXTE)}.json"
    cache = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
    predits, latences = [], []
    for i, texte in enumerate(textes, 1):
        if texte not in cache:
            debut = time.time()
            categorie = classer(texte, MODELE_TEXTE)
            cache[texte] = {"categorie": categorie, "latence_s": round(time.time() - debut, 2)}
            chemin.parent.mkdir(exist_ok=True)
            chemin.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
            time.sleep(PAUSE_TEXTE)
        predits.append(cache[texte]["categorie"])
        latences.append(cache[texte]["latence_s"])
        print(f"\r  classification {i}/{len(textes)}", end="", flush=True)
    print()
    return predits, latences


# ------------------------------------------------------------ transcription
def transcrire_tout(fichiers, modele, langue):
    textes, latences, secondes = [], [], 0.0
    for i, fichier in enumerate(fichiers, 1):
        texte, latence, en_cache = transcription_en_cache(fichier, modele, langue)
        textes.append(texte)
        latences.append(latence)
        secondes += max(10.0, mutagen.File(fichier).info.length)   # 10 s facturees au minimum
        print(f"\r  transcription {i}/{len(fichiers)}", end="", flush=True)
        if not en_cache:
            time.sleep(PAUSE_WHISPER)
    print()
    return textes, latences, secondes


def mesurer_wer(references, transcriptions):
    refs_n = [normaliser(r) for r in references]
    hyps_n = [normaliser(t) for t in transcriptions]
    return {"wer_brut": wer(references, transcriptions),
            "wer": wer(refs_n, hyps_n),
            "wer_par_message": [detail(r, h)["wer"] for r, h in zip(refs_n, hyps_n)]}


def enregistrer(resume, nom):
    Path("resultats").mkdir(exist_ok=True)
    chemin = Path("resultats") / f"{nom_fichier(nom)}.json"
    chemin.write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nresultat enregistre dans {chemin}")


# ------------------------------------------------------------ les trois modes
def evaluer_texte():
    messages = charger_messages()
    textes = [m["texte_oral"] for m in messages]
    vrais = [m["categorie"] for m in messages]
    predits, latences = classer_avec_cache(textes)
    resume = afficher_rapport("texte lu -> " + MODELE_TEXTE, vrais, predits)
    resume.update(etiquette="texte", canal="texte", modele="-", langue="-",
                  ids=[m["id"] for m in messages], vrais=vrais, predits=predits,
                  textes=textes, latence_s=round(sum(latences) / len(latences), 2))
    print(f"\nlatence moyenne par ticket : {resume['latence_s']:.2f} s")
    enregistrer(resume, "texte")


def evaluer_voix(modele, langue):
    messages = charger_messages()
    references = [m["texte_oral"] for m in messages]
    vrais = [m["categorie"] for m in messages]
    transcriptions, lat_asr, secondes = transcrire_tout([DATA / m["fichier"] for m in messages],
                                               modele, langue)
    mesures = mesurer_wer(references, transcriptions)
    print(f"\nWER sans normalisation : {mesures['wer_brut']:.3f}")
    print(f"WER normalise          : {mesures['wer']:.3f}")
    par_voix = {}
    for v in sorted({m["voix"] for m in messages}):
        idx = [i for i, m in enumerate(messages) if m["voix"] == v]
        par_voix[v] = wer([normaliser(references[i]) for i in idx],
                          [normaliser(transcriptions[i]) for i in idx])
        print(f"   voix {v:<8}: {par_voix[v]:.3f}  ({len(idx)} messages)")
    print(f"secondes audio facturees : {secondes:.0f}")

    predits, lat_texte = classer_avec_cache(transcriptions)
    etiquette = f"voix__{modele}__{langue or 'auto'}"
    resume = afficher_rapport(f"{modele} ({langue or 'auto'}) -> {MODELE_TEXTE}", vrais, predits)
    resume.update(mesures)
    resume.update(etiquette=etiquette, canal="voix", modele=modele, langue=langue or "auto",
                  ids=[m["id"] for m in messages], vrais=vrais, predits=predits,
                  textes=transcriptions, wer_par_voix=par_voix,
                  secondes_audio=round(secondes),
                  latence_s=round((sum(lat_asr) + sum(lat_texte)) / len(messages), 2))
    print(f"\nlatence moyenne par message : {resume['latence_s']:.2f} s "
          f"(Whisper {sum(lat_asr) / len(messages):.2f} s + classification "
          f"{sum(lat_texte) / len(messages):.2f} s)")
    enregistrer(resume, etiquette)


def evaluer_reelles(modele, langue):
    messages = {m["id"]: m for m in charger_messages()}
    fichiers = sorted(f for f in (DATA / "voix_reelles").glob("*.*")
                      if verifier_fichier(f, messages)[0] != "erreur")
    if not fichiers:
        sys.exit("aucun enregistrement dans data/voix_reelles/ : "
                 "lancez d'abord python verifier_enregistrements.py")
    ids = [f.stem for f in fichiers]
    references = [messages[i]["texte_oral"] for i in ids]
    reelles, _, secondes = transcrire_tout(fichiers, modele, langue)
    synthese, _, _ = transcrire_tout([DATA / messages[i]["fichier"] for i in ids], modele, langue)
    m_reel = mesurer_wer(references, reelles)
    m_synth = mesurer_wer(references, synthese)
    predits, _ = classer_avec_cache(reelles)

    print(f"\n{'id':<6}{'WER synthese':>14}{'WER voix reelle':>17}   categorie -> predite")
    for k, i in enumerate(ids):
        print(f"{i:<6}{m_synth['wer_par_message'][k]:>14.2f}{m_reel['wer_par_message'][k]:>17.2f}"
              f"   {messages[i]['categorie']} -> {predits[k]}")
    print(f"{'total':<6}{m_synth['wer']:>14.3f}{m_reel['wer']:>17.3f}")
    for k, i in enumerate(ids):
        print(f"\n{i}  lu      : {references[k]}\n      entendu : {reelles[k]}")
    enregistrer({"etiquette": f"voix_reelles__{modele}__{langue or 'auto'}",
                 "canal": "voix reelle", "modele": modele, "ids": ids,
                 "wer": m_reel["wer"], "wer_synthese_memes_ids": m_synth["wer"],
                 "textes": reelles, "predits": predits,
                 "vrais": [messages[i]["categorie"] for i in ids],
                 "secondes_audio": round(secondes)},
                f"voix_reelles__{modele}__{langue or 'auto'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "texte":
        evaluer_texte()
    else:
        langue = sys.argv[2] if len(sys.argv) > 2 else "fr"
        langue = None if langue == "auto" else langue
        if len(sys.argv) > 3 and sys.argv[3] == "reelles":
            evaluer_reelles(sys.argv[1], langue)
        else:
            evaluer_voix(sys.argv[1], langue)
