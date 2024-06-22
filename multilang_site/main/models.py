""" Model definitions """
from pgvector.django import VectorField
from django.db import models
from django.utils.translation import gettext as _
from pgvector.django import HnswIndex


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
    embedding = VectorField(
        dimensions=1536
    )

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        indexes = [
            HnswIndex(
                name="gpt_vectors_index",
                fields=["embedding"],
                m=10,
                ef_construction=24,
                opclasses=["vector_cosine_ops"],
            )
        ]
