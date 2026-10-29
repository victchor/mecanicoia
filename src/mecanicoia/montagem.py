from functools import cache

from mecanicoia.adaptadores.agente_langgraph import AgenteLangGraph
from mecanicoia.adaptadores.buscador_chroma             import BuscadorChroma
from mecanicoia.adaptadores.consulta_fipe_parallelum    import ConsultaFipeParallelum
from mecanicoia.adaptadores.divisor_recursivo           import DivisorRecursivo
from mecanicoia.adaptadores.embeddings_ollama           import EmbeddingsOllama
from mecanicoia.adaptadores.gerador_ollama              import GeradorOllama
from mecanicoia.adaptadores.repositorio_chroma          import RepositorioChroma
from mecanicoia.adaptadores.reranqueador_cross_encoder  import ReranqueadorCrossEncoder
from mecanicoia.aplicacao.responder_pergunta            import ResponderPergunta
from mecanicoia.aplicacao.indexar_manuais               import IndexarManuais
from mecanicoia.adaptadores.leitor_pymupdf              import LeitorPyMuPDF

@cache
def _reranqueador() -> ReranqueadorCrossEncoder:
    return ReranqueadorCrossEncoder()

def criar_responder_pergunta(modelo_llm="qwen3:8b", candidatos=20, quantidade=5) -> ResponderPergunta:
    return ResponderPergunta(
        buscador=BuscadorChroma(),
        reranqueador=_reranqueador(),
        gerador=GeradorOllama(modelo=modelo_llm),
        candidatos=candidatos,
        quantidade=quantidade,
    )

def criar_indexar_manuais(tamanho_lote: int = 32) -> IndexarManuais:
    return IndexarManuais(
        leitor=LeitorPyMuPDF(),
        divisor=DivisorRecursivo(),
        embeddings=EmbeddingsOllama(),
        repositorio=RepositorioChroma(),
        tamanho_lote=tamanho_lote,
    )

def criar_consulta_de_precos() -> ConsultaFipeParallelum:
    return ConsultaFipeParallelum()

def criar_assistente() -> AgenteLangGraph:
    return AgenteLangGraph(
        consulta_de_precos=ConsultaFipeParallelum(),
        buscador=BuscadorChroma(),
        reranqueador=_reranqueador(),
    )