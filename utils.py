#
# File: utils.py
# Author: Daniel Oliveira
#

### Utility functions: semantic intent matching and response generation ###

from __future__ import annotations

import json
import random
import time
from typing import Any

from sentence_transformers import SentenceTransformer
from sentence_transformers import util as st_util
from db import *

# Load the sentence-transformer model once at import time
_model = SentenceTransformer('all-MiniLM-L6-v2')


def load_intents(path: str = 'intents.json') -> dict:
    """Load intents from JSON file."""
    with open(path) as f:
        return json.load(f)


def build_intent_embeddings(intents: dict) -> tuple[list, list]:
    """Pre-compute the mean embedding for each intent's patterns."""
    tags: list[str] = []
    embeddings: list[Any] = []
    for intent in intents['intents']:
        if not intent['patterns']:
            continue
        embs = _model.encode(intent['patterns'], convert_to_tensor=True)
        tags.append(intent['tag'])
        embeddings.append(embs.mean(dim=0))
    return tags, embeddings


def predict_intent(user_input: str, tags: list, embeddings: list, threshold: float = 0.35) -> str | None:
    """Return the intent tag with the highest cosine similarity, or None if below threshold."""
    user_emb = _model.encode(user_input, convert_to_tensor=True)
    scores = [st_util.cos_sim(user_emb.unsqueeze(0), emb.unsqueeze(0)).item() for emb in embeddings]
    best_idx = max(range(len(scores)), key=lambda i: scores[i])
    return tags[best_idx] if scores[best_idx] >= threshold else None


def findanswer(tag: str, intents: dict, inputmsg: str, inputarray: list, id: int, name: str) -> str:
    """Select and personalise a response for the matched intent."""
    intentlist = intents['intents']
    result = ""
    # flag2: True when this is a first-time action request (not a follow-up)
    flag2 = inputarray[-1] not in ("Buy", "Sell", "Password", "Email")

    for i in intentlist:
        if i['tag'] == tag:
            result = random.choice(i['answers'])

            if i['tag'] == "Time" and flag2:
                result = result.replace("%%TIME%%", time.strftime("%c"))

            elif i['tag'] == "Buy" and flag2:
                try:
                    value = int(''.join(filter(str.isdigit, inputmsg)))
                except ValueError:
                    result = "How many BTC do you want to buy?"
                else:
                    updateBalance(id, value, True)
                    result = "Done! Please reload page to see your balance"

            elif i['tag'] == "Sell" and flag2:
                try:
                    value = int(''.join(filter(str.isdigit, inputmsg)))
                except ValueError:
                    result = "How many BTC do you want to sell?"
                else:
                    updateBalance(id, value, False)
                    result = "Done! Please reload page to see your balance"

            elif i['tag'] == "Greeting" and flag2:
                result = result.replace("%%Name%%", name.split()[0])

            elif i['tag'] == "Name" and flag2:
                result = result.replace("%%Name%%", name)

            else:
                if inputarray[-1] == "Buy":
                    try:
                        value = int(''.join(filter(str.isdigit, inputmsg)))
                    except ValueError:
                        result = "Please try again using a correct value"
                    else:
                        updateBalance(id, value, True)
                        result = "Done! Please reload page to see your balance"

                elif inputarray[-1] == "Sell":
                    try:
                        value = int(''.join(filter(str.isdigit, inputmsg)))
                    except ValueError:
                        result = "Please try again using a correct value"
                    else:
                        updateBalance(id, value, False)
                        result = "Done! Please reload page to see your balance"

                elif inputarray[-1] == "Password":
                    updatePassword(id, inputmsg)
                    result = "Done! Your password is updated"

                elif inputarray[-1] == "Email":
                    updateEmail(id, inputmsg)
                    result = "Done! Your email is updated"

    return result
