import chromadb
import ollama

from mecanicoia.dominio.modelos import Trecho
from mecanicoia.dominio.portas import BuscadorDeTrechos

class BuscadorChroma(BuscadorDeTrechos):
    def __init__(self, caminho_banco="chroma_db", nome_colecao="manuais", modelo_embedding="bge-m3"):
        cliente = chromadb.PersistentClient(path=caminho_banco)
        self.colecao = cliente.get_or_create_collection(name=nome_colecao)
        self.modelo_embedding = modelo_embedding

    def buscar(self, pergunta: str, candidatos: int) -> list[Trecho]:
        vetor = ollama.embed(model=self.modelo_embedding, input=pergunta).embeddings
        resultado = self.colecao.query(query_embeddings=vetor, n_results=candidatos)
        return [
            Trecho(arquivo=meta["arquivo"], pagina=meta["pagina"], texto=texto)
            for texto, meta in zip(resultado["documents"][0], resultado["metadatas"][0])
        ]