from pathlib import Path

from mecanicoia.dominio.modelos import Chunk
from mecanicoia.dominio.portas import (
    DivisorDeTexto,
    GeradorDeEmbeddings,
    LeitorDeDocumentos,
    RepositorioVetorial,
)


class IndexarManuais:
    def __init__(
        self,
        leitor: LeitorDeDocumentos,
        divisor: DivisorDeTexto,
        embeddings: GeradorDeEmbeddings,
        repositorio: RepositorioVetorial,
        tamanho_lote: int = 32,
    ):
        self.leitor = leitor
        self.divisor = divisor
        self.embeddings = embeddings
        self.repositorio = repositorio
        self.tamanho_lote = tamanho_lote

    def executar(self, caminho: Path) -> int:
        chunks = self._gerar_chunks(caminho)
        existentes = self.repositorio.ids_existentes([c.id for c in chunks])
        novos = [c for c in chunks if c.id not in existentes]

        for inicio in range(0, len(novos), self.tamanho_lote):
            lote = novos[inicio:inicio + self.tamanho_lote]
            vetores = self.embeddings.gerar([c.texto for c in lote])
            self.repositorio.salvar(lote, vetores)

        return len(novos)

    def _gerar_chunks(self, caminho: Path) -> list[Chunk]:
        chunks = []
        for pagina in self.leitor.ler(caminho):
            for indice, pedaco in enumerate(self.divisor.dividir(pagina.texto)):
                chunks.append(Chunk(arquivo=pagina.arquivo, pagina=pagina.numero, indice=indice, texto=pedaco))
        return chunks
