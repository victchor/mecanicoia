from sentence_transformers import CrossEncoder

from mecanicoia.dominio.modelos import Trecho
from mecanicoia.dominio.portas import Reranqueador


class ReranqueadorCrossEncoder(Reranqueador):
    def __init__(self, nome_modelo="BAAI/bge-reranker-v2-m3"):
        self.modelo = CrossEncoder(nome_modelo, max_length=512)

    def reranquear(self, pergunta: str, trechos: list[Trecho], quantidade: int ) -> list[Trecho]:
        notas = self.modelo.predict([(pergunta, t.texto) for t in trechos])
        for trecho, nota in zip(trechos, notas):
            trecho.nota = float(nota)
        return sorted(trechos, key=lambda t: t.texto, reverse=True)[:quantidade]
