import numpy as np

def normalize_embeddings(raw_chunk_embeddings):
    corpus_center = np.mean(raw_chunk_embeddings, axis=0)
    centered_embs = raw_chunk_embeddings - corpus_center
    norms = np.linalg.norm(centered_embs, axis=1, keepdims=True)
    norms[norms == 0] = 1e-6
    final_chunk_embeddings = centered_embs / norms
    return corpus_center, final_chunk_embeddings