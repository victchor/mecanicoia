import ollama

from mecanicoia.dominio.portas import GeradorDeEmbeddings


class EmbeddingsOllama(GeradorDeEmbeddings):
    def __init__(self, modelo="bge-m3"):
        self.modelo = modelo

    def gerar(self, textos: list[str]) -> list[list[float]]:
        return ollama.embed(model=self.modelo, input=textos).embeddings