"""Du son au texte : Whisper sur Groq.

    python transcription.py ../data/voix/T016.mp3
    python transcription.py ../data/voix/T016.mp3 whisper-large-v3 auto
"""
import json
import os
import sys
import time
from pathlib import Path

from groq import Groq, RateLimitError

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# Formats acceptes par l'API de transcription de Groq (25 Mo au maximum)
FORMATS = {".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".wav", ".webm"}
DOSSIER_CACHE = Path("../data/transcriptions")


# ---------------------------------------------------------------- a ecrire
def transcrire(chemin, modele, langue="fr"):
    """Envoie un fichier audio a Whisper et renvoie le texte transcrit.

    langue="fr" impose le francais ; langue=None laisse Whisper deviner la langue.
    """
    chemin = Path(chemin)
    with open(chemin, "rb") as f:          # un fichier audio se lit en binaire
        octets = f.read()
    options = {}
    if langue is not None:                 # None : Whisper detecte la langue seul
        options["language"] = langue
    reponse = client.audio.transcriptions.create(
        file=(chemin.name, octets),
        model=modele,
        temperature=0.0,
        **options,
    )
    return reponse.text.strip()


# ---------------------------------------------------------------- fourni
def transcription_en_cache(chemin, modele, langue="fr"):
    """Transcrit un fichier UNE fois : le resultat est garde dans data/transcriptions/.

    Renvoie (texte, latence en secondes, deja_en_cache). Relancer ne coute rien.
    """
    chemin = Path(chemin)
    if chemin.suffix.lower() not in FORMATS:
        raise ValueError(f"{chemin.name} : format refuse par Groq. "
                         f"Acceptes : {' '.join(sorted(FORMATS))}")
    dossier = DOSSIER_CACHE / f"{chemin.parent.name}__{modele}__{langue or 'auto'}"
    cache = dossier / f"{chemin.stem}.json"
    if cache.exists():
        d = json.loads(cache.read_text(encoding="utf-8"))
        return d["texte"], d["latence_s"], True
    for tentative in range(4):
        try:
            debut = time.time()
            texte = transcrire(chemin, modele, langue)
            latence = time.time() - debut
            break
        except RateLimitError:
            attente = 15 * (tentative + 1)
            print(f"\n  quota audio atteint, pause de {attente} s")
            time.sleep(attente)
    else:
        raise RuntimeError("quota toujours atteint apres 4 tentatives")
    dossier.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"texte": texte, "latence_s": round(latence, 2)},
                                ensure_ascii=False), encoding="utf-8")
    return texte, latence, False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage : python transcription.py <fichier audio> [modele] [fr|auto]")
    modele = sys.argv[2] if len(sys.argv) > 2 else "whisper-large-v3-turbo"
    langue = sys.argv[3] if len(sys.argv) > 3 else "fr"
    debut = time.time()
    print(transcrire(sys.argv[1], modele, None if langue == "auto" else langue))
    print(f"({time.time() - debut:.1f} s)")
