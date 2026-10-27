import json
from pathlib import Path

from mecanicoia.montagem import criar_responder_pergunta

PERGUNTAS = Path("avaliacao/perguntas.jsonl")
RESULTADOS = Path("avaliacao/resultados.jsonl")


def main() -> None:
    responder_pergunta = criar_responder_pergunta()

    with PERGUNTAS.open(encoding="utf-8") as arquivo:
        casos = [json.loads(linha) for linha in arquivo if linha.strip()]

    acertos = 0
    with RESULTADOS.open("w", encoding="utf-8") as saida:
        for caso in casos:
            resposta = responder_pergunta.executar(caso["pergunta"])
            paginas = [t.pagina for t in resposta.fontes]

            if caso["pagina_esperada"] is None:
                acertou = "Não encontrei" in resposta.texto
            else:
                acertou = caso["pagina_esperada"] in paginas
            acertos += acertou

            print(f"{'OK  ' if acertou else 'ERRO'} {caso['pergunta']} -> páginas {paginas}")
            registro = {**caso, "resposta": resposta.texto, "paginas_recuperadas": paginas, "acertou": acertou}
            saida.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"\nAcertos: {acertos}/{len(casos)}")


if __name__ == "__main__":
    main()
