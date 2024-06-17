""" Model translator """

from modeltranslation.translator import translator, TranslationOptions
from main.models import Article


class ArticleTranslationOptions(TranslationOptions):
    """ Translation options for articles """
    
    fields = ('title', 'publication_date', 'content')


translator.register(Article, ArticleTranslationOptions)
