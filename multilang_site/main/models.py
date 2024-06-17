from django.db import models

from django.utils.translation import gettext as _
# Create your models here.


class Article(models.Model):
    title = models.CharField(verbose_name=_("title"), max_length=200)
    content = models.TextField(verbose_name=_("content"))
    publication_date = models.DateField(verbose_name=_("publication_date"),
                                        auto_now_add=True)

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
