from langchain_text_splitters import RecursiveCharacterTextSplitter

from mecanicoia.dominio.portas import DivisorDeTexto


class DivisorRecursivo(DivisorDeTexto):
    def __init__(self, tamanho=1000, sobreposicao=150):
        self.divisor = RecursiveCharacterTextSplitter(chunk_size=tamanho, chunk_overlap=sobreposicao)

    def dividir(self, texto: str) -> list[str]:
        return self.divisor.split_text(texto)