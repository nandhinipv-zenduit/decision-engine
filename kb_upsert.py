import os
import requests
from pinecone import Pinecone
from openai import OpenAI

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

ZOHO_KB_API = "YOUR_ZOHO_DESK_KB_API"

def get_kb_articles():

    headers = {
        "Authorization": "Zoho-oauthtoken YOUR_TOKEN"
    }

    response = requests.get(ZOHO_KB_API, headers=headers)

    return response.json()["data"]


def embed_text(text):

    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def upsert_kb():

    articles = get_kb_articles()

    vectors = []

    for article in articles:

        text = article["title"] + " " + article["content"]

        embedding = embed_text(text)

        vectors.append({
            "id": article["id"],
            "values": embedding,
            "metadata": {
                "title": article["title"],
                "url": article["permalink"]
            }
        })

    index.upsert(vectors=vectors)

    print("KB uploaded")


if __name__ == "__main__":
    upsert_kb()
