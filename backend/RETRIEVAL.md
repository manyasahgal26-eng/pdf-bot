# Retrieval Modes

The backend supports two retrieval modes.

## TF-IDF mode

Default mode. This is used on Render free tier because it is lightweight.

```bash
RETRIEVAL_MODE=tfidf
```

Install:

```bash
pip install -r requirements.txt
```

## Chroma mode

Higher-quality local mode using ChromaDB and SentenceTransformers.

```bash
RETRIEVAL_MODE=chroma
```

Install:

```bash
pip install -r requirements-chroma.txt
```

Render free usually does not have enough memory for Chroma mode.
