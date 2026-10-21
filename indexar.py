import chromadb
import ollama

from extrair_manual import PASTA_DADOS, dividir_em_chunks, extrair_paginas

cliente = chromadb.PersistentClient(path="chroma_db")
colecao = cliente.get_or_create_collection(name="manuais")

TAMANHO_LOTE = 32

def indexar_pdf(caminho_pdf):
    chunks = dividir_em_chunks( extrair_paginas((caminho_pdf)) )
    ids = [f"{c['arquivo']}:p{c['pagina']}:c{c['indice']}" for c in chunks]

    indexados = set(colecao.get(ids=ids)["ids"])
    novos = [(id_,c) for id_, c in zip(ids, chunks) if id_ not in indexados]

    if not novos:
        print(f"{caminho_pdf} ja indexado, nada a fazer")
        return

    for inicio in range(0, len(novos), TAMANHO_LOTE):
        lote = novos[inicio:inicio + TAMANHO_LOTE]
        textos = [c["texto"] for _, c in lote]
        vetores = ollama.embed(model="bge-m3", input=textos).embeddings
        colecao.add(
            ids = [id_ for id_, _ in lote],
            documents=textos,
            embeddings = vetores,
            metadatas=[{"arquivo": c["arquivo"], "pagina": c["pagina"]} for _, c in lote],
        )
        print(f"{inicio + len(lote)}/{len(novos)} chunks indexados")


if __name__ == "__main__":
    for caminho_pdf in PASTA_DADOS.glob("*.pdf"):
        indexar_pdf(caminho_pdf)
