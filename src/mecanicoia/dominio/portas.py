from pathlib import Path
from typing import Protocol

from mecanicoia.dominio.modelos import Trecho, Chunk, PrecoFipe, Pagina


class BuscadorDeTrechos(Protocol):
    def buscar(self, pergunta: str, candidatos: int) -> list[Trecho]: ...


class Reranqueador(Protocol):
    def reranquear(self, pergunta: str, trechos: list[Trecho], quantidade: int) -> list[Trecho]: ...


class GeradorDeTexto(Protocol):
    def gerar(self, instrucoes: str, mensagem: str) -> str: ...


class LeitorDeDocumentos(Protocol):
    def ler(self, caminho: Path) -> list[Pagina]: ...


class DivisorDeTexto(Protocol):
    def dividir(self, texto: str) -> list[str]: ...


class GeradorDeEmbeddings(Protocol):
    def gerar(self, texto: list[str]) -> list[list[float]]: ...


class RepositorioVetorial(Protocol):
    def ids_existentes(self, ids: list[str]) -> set[str]: ...
    def salvar(self, chunks: list[Chunk], vetores: list[list[float]]) -> None: ...


class ConsultaDePrecos(Protocol):
    def consultar(self, marca: str, modelo: str, ano: int) -> list[PrecoFipe]: ...

class Assistente(Protocol):
    def responder(self, pergunta: str) -> str: ...