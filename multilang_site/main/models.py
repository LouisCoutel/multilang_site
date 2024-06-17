""" Model definitions """

from django.db import models
from django.utils.translation import gettext as _


class Article(models.Model):
    """ Model for a blog article
    Attributes:
        title (str): Article title. Max length: 200 characters.
        content (str): Article main body of text.
        publication_date (Date): Article publication date.

    """

    title = models.CharField(verbose_name=_("title"), max_length=200)
    content = models.TextField(verbose_name=_("content"))
    publication_date = models.DateField(verbose_name=_("publication_date"),
                                        auto_now_add=True)

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
