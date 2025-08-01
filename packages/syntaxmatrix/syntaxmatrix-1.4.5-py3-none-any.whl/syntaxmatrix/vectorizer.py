import os
import openai
from openai import OpenAI
from . import llm_store as _llms
from . import profiles as prof
from typing import List
import itertools
from syntaxmatrix import llm_store as _llms
from dotenv import load_dotenv


def embed_text(text: str):

    settings = _llms.load_embed_model()
    model = settings["model"]
    api_key = settings["api_key"]
    embed_client = OpenAI(api_key=api_key)

    try:
        resp = embed_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return resp.data[0].embedding
    except Exception as e:
        # log to console for debugging
        print(f"[vectorizer] embed_text failed: {e}")
        # return None so callers can check and bail out
        return None
    
    
def get_embeddings_in_batches(texts:List[str], batch_size=100) -> List[List[float]]: 

    settings = _llms.load_embed_model()
    model = settings["model"]
    api_key = settings["api_key"]
    embed_client = OpenAI(api_key=api_key)
    results = []
    for batch in itertools.zip_longest(*(iter(texts),) * batch_size):
        batch = [t for t in batch if t is not None]
        res = embed_client.embeddings.create(model=model, input=batch)
        results.extend([r.embedding for r in res.data])
    return results