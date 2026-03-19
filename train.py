#
# File: train.py
# Author: Daniel Oliveira
#

"""Pre-compute sentence-transformer embeddings for all intent patterns."""

from __future__ import annotations

import pickle
from utils import load_intents, build_intent_embeddings

EMBEDDINGS_CACHE = 'intent_embeddings.pkl'

if __name__ == '__main__':
    print("Loading intents...")
    intents = load_intents()
    print(f"Computing embeddings for {len(intents['intents'])} intents...")
    tags, embeddings = build_intent_embeddings(intents)
    with open(EMBEDDINGS_CACHE, 'wb') as f:
        pickle.dump((tags, embeddings), f)
    print(f"Saved {len(tags)} intent embeddings to {EMBEDDINGS_CACHE}")
