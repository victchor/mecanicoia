import chromadb

from mecanicoia.dominio.modelos import Chunk
from mecanicoia.dominio.portas import RepositorioVetorial


class RepositorioChroma(RepositorioVetorial):
    def __init__(self, caminho_banco="chroma_db", nome_colecao="manuais"):
        cliente = chromadb.PersistentClient(path=caminho_banco)
        self.colecao = cliente.get_or_create_collection(name=nome_colecao)

    def ids_existentes(self, ids: list[str]) -> set[str]:
        return set(self.colecao.get(ids=ids)["ids"])

    def salvar(self, chunks: list[Chunk], vetores: list[list[float]]) -> None:
        self.colecao.add(
            ids=[c.id for c in chunks],
            documents=[c.texto for c in chunks],
            embeddings=vetores,
            metadatas=[{"arquivo": c.arquivo, "pagina": c.pagina} for c in chunks],
        )