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
    "depuis", "pendant",
    "certain", "certaines", "peu", "peut", "peuvent",
    "mettre", "voir", "donner", "venir", "prendre",
    "vouloir", "falloir", "trouver", "laisser",
    "croire", "partir", "arriver", "sans"
    "sommes", "etes", "suis", "es",
    "parce",
    "parceque", "quand", "lorsque", "puisque",
    "toutefois", "cependant", "neanmoins",

    "chaque","jour"
    
}

STOP_WORDS_PERSO.update({
    "mais", "avec", "pour", "dans", "jusqu",
    "sans", "entre", "par", "sur",
    "ainsi", "donc", "alors", "car"
})

STOP_WORDS_PERSO.update({
    "sont", "est", "ete", "sera",
    "avoir", "avons", "ont", "avait",
    "aller", "vais", "va", "allons",
    "faire", "fait", "font",
    "falloir", "faut", "faudra",
    "peut", "peuvent",
    
    "dire", "dit", "disent",
    "voir", "vu", "voient",

    "nous", "vous", "ils", "elles", "on",
    "nos", "vos", "leurs",
    "notre", "votre", "moi", "toi", 
    "meme", "memes",
    "mon", "ton", "son",
    "ma", "ta", "sa",
    "me", "te", "se", "le", "la", "les",
    "je", "tu", "il", "elle",
    "ce", "cet", "cette", "ces",
    "celui", "celle", "ceux",
    "soit", "soient","encore","aussi","trop","tres","bien",

    "sommes","etes","suis","es","et","ne","pas","plus","non","ni",
    "que","qui","quoi","dont","ou","lors","lorsqu","quand","comme",
    "si","y","en","lui","leur",
})

MOTS_AFFICHAGE_MAJ = {
    "dieu": "Dieu",
    "etat": "État",
    "nation": "Nation",
    "republique": "République",
    "constitution": "Constitution",
    "democratie": "Démocratie",
    "russie": "Russie",
    "france": "France",
    "fracais": "Français","francais": "Français","francaise": "Française","francaises": "Françaises", 
    "russe": "Russe","russes": "Russes",
    "amerique": "Amérique",
    "europe": "Europe",
    "afrique": "Afrique",
    "burkina": "Burkina", "burkinabe": "Burkinabe","burkinabes": "Burkinabes",
    "mpsr": "MPSR",
    "patrie": "Patrie",
    "ouagadougou": "Ouagadougou",
    "cedeao": "CEDEAO",
    "faso": "Faso",
    "niger": "Niger",
    "africain": "Africain","africains": "Africains",
    "africaine": "Africaine",
    "compatriotes": "Compatriotes","patriotes": "Patriotes",
}


def normaliser(mot: str) -> str:

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

# 🔹 Fonction principale
def analyse_texte(texte: str):
    texte = pre_nettoyage_texte(texte)

    # Tokenisation
    tokens = [
        normaliser(m)
        for m in word_tokenize(texte, language="french")
        if m.isalpha()
    ]

    total_mots = len(tokens)



    # Filtrage mots pertinents
    mots_pertinents = [
        mot for mot in tokens
        if mot not in STOP_WORDS_PERSO and len(mot) >= 4
    ]

    # Comptage occurrences
    compteur = Counter(mots_pertinents)

    # 🔹 Seuil dynamique basé sur les mots pertinents
    total_pertinents = sum(compteur.values())
    if total_pertinents < 200:
        seuil = 1
    elif total_pertinents < 460:
        seuil = 2
    else:
        seuil = 3

    # Préparer la liste des mots à afficher (après seuil)
    mots_affiches = []
    for mot, freq in compteur.items():
        if freq >= seuil:
            mot_affiche = MOTS_AFFICHAGE_MAJ.get(mot, mot)
            mots_affiches.append((mot_affiche, freq))

    # Tri par fréquence
    mots_affiches.sort(key=lambda x: x[1], reverse=True)

    return {
        "total_mots_contenu": total_mots,                # tous les mots du texte
        "total_mots_pertinents": sum(freq for _, freq in mots_affiches),  # somme occurrences filtrées
        "seuil": seuil,
        "frequences": mots_affiches                      # liste complète pour pagination
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
