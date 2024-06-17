from django.shortcuts import render
from django.utils.log import logging
from django.utils import translation
from main.models import Article
from django.views.generic import View
from django_htmx.http import reswap


def base(request):
    return render(request, "main/base_layout.html")


class ArticlesView(View):

    def get(self, request):
        page = int(request.GET.get('page', ''))
        first_article = ((page - 1) * 10) if page > 1 else 0

        lang = translation.get_language()
        translation.activate(lang)
        logging.warn(lang)

        articles_len = Article.objects.count()

        if first_article > articles_len:
            response = render(request, "main/articles/reached_end.html")
            reswap(response, "outerHTML")
            return response

        last_article = (page * 10) if page else 10
        last_article = last_article if last_article <= articles_len else (
            articles_len - 1)

        articles = Article.objects.order_by(
            "-publication_date")[first_article:last_article]

        context = {"articles": articles,
                   "current_page": page, "next_page": (page + 1)}
        return render(request, "main/articles/articles.html", context)
