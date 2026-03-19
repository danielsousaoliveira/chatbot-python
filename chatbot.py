#
# File: chatbot.py
# Author: Daniel Oliveira
#

### Conversation Agent Backend Functions ###

from __future__ import annotations

import pickle
from pathlib import Path
from utils import load_intents, build_intent_embeddings, predict_intent, findanswer

EMBEDDINGS_CACHE = 'intent_embeddings.pkl'

# Track the last intent tag for multi-turn conversation handling
inputarray: list[str] = ["first"]

# Load intents and embeddings once at startup
intents = load_intents()
if Path(EMBEDDINGS_CACHE).exists():
    with open(EMBEDDINGS_CACHE, 'rb') as f:
        tags, embeddings = pickle.load(f)
else:
    tags, embeddings = build_intent_embeddings(intents)


def communicate(inputmsg: str, id: int, name: str) -> str:
    """Return the chatbot's response to a user message."""
    tag = predict_intent(inputmsg, tags, embeddings)
    if tag is None:
        return "Not sure I understood that, can you put it another way?"
    result = findanswer(tag, intents, inputmsg, inputarray, id, name)
    inputarray.append(tag)
    return result
