import json
from pathlib import Path

from responder import responder

S = Path("avaliacao/perguntas.jsonl")
RESULTADOS = Path("avaliacao/resultados.jsonl")

with S.open(encoding="utf-8") as arquivo:
    casos = [json.loads(linha) for linha in arquivo if linha.strip()]

acertos = 0
with RESULTADOS.open("w", encoding="utf-8") as saida:
    for caso in casos:
        resposta, trechos = responder(caso["pergunta"])
        paginas = [t["pagina"] for t in trechos]
        acertou = caso["pagina_esperada"] in paginas
        acertos += acertou

        print(f"{'OK  ' if acertou else 'ERRO'} {caso['pergunta']} -> páginas {paginas}")
        registro = {**caso, "resposta": resposta, "paginas_recuperadas": paginas, "acertou_pagina": acertou}
        saida.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"\nPágina certa entre os 5 trechos: {acertos}/{len(casos)}")
