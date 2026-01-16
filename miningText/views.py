import io
from django.http import HttpResponse
import pandas as pd # pour le excel pdf

from django.template.loader import get_template
from xhtml2pdf import pisa # pour le  pdf

from django.shortcuts import render
from .utils import extract_text_from_file
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q

from django.core.paginator import Paginator


from .utils import analyse_texte

from django.shortcuts import render, get_object_or_404, redirect
from .models import Article


def export_excel(request, id):
    article = get_object_or_404(Article, id=id)
    analyse = analyse_texte(article.contenu)

    df = pd.DataFrame(analyse["frequences"], columns=["Mot", "Occurrences"])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Analyse")
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename=analyse_article_{id}.xlsx'
    return response


def export_pdf(request, id):
    article = get_object_or_404(Article, id=id)
    analyse = analyse_texte(article.contenu)

    template = get_template("miningText/pdf_template.html")
    html = template.render({
        "article": article,
        "analyse": analyse,
        "mots_affiches": len(analyse["frequences"])
    })

    # Créer un buffer pour PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), dest=result)
    
    if pdf.err:
        return HttpResponse("Erreur lors de la génération du PDF")

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="analyse_article_{id}.pdf"'
    return response

# READ - Lister tous les articles
def index(request):
    articles = Article.objects.order_by('-date_publication','-id')
    return render(request, 'miningText/index.html', {'articles': articles})

def search_articles_index(request):
    query = request.GET.get("q", "")

    articles = Article.objects.filter(
        Q(titre__icontains=query) |
        Q(auteur__icontains=query) |
        Q(contenu__icontains=query)
    ).order_by("-date_publication","-id")

    html = render_to_string(
        "miningText/partials/article_list_index.html",
        {"articles": articles},
        request=request
    )

    return JsonResponse({"html": html})

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
    articles = Article.objects.all().order_by('-date_publication','-id')

    return render(
        request,
        "miningText/transform.html",
        {"articles": articles}
    )


def transform_ajax(request, id):
    article = get_object_or_404(Article, id=id)
    analyse = analyse_texte(article.contenu)

    # Pagination sur les mots affichés
    page_number = request.GET.get("page", 1)
    paginator = Paginator(analyse["frequences"], 12)  # 20 mots par page
    page_obj = paginator.get_page(page_number)

    # Contenu de l'article
    article_html = render_to_string(
        "miningText/partials/article_content.html",
        {"article": article},
        request=request
    )

    # Analyse avec pagination
    analyse_html = render_to_string(
        "miningText/partials/article_analyse.html",
        {
            "analyse": analyse,
            "page_obj": page_obj,
            "article": article,
            "mots_affiches": len(analyse["frequences"])  # Nombre total de mots affichables
        },
        request=request
    )

    return JsonResponse({
        "article_html": article_html,
        "analyse_html": analyse_html,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "mots_affiches": len(analyse["frequences"])
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

        source = request.POST.get("source")
        source_lien = request.POST.get("source_lien")

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
            date_publication=date_publication,
            source=source,
            source_lien=source_lien
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
        article.date_publication = request.POST.get('date_publication')
        article.source = request.POST.get('source')
        article.source_lien = request.POST.get('source_lien')
        article.save()
        return redirect('detail', id=article.id)
    
    return render(request, 'miningText/update.html', {'article': article})

# DELETE - Supprimer un article
def delete(request, id):
    article = get_object_or_404(Article, id=id)
    
    if request.method == 'POST':
        article.delete()
        return redirect('analyse')
    
    return render(request, 'miningText/delete.html', {'article': article})