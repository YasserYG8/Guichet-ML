"""Verifie vos enregistrements AVANT de les envoyer a Whisper.

    python verifier_enregistrements.py --liste 3   # les 5 textes a lire du binome n°3
    python verifier_enregistrements.py             # controle data/voix_reelles/

Aucun appel reseau, aucun quota consomme.
"""
import csv
import re
import sys
from pathlib import Path

import mutagen

DATA = Path("../data")
DOSSIER = DATA / "voix_reelles"
FORMATS = {".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".wav", ".webm"}
A_CONVERTIR = {".amr": "format de vieux dictaphone Android",
               ".3gp": "format video de vieux telephone",
               ".opus": "note vocale WhatsApp : renommez simplement le fichier en .ogg",
               ".aac": "AAC brut : choisissez .m4a dans les reglages de l'application",
               ".wma": "format Windows non accepte"}
TAILLE_CONSEILLEE = 2 * 1024 * 1024    # 2 Mo : largement assez pour 30 s
TAILLE_MAX = 25 * 1024 * 1024          # limite de l'API Groq
DUREE_MIN, DUREE_MAX = 1.0, 30.0
ECART = 14                             # binome n : tickets n, n+14, n+28, n+42, n+56


def charger_messages():
    with open(DATA / "messages.csv", encoding="utf-8") as f:
        return {m["id"]: m for m in csv.DictReader(f)}


def tickets_du_binome(numero):
    return [f"T{numero + k * ECART:03d}" for k in range(5)]


def lister(numero, messages):
    print(f"Binome n°{numero} : enregistrez ces 5 messages, mot pour mot.\n")
    for tid in tickets_du_binome(numero):
        print(f"{tid}.m4a   {messages[tid]['texte_oral']}\n")


def verifier_fichier(chemin, messages):
    """Renvoie (niveau, message) : niveau = "ok", "attention" ou "erreur"."""
    ext = chemin.suffix.lower()
    if ext in A_CONVERTIR:
        return "erreur", f"{ext} refuse par Groq ({A_CONVERTIR[ext]})"
    if ext not in FORMATS:
        return "erreur", f"extension {ext} inconnue (acceptees : {' '.join(sorted(FORMATS))})"
    if not re.fullmatch(r"T\d{3}", chemin.stem):
        return "erreur", "nom incorrect : renommez le fichier T016.m4a, T030.m4a..."
    if chemin.stem not in messages:
        return "erreur", f"{chemin.stem} n'existe pas dans messages.csv"
    taille = chemin.stat().st_size
    if taille > TAILLE_MAX:
        return "erreur", f"{taille / 1e6:.1f} Mo : depasse la limite de 25 Mo de l'API"
    try:
        duree = mutagen.File(chemin).info.length
    except Exception:
        duree = None
    if duree is None:
        return "attention", f"{taille / 1e3:.0f} Ko, duree illisible (fichier abime ?)"
    if duree < DUREE_MIN:
        return "erreur", f"{duree:.1f} s : presque vide, recommencez l'enregistrement"
    if duree > DUREE_MAX:
        return "erreur", f"{duree:.0f} s : trop long, coupez le silence ou recommencez"
    if taille > TAILLE_CONSEILLEE:
        return "attention", (f"{taille / 1e6:.1f} Mo pour {duree:.0f} s : qualite trop haute "
                             "(WAV ou 'lossless'), choisissez m4a qualite normale")
    return "ok", f"{duree:4.1f} s  {taille / 1e3:4.0f} Ko"


def verifier(messages):
    if not DOSSIER.exists():
        sys.exit(f"creez le dossier {DOSSIER} et copiez-y vos enregistrements")
    fichiers = sorted(f for f in DOSSIER.iterdir() if f.is_file() and not f.name.startswith("."))
    if not fichiers:
        sys.exit(f"{DOSSIER} est vide")
    erreurs = 0
    for f in fichiers:
        niveau, message = verifier_fichier(f, messages)
        erreurs += niveau == "erreur"
        print(f"{niveau.upper():<10}{f.name:<16} {message}")
    valides = [f for f in fichiers if verifier_fichier(f, messages)[0] != "erreur"]
    print(f"\n{len(valides)} fichiers utilisables sur {len(fichiers)}", end="")
    print(" : pret pour evaluer_voix.py" if erreurs == 0 else " : corrigez les erreurs")


if __name__ == "__main__":
    messages = charger_messages()
    if len(sys.argv) > 2 and sys.argv[1] == "--liste":
        lister(int(sys.argv[2]), messages)
    else:
        verifier(messages)
