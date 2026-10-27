from pathlib import Path

from mecanicoia.montagem import criar_indexar_manuais

PASTA_DADOS = Path("data")


def main() -> None:
    caso_de_uso = criar_indexar_manuais()
    for pdf in sorted(PASTA_DADOS.glob("*.pdf")):
        novos = caso_de_uso.executar(pdf)
        print(f"{pdf.name}: {novos} chunks novos")


if __name__ == "__main__":
    main()