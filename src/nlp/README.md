# Analyse syntaxique du texte extrait des pdfs trouvés sur data.gouv.fr

## Description

Ce dataset contient un analyse syntaxique pour les textes du dataset [Texte extrait des pdfs trouvés sur data.gouv.fr](https://www.data.gouv.fr/fr/datasets/texte-provenant-des-pdfs-trouves-sur-data-gouv-fr/)
Au total, il s'agit de 6526 fichiers JSON compatibles avec le format [CONLL-U](https://universaldependencies.org/format.html).

L'analyse a été réalisée avec la librairie NLP en Python [stanza](https://stanfordnlp.github.io/stanza/).
Spécifiquement, avec les modèles [gsd](https://universaldependencies.org/treebanks/fr_gsd/index.html) (pour la
tokenisation, la lemmatisation, l'extraction de dépendances, et les infos miscellanées) et [WikiNER](https://figshare.com/articles/Learning_multilingual_named_entity_recognition_from_Wikipedia/5462500) pour la
reconnaissance d'entités nommées.

**IMPORTANT**: Afin d'accelerer les analyses, seulement les premiers 350 Kb de chaque fichier sont lus.

Le résultat sont de fichiers `json` provenant des `txt` triés par organisation (l'organisation qui a publié la ressource).
Le nom de chaque fichier correspond au string `{id-du-dataset}--{id-de-la-ressource}.json`.

#### Input
Dataset [Texte extrait des pdfs trouvés sur data.gouv.fr](https://www.data.gouv.fr/fr/datasets/texte-provenant-des-pdfs-trouves-sur-data-gouv-fr/).

#### Output
Fichiers JSON pour chaque fichier type `txt` trouvée dans le dataset qui a été analysé avec succès.
Chaque fichier contient une liste de phrases. Chaque phrase corresponde à une liste de *mots*. Chaque mot contient les informations suivantes :
- **id** : son identifiant dans la phrase ;
- **texte** : le texte brut du mot ;
- **lemma** : le lemme du mot ;
- **head** : la tête de la relation de dépendance ;
- **deprel** : le type de la relation de dépendance ([Universal Dependencies](https://universaldependencies.org/));
- **misc** : des autres informations sur la nature du mot, tels que sa position de début/fin dans la phrase ;
- **ner** : entité nommée trouvé par le model (LOC: endroit, PER: personne, ORG: organisation, MISC: autre)


Bref aperçu d'un fichier :

```bash
[
    [
        {
            "id": "1",
            "text": "ACTES",
            "lemma": "ACTES",
            "upos": "NOUN",
            "feats": "Gender=Masc|Number=Plur",
            "head": 0,
            "deprel": "root",
            "misc": "start_char=47|end_char=52",
            "ner": "B-ORG"
        },
        {
            "id": "2",
            "text": "ADMINISTRATIFS",
            "lemma": "administratifs",
            "upos": "ADJ",
            "feats": "Gender=Masc|Number=Plur",
            "head": 1,
            "deprel": "amod",
            "misc": "start_char=53|end_char=67",
            "ner": "E-ORG"
        },
        ...
    ],
    ...
]
```

### Code
Les scripts Python utilisés pour faire cette extraction sont [ici](https://github.com/psorianom/data_gouv_text).

### Remarques
Dû à la qualité des pdfs d'origine, à la performance des méthodes de transformation pdf-->txt,
et à la qualité des modèles d'analyse syntaxique/reconnaissance d'entités nommées, les résultats peuvent être très bruités.