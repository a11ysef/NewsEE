"""Demonstration selection: TF-IDF similarity retrieval (or random, as a control).

Pure Python, no extra dependencies. The pool is the MAVEN-Arg training subset
(data/pool.jsonl), so demonstrations never come from the evaluation documents.
"""
import math
import random
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set("""a an the of in on at to for from by with and or but as is was were be been are it its
this that these those he she they his her their them which who whom whose what when where
while after before during into over under than then also not no s""".split())


def _tokens(text):
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 1]


class Retriever:
    def __init__(self, pool, seed=42):
        self.pool = pool
        self.rng_seed = seed
        df = Counter()
        tfs = []
        for d in pool:
            tf = Counter(_tokens(d["text"]))
            tfs.append(tf)
            df.update(tf.keys())
        n = len(pool)
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}
        self.vecs = [self._vec(tf) for tf in tfs]
        self.types = [{e["type"] for e in d["events"]} for d in pool]

    def _vec(self, tf):
        v = {t: (1 + math.log(c)) * self.idf.get(t, 0.0) for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def _candidates(self, require_type):
        return [i for i in range(len(self.pool)) if require_type is None or require_type in self.types[i]]

    def similar(self, text, k, require_type=None):
        """Top-k most similar pool documents (optionally containing an event type)."""
        q = self._vec(Counter(_tokens(text)))
        scored = []
        for i in self._candidates(require_type):
            v = self.vecs[i]
            s = sum(w * v.get(t, 0.0) for t, w in q.items())
            scored.append((s, i))
        scored.sort(reverse=True)
        return [self.pool[i] for _, i in scored[:k]]

    def random(self, text, k, require_type=None):
        """k random pool documents; deterministic per query text (reproducible)."""
        rng = random.Random(f"{self.rng_seed}|{require_type}|{text[:200]}")
        cands = self._candidates(require_type)
        return [self.pool[i] for i in rng.sample(cands, min(k, len(cands)))]
