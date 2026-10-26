from typing import Protocol

from mecanicoia.dominio.modelos import Trecho


class BuscadorDeTrechos(Protocol):
    def buscar(self, pergunta: str, candidatos: int) -> list[Trecho]: ...


class Reranqueador(Protocol):
    def reranquear(self, pergunta: str, trechos: list[Trecho], quantidade: int) -> list[Trecho]: ...


class GeradorDeTexto(Protocol):
    def gerar(self, instrucoes: str, mensagem: str) -> str: ...