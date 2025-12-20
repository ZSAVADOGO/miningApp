from django.shortcuts import render
from .utils import extract_text_from_file
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q




#Pour l'annalyse et le 
import nltk
#nltk.download('punkt')
#nltk.download('stopwords')

from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from .utils import analyse_texte

# Create your views here.
from django.http import HttpResponse


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Article




# READ - Lister tous les articles
def index(request):
    articles = Article.objects.order_by('-id')
    return render(request, 'miningText/index.html', {'articles': articles})

# Recherche - 
def search_articles(request):
    q = request.GET.get("q", "").strip()

    articles = Article.objects.all()

    if q:
        articles = articles.filter(
            Q(titre__icontains=q) |
            Q(auteur__icontains=q) |
            Q(contenu__icontains=q)
        )

    return render(
        request,
        "miningText/partials/article_list.html",
        {"articles": articles}
    )

# Transform - Afficher le module Transform
def transform(request):
    articles = Article.objects.all().order_by('-id')

    return render(
        request,
        "miningText/transform.html",
        {"articles": articles}
    )


def transform_ajax(request, id):
    article = get_object_or_404(Article, id=id)
    analyse = analyse_texte(article.contenu)

    article_html = render_to_string(
        "miningText/partials/article_content.html",
        {"article": article},
        request=request
    )

    analyse_html = render_to_string(
        "miningText/partials/article_analyse.html",
        {"analyse": analyse},
        request=request
    )

    return JsonResponse({
        "article_html": article_html,
        "analyse_html": analyse_html
    })





# READ - Afficher un article
def detail(request, id):
    article = get_object_or_404(Article, id=id)
    return render(request, 'miningText/detail.html', {'article': article})

# CREATE - Afficher le formulaire
def create(request):
    if request.method == "POST":
        titre = request.POST.get("titre")
        auteur = request.POST.get("auteur")
        date_publication = request.POST.get("date_publication")
        contenu = request.POST.get("contenu", "")

        discours_file = request.FILES.get("discours")

        if discours_file:
            texte_fichier = extract_text_from_file(discours_file)

            # Fusion intelligente
            contenu = contenu.strip()
            contenu = texte_fichier

        article = Article.objects.create(
            titre=titre,
            auteur=auteur,
            contenu=contenu,
            date_publication=date_publication
        )

        return redirect('detail', id=article.id)
    
    return render(request, 'miningText/create.html')

# UPDATE - Modifier un article
def update(request, id):
    article = get_object_or_404(Article, id=id)
    
    if request.method == 'POST':
        article.titre = request.POST.get('titre')
        article.contenu = request.POST.get('contenu')
        article.auteur = request.POST.get('auteur')
        article.save()
        return redirect('detail', id=article.id)
    
    return render(request, 'miningText/update.html', {'article': article})

# DELETE - Supprimer un article
def delete(request, id):
    article = get_object_or_404(Article, id=id)
    
    if request.method == 'POST':
        article.delete()
        return redirect('transform')
    
    return render(request, 'miningText/delete.html', {'article': article})