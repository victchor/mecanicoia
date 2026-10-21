from sentence_transformers import CrossEncoder

modelo_reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", max_length=512)

def reranquear(pergunta, trechos, quantidade=5):
    pares = [(pergunta, t["texto"]) for t in trechos]
    notas = modelo_reranker.predict(pares)

    for trecho, nota in zip(trechos, notas):
        trecho["nota"] = float(nota)

    ordenados = sorted(trechos, key=lambda t: t["nota"], reverse=True)
    return ordenados[:quantidade]