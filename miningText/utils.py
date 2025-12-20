import pdfplumber
from docx import Document

from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def analyse_texte(texte):
    # Tokenisation brute
    mots_bruts = word_tokenize(texte.lower())

    total_mots_bruts = len([m for m in mots_bruts if m.isalpha()])

    stop_words = set(stopwords.words('french'))
    stop_words_perso = [
        'cette', 'a', 'donc', 'est', 'il', 'elle',
        'les', 'des', 'pour', 'dans'
    ]
    stop_words.update(stop_words_perso)

    mots_filtres = [
        mot for mot in mots_bruts
        if mot.isalpha() and mot not in stop_words
    ]

    compteur = Counter(mots_filtres)

    return {
        "total_mots_contenu": total_mots_bruts,
        "total_mots_pertinents": len(mots_filtres),
        "frequences": compteur.most_common(20)
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
