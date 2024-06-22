from openai import OpenAI, AssistantEventHandler
from pgvector.django import CosineDistance
from main.models import Article
client = OpenAI()

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding
def distance_search(article_desc: str):
    embedding = get_embedding(article_desc, model='text-embedding-3-small')
    matching_articles = Article.objects.annotate(
        distance=CosineDistance("embedding", embedding)
    ).order_by("distance")

    return matching_articles
