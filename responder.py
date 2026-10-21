import ollama
from reranker import reranquear

from indexar import colecao

PROMPT_SISTEMA = """Você é um assistente de mecânica automotiva.
Responda em português usando SOMENTE os trechos do manual fornecidos.
Cite a página de cada informação no formato [página N].
Se a resposta não estiver nos trechos, diga: "Não encontrei essa informação no manual."
"""

def recuperar(query, topk=5):
    vetor = ollama.embed(model="bge-m3", input=query).embeddings
    resultado = colecao.query(query_embeddings=vetor, n_results=topk)

    return [
        {"texto": texto, **meta}
        for texto, meta, in zip(resultado["documents"][0], resultado["metadatas"][0])
    ]

def montar_contexto(trechos):
    return "\n\n".join(f"[página {t['pagina']}]\n{t['texto']}" for t in trechos)

def responder(query):
    candidatos = recuperar(query, topk=20)
    trechos = reranquear(query, candidatos, quantidade=5)
    contexto = montar_contexto(trechos)
    resposta = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": f"Trechos do manual: \n\n{contexto}\n\nPergunta: {query}"}
        ],
        think=False,
    )
    return resposta.message.content, trechos

if __name__ == "__main__":
    pergunta = "Qual a pressão dos pneus?"
    texto_resposta, trechos = responder(pergunta)
    print(texto_resposta)
    print("\nPáginas consultadas:", [(t["pagina"], round(t["nota"], 2)) for t in trechos])
