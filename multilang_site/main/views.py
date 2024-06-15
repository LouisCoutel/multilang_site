from django.shortcuts import render
from main.models import Article


def base(request):
    return render(request, "main/base_layout.html")


def articles(request):
    articles = Article.objects.order_by("-publication_date")[:15]
    context = {"articles": articles}
    return render(request, "main/articles/articles.html", context)
# Create your views here.
