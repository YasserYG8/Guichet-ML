"""Evalue le modele de vision sur les 20 captures d'ecran.

    python evaluer_images.py

Chaque reponse est gardee en cache : relancer ne coute rien.
"""
import csv
import json
import time
from pathlib import Path

from groq import RateLimitError

from evaluation import afficher_rapport
from vision import MODELE_VISION, classer_image

PAUSE = 16          # une image + la consigne ~ 2 000 tokens ; limite : 8 000 tokens / minute
DATA = Path("../data")


def classer_avec_cache(chemin):
    fichier_cache = DATA / "classifications" / "images.json"
    cache = json.loads(fichier_cache.read_text(encoding="utf-8")) if fichier_cache.exists() else {}
    cle = f"{MODELE_VISION}|{chemin.name}"
    if cle in cache:
        return cache[cle]["categorie"], cache[cle]["latence_s"]
    for tentative in range(4):
        try:
            debut = time.time()
            categorie = classer_image(chemin)
            latence = round(time.time() - debut, 2)
            break
        except RateLimitError:
            attente = 20 * (tentative + 1)
            print(f"\n  quota atteint, pause de {attente} s")
            time.sleep(attente)
    else:
        raise RuntimeError("quota toujours atteint apres 4 tentatives")
    cache[cle] = {"categorie": categorie, "latence_s": latence}
    fichier_cache.parent.mkdir(exist_ok=True)
    fichier_cache.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(PAUSE)
    return categorie, latence


def main():
    with open(DATA / "images.csv", encoding="utf-8") as f:
        images = list(csv.DictReader(f))
    vrais, predits, latences = [], [], []
    for i, img in enumerate(images, 1):
        categorie, latence = classer_avec_cache(DATA / img["fichier"])
        vrais.append(img["categorie"])
        predits.append(categorie)
        latences.append(latence)
        print(f"\r{i}/{len(images)} captures", end="", flush=True)
    print()
    resume = afficher_rapport(f"captures -> {MODELE_VISION}", vrais, predits)

    print("\nCaptures mal classees")
    for img, p in zip(images, predits):
        if p != img["categorie"]:
            marque = " (ambigue)" if img["ambigu"] == "1" else ""
            print(f"   {img['id']}  attendu {img['categorie']:<12} predit {p}{marque}")

    resume.update(etiquette=f"image__{MODELE_VISION}", canal="image", modele=MODELE_VISION,
                  langue="-", ids=[img["id"] for img in images], vrais=vrais, predits=predits,
                  latence_s=round(sum(latences) / len(latences), 2))
    print(f"\nlatence moyenne par capture : {resume['latence_s']:.2f} s")
    Path("resultats").mkdir(exist_ok=True)
    chemin = Path("resultats") / f"image__{MODELE_VISION.replace('/', '_')}.json"
    chemin.write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"resultat enregistre dans {chemin}")


if __name__ == "__main__":
    main()
