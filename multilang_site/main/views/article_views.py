""" Articles views """

from django.db.models import QuerySet
from django.shortcuts import render
from django.utils import translation
from pgvector.django import CosineDistance
from main.models import Article
from django.views.generic import View
from django_htmx.http import reswap
from main.assistant import distance_search


def base(request):
    """ View returning the base layout of the app and loading the articles view, used as a default.

    Returns:
        render (HttpResponse): rendered base layout with 'articles' view URL in context.
    """

    context = {"view": "/articles?page=1"}
    return render(request, "main/base_layout.html", context=context)


class ArticlesView(View):
    """ Article views depending on request type """

    def get(self, request):
        """ Response to a GET request.
        Checks if request was triggered by HTMX, if not return base_layout, allowing full page refreshes.

        Returns:
            render_0 (HttpResponse): rendered base_layout with 'articles' view in context.
            render_1 (HttpResponse): rendered articles template.
        """

        if not request.htmx:
            return render(request, "main/base_layout.html", context={"view": "/articles?page=1"})

        page = int(request.GET.get('page', ''))
        first_article: int = ((page - 1) * 10) if page > 1 else 0

        lang: str = translation.get_language()

        translation.activate(lang)

        articles_len: int = Article.objects.count()

        if first_article >= articles_len:
            res = render(request, "main/articles/reached_end.html")
            reswap(res, "outerHTML")

            return res

        last_article: int = (page * 10) if page else 10
        last_article = last_article if last_article <= articles_len else (
            articles_len)

        articles: QuerySet = Article.objects.order_by(
            "-publication_date")[first_article:last_article]

        context = {"articles": articles,
                   "current_page": page, "next_page": (page + 1), "heading": "Latest articles"}

        return render(request, "main/articles/articles.html", context)


def article(request):
    """ Full article view. """
    
    article_id = request.GET.get("id")
    article = Article.objects.get(id=article_id)

    if not request.htmx:
        return render(request, "main/base_layout.html", context={"view": f"/article/?id={article_id}"})

    similar_articles = Article.objects.annotate(
        distance=CosineDistance("embedding", article.embedding)
    ).order_by("distance")[1:6]

    context = {"article": article, "similar_articles": similar_articles}
    return render(request, template_name="main/articles/article.html", context=context)


def search(request):
    """ Return search results.

    Returns:
        res (HttpResponse): rendered articles template and URL params.
        render (HttpResponse): rendered base layout with 'search' view in context.
    """

    query: str = request.GET.get("query")

    if not request.htmx:
        context = {"view": f"/search?query={query}"}
        return render(request, "main/base_layout.html", context)

    articles: QuerySet = distance_search(query)
    context = {"articles": articles, "heading": f"Results for '{query}'"}

    res = render(request, "main/articles/articles.html", context)
    res['HX-Push-Url'] = f"/search/?query={query}"

    return res
