# Atelier 3 — La voix et l'image

Ce dossier contient ce que vous ne pouvez pas produire vous-mêmes : les messages
vocaux, les captures d'écran, le classifieur de l'atelier 2 et le code qui ne fait
qu'afficher ou boucler. Ce qui porte un raisonnement, vous l'écrivez en séance.



## Déroulement des 3 heures

###### Activité	Durée	Travail demandé

###### 1\. Présentation et préparation	10 min	Comprendre les deux chaînes : voix → Whisper → classifieur ; image → modèle de vision.

###### 2\. Transcription audio	20 min	Compléter transcrire() et tester T016 et T006. Comparer le texte obtenu avec texte\_oral.

###### 3\. Mesure du WER	25 min	Compléter normaliser(), lancer les tests et calculer le WER. Identifier S, D et I.

###### 4\. Évaluation de la chaîne vocale	25 min	Comparer les résultats du classifieur sur le texte de référence et sur les transcriptions Whisper.

###### 5\. Propagation des erreurs	20 min	Compléter propagation(). Identifier deux tickets dont la catégorie change après transcription.

###### 6\. Classification d’image	35 min	Compléter classer\_image(), tester une capture puis évaluer les 20 images.

###### 7\. Comparaison des trois canaux	20 min	Compléter le tableau texte / voix / image avec les résultats obtenus.

###### 8\. Conclusion	10 min	Répondre aux questions de bilan.

###### Marge technique	15 min	Temps réservé aux installations, erreurs ou limites de débit.



## Contenu

&#x20;   data/messages.csv            72 messages : id, fichier, voix, texte\_oral, categorie
data/voix/                   les 72 messages vocaux (mp3, qualité téléphone)
data/images.csv              20 captures : id, fichier, categorie, ambigu
data/captures/               les 20 captures d'écran (png)

&#x20;   code/evaluation.py           fourni — métriques de l'atelier 2
code/classifieur.py          fourni — le classifieur de l'atelier 2
code/evaluer\\\_voix.py         fourni — la chaîne voix -> Whisper -> classifieur
code/evaluer\\\_images.py       fourni — la boucle sur les 20 captures
code/comparer.py             fourni — le tableau des canaux
code/verifier\\\_enregistrements.py   fourni — contrôle vos fichiers, sans quota
code/test\\\_wer.py, test\\\_propagation.py   vérifient votre code, sans quota





## Ce que vous allez écrire

&#x20;   code/transcription.py   étape 1 — transcrire()
code/wer.py             étape 2 — normaliser()
code/propagation.py     étape 4 — propagation()
code/vision.py          étape 7 — classer\_image()



## Mise en route

&#x20;   python -m pip install groq jiwer mutagen
export GROQ\_API\_KEY=gsk\_votre\_cle       # la clé de l'atelier 2
cd code
python transcription.py ../data/voix/T016.mp3



## Quotas du palier gratuit (par clé)

&#x20;   Whisper     20 requêtes / minute     -> 3,5 s entre deux messages
7 200 s audio / heure    une évaluation des 72 messages \~ 730 s
10 s facturées au minimum par fichier
qwen3.8     8 000 tokens / minute    un texte \~300 tokens, une image \~2 000
200 000 tokens / jour



Transcriptions et classifications sont gardées en cache dans data/ :
relancer une évaluation ne coûte rien. Ne supprimez pas ces dossiers en séance.

## À la fin du module

Supprimez data/voix\_reelles/ et data/transcriptions/voix\_reelles\_\_\* :
ce sont vos voix.

