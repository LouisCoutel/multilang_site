from django.core.management.base import BaseCommand
from faker import Faker
from main.models import Article
from faker.providers import lorem


class Command(BaseCommand):
    help = "Seed db with dummy articles"

    def add_arguments(self, parser):
        parser.add_argument("n_articles", type=int,
                            help="Number of articles to create")

    def handle(self, **kwargs):
        n_articles = kwargs["n_articles"]

        self.stdout.write(self.style.SUCCESS("Seeding database..."))

        fake = Faker()
        fake.add_provider(lorem)

        article_titles = set(
            Article.objects.values_list("title", flat=True))
        for _ in range(n_articles):
            title = fake.sentence()

            while title in article_titles:
                title = fake.sentence()

            content = fake.text(max_nb_chars=750)

            Article.objects.create(title=title, content=content)
            self.stdout.write(self.style.SUCCESS(
                "Database seeding completed."))
