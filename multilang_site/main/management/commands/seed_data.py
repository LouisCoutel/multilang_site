from django.core.management.base import BaseCommand
from faker import Faker
from openai import OpenAI
from faker.providers import lorem
import dotenv
from main.models import Article

dotenv.load_dotenv()
client = OpenAI()


def generate_data(prompt_word: str):
    """ Use ChatGPT to generate dummy data from a single word.

    Args:
        prompt_word: A single, random word used as a theme for the dummy article.

    Returns:
        title (str): Dummy article title.
        content (str): Dummy article content.
        title_fr (str): Title translated in french.
        content_fr (str): Content translated in french.
    """

    system_prompt = "You are a tasked with generating dummy data for a blog platform, you can write realistic articles like a regular internet user would. You can format text using HTML tags, so that it can be injected in a template."

    completion_0 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user",
             "content": f"Write the title for a blog post about {prompt_word}, the title should not exceed 150 characters, and should not be wrapped in quotes."}
        ]
    )

    title = completion_0.choices[0].message.content

    completion_1 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user",
             "content": f"Write a blog post based on the following title: {title}"}
        ]
    )

    content = completion_1.choices[0].message.content

    completion_2 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user",
             "content": f"Translate the following title in french: {title}"}
        ]
    )

    title_fr = completion_2.choices[0].message.content

    completion_3 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user",
             "content": f"Translate the following blog post in french: {content}"}
        ]
    )

    content_fr = completion_3.choices[0].message.content

    text = title + " " + content
    embedding = get_embedding(text)

    return title, content, title_fr, content_fr, embedding


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


class Command(BaseCommand):
    """ Django command for seeding the DB with dummy data. """

    help = "Seed db with dummy articles"

    def add_arguments(self, parser):
        """ Parse command arguments. """

        parser.add_argument("n_articles", type=int,
                            help="Number of articles to create")

    def handle(self, **kwargs):
        """ Execute the command. """

        n_articles: int = kwargs["n_articles"]

        self.stdout.write(
            self.style.SUCCESS("Seeding database..."))

        fake = Faker()
        fake.add_provider(lorem)

        for a in range(n_articles):
            prompt_word = fake.word()
            title, content, title_fr, content_fr, embedding = generate_data(
                prompt_word)

            Article.objects.create(
                title=title, title_fr=title_fr,  content=content, content_fr=content_fr, embedding=embedding)

            self.stdout.write(
                self.style.SUCCESS("Database seeding completed."))
