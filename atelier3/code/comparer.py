"""Toutes vos evaluations cote a cote : texte, voix, image.

    python comparer.py
"""
import glob
import json


def charger_tous():
    resumes = []
    for chemin in sorted(glob.glob("resultats/*.json")):
        with open(chemin, encoding="utf-8") as f:
            resumes.append(json.load(f))
    return resumes


def tableau(resumes):
    print(f"{'canal':<8}{'modele':<25}{'langue':<8}{'WER':>7}{'macro-F1':>10}"
          f"{'invalides':>11}{'n':>5}{'latence':>9}")
    print("-" * 85)
    for r in sorted(resumes, key=lambda x: (x["canal"], -x["f1_macro"])):
        wer = f"{r['wer']:.3f}" if "wer" in r else "-"
        n = len(r["ids"])
        print(f"{r['canal']:<8}{r['modele'][:24]:<25}{r['langue']:<8}{wer:>7}"
              f"{r['f1_macro']:>10.3f}{r['invalides']:>11.3f}{n:>5}{r['latence_s']:>8.2f}s")


def voix_reelles(resumes):
    for r in resumes:
        print(f"\n{r['etiquette']} : {len(r['ids'])} messages, "
              f"WER voix reelle {r['wer']:.3f} contre {r['wer_synthese_memes_ids']:.3f} "
              f"en synthese sur les memes tickets")


if __name__ == "__main__":
    tous = charger_tous()
    if not tous:
        raise SystemExit("aucun resultat dans resultats/ : lancez d'abord evaluer_voix.py")
    tableau([r for r in tous if r["canal"] != "voix reelle"])
    voix_reelles([r for r in tous if r["canal"] == "voix reelle"])
    print("\n1 ticket sur 72 = 1,4 point de macro-F1 ; 1 image sur 20 = 5 points.")
