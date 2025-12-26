import pdfplumber
from docx import Document

import unicodedata

import re

from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Mots politiques / idéologiques à fort impact
MOTS_FORTS = {
    "etat", "nation", "peuple", "jeunesse", "democratie", "liberte",
    "securite", "justice", "reforme", "gouvernance",
    "developpement", "education", "emploi", "economie",
    "sante", "paix", "stabilite", "avenir", "responsabilite",
    "solidarite", "progres", "investissement", "transparence",
    "croissance", "territoire", "citoyen", "institution",
    "inclusion", "egalite", "diversite", "cohesion"
}

# Stopwords étendus (normalisés)
STOP_WORDS_PERSO = {
    "plus", "cela", "cette", "tres", "aussi", "tant", "comme", "ainsi",
    "etre", "avoir", "faire", "dire", "aller",
    "monsieur", "madame", "chers", "cheres",
    "tous", "tout", "toute", "toutes",
    "autre", "autres", "leur", "leurs",
    "mesdames", "messieurs",
    "ceux", "celles", "fois", "jours",
    "annee", "annees", "depuis", "pendant",
    "certain", "certaines", "peu", "peut", "peuvent",
    "mettre", "voir", "donner", "venir", "prendre",
    "vouloir", "falloir", "trouver", "laisser",
    "croire", "partir", "arriver", "sans"
    "sommes", "etes", "suis", "es",
    "parce",
    "parceque", "quand", "lorsque", "puisque",
    "toutefois", "cependant", "neanmoins",
    
}

STOP_WORDS_PERSO.update({
    "mais", "avec", "pour", "dans", "jusqu",
    "sans", "entre", "par", "sur",
    "ainsi", "donc", "alors", "car"
})

STOP_WORDS_PERSO.update({
    "etre", "sont", "est", "ete", "sera",
    "avoir", "avons", "ont", "avait",
    "aller", "vais", "va", "allons",
    "faire", "fait", "font",
    "falloir", "faut", "faudra"
})

STOP_WORDS_PERSO.update({
    "nous", "vous", "ils", "elles", "on",
    "nos", "vos", "leurs",
    "notre", "votre", "leur",
    "moi", "toi", "lui", 
    "meme", "memes",
    "mon", "ton", "son",
    "ma", "ta", "sa",
    "me", "te", "se", "le", "la", "les",
    "je", "tu", "il", "elle",
    "ce", "cet", "cette", "ces",
    "celui", "celle", "ceux"
})

MOTS_AFFICHAGE_MAJ = {
    "dieu": "Dieu",
    "etat": "État",
    "nation": "Nation",
    "republique": "République",
    "constitution": "Constitution"
}


def normaliser(mot: str) -> str:
    """
    Normalise un mot pour l'analyse :
    - minuscules
    - suppression des accents
    - gestion œ / æ
    """
    mot = mot.lower()
    mot = mot.replace("œ", "oe").replace("æ", "ae")

    mot = unicodedata.normalize("NFD", mot)
    mot = "".join(c for c in mot if unicodedata.category(c) != "Mn")

    return mot



def pre_nettoyage_texte(texte: str) -> str:
    texte = texte.replace("’", "'")
    texte = re.sub(r"\b[lLdD]'"," ", texte)   # l'hiver → hiver
    texte = texte.lower()
    texte = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s-]", " ", texte)
    return texte


def analyse_texte(texte: str):

    texte = pre_nettoyage_texte(texte)

    tokens = [
        normaliser(m)
        for m in word_tokenize(texte, language="french")
        if m.isalpha()
    ]

    total_mots = len(tokens)

    mots_pertinents = [
        mot for mot in tokens
        if mot not in STOP_WORDS_PERSO and len(mot) >= 4
    ]

    compteur = Counter(mots_pertinents)

    # 🔹 seuil dynamique
    if total_mots < 200:
        seuil = 1
    elif total_mots < 600:
        seuil = 2
    else:
        seuil = 3

    frequences = []
    for mot, freq in compteur.items():
        if freq >= seuil:
            mot_affiche = MOTS_AFFICHAGE_MAJ.get(mot, mot)
            frequences.append((mot_affiche, freq))

    frequences.sort(key=lambda x: x[1], reverse=True)

    return {
        "total_mots_contenu": total_mots,
        "total_mots_pertinents": len(mots_pertinents),
        "seuil": seuil,
        "frequences": frequences[:20]
    }



def analyse_texte2(texte):
    texte = texte.lower()
    tokens = [m for m in word_tokenize(texte) if m.isalpha()]

    total_mots = len(tokens)

    stop_words = set(stopwords.words("french"))
    stop_words.update({
        "plus", "cela","cette", "aussi", "tant", "comme", "ainsi",
        "être", "avoir", "faire", "dire", "aller"
    })

    mots_impact = [
        mot for mot in tokens
        if mot not in stop_words and len(mot) >= 4
    ]

    compteur = Counter(mots_impact)

    # 🎯 seuil adaptatif
    if total_mots < 100:
        seuil = 1
    elif total_mots < 500:
        seuil = 2
    else:
        seuil = 3

    mots_significatifs = {
        mot: freq for mot, freq in compteur.items()
        if freq >= seuil
    }

    return {
        "total_mots_contenu": total_mots,
        "total_mots_pertinents": sum(mots_significatifs.values()),
        "frequences": Counter(mots_significatifs).most_common(20),
        "seuil_utilise": seuil
    }



def extract_text_from_file(uploaded_file):
    name = uploaded_file.name.lower()

    # TXT
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    # PDF
    elif name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    # DOCX
    elif name.endswith(".docx"):
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        return "⚠️ Format de fichier non supporté."
