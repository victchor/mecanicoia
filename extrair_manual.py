from pathlib import Path

import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter

PASTA_DADOS = Path("data")

def extrair_paginas(caminho_pdf: Path) -> list[dict]:
    paginas = []
    with pymupdf.open(caminho_pdf) as documento:
        print(f"{caminho_pdf.name} - {documento.page_count} páginas")
        for numero, pagina in enumerate(documento, start=1):
            texto_pagina = pagina.get_text()
            if texto_pagina.strip():
                paginas.append({"arquivo": caminho_pdf.name, "pagina": numero, "texto": texto_pagina})
    return paginas


def dividir_em_chunks(paginas: list[dict]) -> list[dict]:
    divisor = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = []
    for pagina in paginas:
        for indice, pedaco in enumerate(divisor.split_text(pagina["texto"])):
            chunks.append({
                "arquivo": pagina["arquivo"],
                "pagina": pagina["pagina"],
                "indice": indice,
                "texto": pedaco,
            })
    return chunks


if __name__ == "__main__":
    for caminho_pdf in PASTA_DADOS.glob("*.pdf"):
        paginas = extrair_paginas(caminho_pdf)
        chunks = dividir_em_chunks(paginas)
        print(f"Páginas com texto: {len(paginas)} | Chunks: {len(chunks)}")
        print(chunks[20])