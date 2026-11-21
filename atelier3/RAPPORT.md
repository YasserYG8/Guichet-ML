# Atelier 3 — La voix et l'image : rapport

Classifieur texte : `qwen/qwen3.8-27b` (atelier 2). ASR : `whisper-large-v3-turbo`, `language="fr"`.
Modèle de vision : `qwen/qwen3.8-27b`. Tous les appels passent par le palier gratuit de Groq.

## A. Fichiers complétés

| Fichier | Fonction | Vérification |
| :--- | :--- | :--- |
| `code/transcription.py` | `transcrire()` : fichier ouvert en `"rb"`, `language` envoyé seulement s'il n'est pas `None` | T016 transcrit sans erreur |
| `code/wer.py` | `normaliser()` (et correction de l'import : `import re` au lieu de `from wer import re`) | `test_wer.py` : 8/8 ; `wer.py` : brut 0,545, normalisé 0,083 |
| `code/propagation.py` | `propagation()` : chaque ticket va dans une seule des 4 cases | `test_propagation.py` : 4/4 |
| `code/vision.py` | `classer_image()` : consigne + image (`data_url`) dans un message, JSON vérifié comme `classer()` | I06 → facturation (correct) |

## B. Résultats des évaluations

### Étape 1 — Transcription

- **T016** (`fr`) : transcription identique à `texte_oral`.
- **T006** : le texte lu est un seul mot, « stop ».
  - avec `language="fr"` → « Au revoir. »
  - avec `auto` → « All. »

`language="fr"` dit à Whisper la langue à attendre. Il ne perd pas de temps à la deviner, et il ne se trompe pas de langue sur un message très court. Mais sur un mot isolé et mal prononcé, Whisper peut quand même inventer une phrase française plausible.

### Étape 2 — WER

Phrase d'exemple : WER brut **0,545**, normalisé **0,083**. Après normalisation, il reste une seule erreur d'écoute : une substitution (S), `est → et`. Les autres « erreurs » venaient seulement de la ponctuation, des majuscules et du symbole €.

### Étape 3 — Chaîne vocale

| | WER | macro-F1 | Latence / message |
| :--- | :---: | :---: | :---: |
| Texte lu (référence) | — | 0,959 | 0,33 s |
| Voix → whisper-large-v3-turbo | 0,091 (brut 0,125) | 0,904 | 0,72 s (Whisper 0,34 s + classification 0,39 s) |
| Écart (en tickets) | | **4 tickets** (69 → 65 bien classés, −5,5 points) | ×2,2 |

WER par voix de synthèse : `mb-fr1` 0,011 · `mb-fr4` 0,048 · `fr` **0,214**.
Audio facturé : 725 s (10 s minimum par fichier).

### Étape 4 — Propagation des erreurs

| | voix juste | voix fausse |
| :--- | :---: | :---: |
| **texte juste** | 65 | **4** (perdus) |
| **texte faux** | 0 | 3 |

Les 4 tickets perdus viennent tous de la voix `fr` :

| Ticket | Vrai | Voix → | Lu | Entendu |
| :--- | :--- | :--- | :--- | :--- |
| T027 | technique | facturation | L'export CSV génère un fichier vide alors que j'ai bien des données affichées. | L'expansé est ce que je n'ai pas fait un affichier bidalon que j'ai bien dédonné l'affiché. |
| T030 | compte | technique | je n'arrive plus à rentrer | Je n'arrive plus à montrer. |
| T048 | compte | technique | Supprimez tout | Sous-titrage Société Radio-Canada |
| T051 | technique | compte | Vos serveurs sont down ? | Bofan m'eurent fou taul |

Deux tickets perdus en détail :

- **T030** : un seul mot est faux, « rentrer » → « montrer » (WER 0,17). Mais c'est le mot qui porte le sens. « Je n'arrive plus à rentrer » parle d'un accès au compte. « Je n'arrive plus à montrer » ressemble à une fonction qui ne marche pas. Le classifieur choisit donc `technique`. Un WER faible ne garantit pas une bonne catégorie : tout dépend du mot qui est faux.
- **T048** : Whisper n'a rien compris et a **halluciné** « Sous-titrage Société Radio-Canada », une phrase typique de ses données d'entraînement (WER 2,50 > 1). Le texte n'a plus aucun rapport avec une demande de suppression de données. Le classifieur ne peut rien rattraper.

Les 3 tickets « faux des deux côtés » (T004, T039, T041) sont déjà faux sur le texte lu : ce sont des erreurs du classifieur, pas de l'audio.

### Étape 5 — Captures d'écran

20/20 captures bien classées : macro-F1 **1,000**, 0 invalide, 3,47 s par capture. Il n'y a **aucune image mal classée** à examiner. Même les 3 captures marquées ambiguës (I05, I10, I17) sont correctes. La règle de la consigne (« une erreur technique sur une page de paiement → technique ») aide sur ces cas.

## C. Tableau comparatif des trois canaux

| Canal | Modèle | Qualité | Latence | Coût indicatif |
| :--- | :--- | :--- | :--- | :--- |
| Texte | Classifieur atelier 2 (qwen3.8-27b) | Macro-F1 : **0,959** (72 tickets) | 0,33 s | 1 appel, ~300 tokens |
| Voix | Whisper turbo + classifieur | WER : **0,091** / Macro-F1 : **0,904** | 0,72 s | 2 appels : ≥ 10 s d'audio facturées + ~300 tokens |
| Image | Modèle de vision (qwen3.8-27b) | Macro-F1 : **1,000** (20 captures) | 3,47 s | 1 appel, ~2 000 tokens |

Le coût est 0 € sur le palier gratuit. Il est donc exprimé en consommation de quota (limites : Whisper 7 200 s d'audio / heure ; qwen3.8 8 000 tokens / minute et 200 000 / jour).

## D. Questions de conclusion

**A. Quel canal donne le meilleur résultat ?**
L'image a le meilleur score (macro-F1 1,000 contre 0,959 pour le texte). Mais elle n'est évaluée que sur 20 captures : une seule erreur fait perdre 5 points. Sur 72 tickets, un ticket vaut seulement 1,4 point. L'écart de 4 points entre image et texte correspond donc à moins d'une image : il n'est pas mesurable. De plus, les captures ne sont pas les mêmes tickets. La conclusion sûre est donc : **le texte est la référence la plus fiable (0,959 sur 72 tickets)**, l'image fait au moins aussi bien sur son petit jeu, et **la voix est clairement en dessous (0,904, −4 tickets)**. L'image est aussi le canal le plus lent (×10 par rapport au texte) et le plus cher en tokens (×7).

**B. Pour la voix, les erreurs viennent-elles de la transcription ou de la classification ?**
Des deux, et on peut les compter séparément grâce à la propagation. Sur 7 tickets faux en voix :
- **4 viennent de la transcription** (texte juste, voix fausse) ;
- **3 viennent du classifieur** (déjà faux sur le texte lu).

La transcription ajoute donc 4 erreurs. Elles viennent toutes de la voix `fr` (WER 0,214, contre 0,011 et 0,048 pour les deux autres voix). Les messages courts sont les plus fragiles (« Supprimez tout », « Vos serveurs sont down ? ») : Whisper n'a pas assez de contexte et peut halluciner une phrase entière.

**C. Quelles vérifications avant d'utiliser ce système dans un vrai guichet ?**
- **Tester sur de vraies voix**, pas seulement des voix de synthèse : accents, bruit, téléphone, mots anglais (« down », « CSV »). La voix `fr` montre déjà que le WER peut être multiplié par 20 d'une voix à l'autre.
- **Détecter les hallucinations de Whisper** : messages très courts, texte sans rapport (« Sous-titrage… »), WER impossible à calculer en production. Envoyer ces cas à un humain (comme `requires_review` à l'atelier 1).
- **Mesurer sur plus de captures**, avec de vraies captures de clients (photos d'écran, mauvais cadrage). 20 images ne suffisent pas pour conclure.
- **Mesurer chaque étage séparément en continu** : WER pour l'ASR, macro-F1 pour la chaîne. Sinon on ne sait pas quel étage réparer.
- **Vérifier la latence et les quotas en charge** : le palier gratuit (20 requêtes Whisper / minute, 8 000 tokens / minute) ne tient pas un vrai volume.
- **Protéger les données personnelles** : les voix et les captures contiennent des informations sur les clients. Il faut l'accord des clients, une durée de conservation, et supprimer les caches (`data/transcriptions/`, `data/voix_reelles/`).

## Commandes pour reproduire

```bash
cd atelier3/code
python test_wer.py && python test_propagation.py      # sans quota
python evaluer_voix.py texte
python evaluer_voix.py whisper-large-v3-turbo
python propagation.py whisper-large-v3-turbo
python evaluer_images.py
python comparer.py
```

`GROQ_API_KEY` doit être une variable d'environnement : les scripts n'utilisent pas `.env`. Les résultats sont gardés en cache dans `data/transcriptions/` et `data/classifications/` : relancer ne coûte rien.
