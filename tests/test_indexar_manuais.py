from pathlib import Path

from mecanicoia.aplicacao.indexar_manuais import IndexarManuais
from mecanicoia.dominio.modelos import Pagina

PDF = Path("manual.pdf")


class LeitorFalso:
    def ler(self, caminho):
        return [
            Pagina(arquivo="manual.pdf", numero=1, texto="a b c"),
            Pagina(arquivo="manual.pdf", numero=2, texto="d e"),
        ]


class DivisorFalso:
    def dividir(self, texto):
        return texto.split()


class EmbeddingsFalso:
    def __init__(self):
        self.chamadas = 0

    def gerar(self, textos):
        self.chamadas += 1
        return [[0.0] for _ in textos]


class RepositorioEmMemoria:
    def __init__(self):
        self.dados = {}

    def ids_existentes(self, ids):
        return {id_ for id_ in ids if id_ in self.dados}

    def salvar(self, chunks, vetores):
        for chunk, vetor in zip(chunks, vetores):
            self.dados[chunk.id] = (chunk, vetor)


def test_indexa_todos_os_chunks_na_primeira_vez():
    repositorio = RepositorioEmMemoria()
    caso_de_uso = IndexarManuais(LeitorFalso(), DivisorFalso(), EmbeddingsFalso(), repositorio)

    assert caso_de_uso.executar(PDF) == 5
    assert "manual.pdf:p2:c1" in repositorio.dados


def test_reindexar_nao_duplica_nem_gera_embeddings_de_novo():
    repositorio = RepositorioEmMemoria()
    embeddings = EmbeddingsFalso()
    caso_de_uso = IndexarManuais(LeitorFalso(), DivisorFalso(), embeddings, repositorio)

    caso_de_uso.executar(PDF)
    assert caso_de_uso.executar(PDF) == 0
    assert len(repositorio.dados) == 5
    assert embeddings.chamadas == 1


def test_processa_em_lotes():
    embeddings = EmbeddingsFalso()
    caso_de_uso = IndexarManuais(LeitorFalso(), DivisorFalso(), embeddings, RepositorioEmMemoria(), tamanho_lote=2)

    caso_de_uso.executar(PDF)
    assert embeddings.chamadas == 3