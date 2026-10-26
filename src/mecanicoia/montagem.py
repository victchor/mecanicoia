from mecanicoia.adaptadores.buscador_chroma import BuscadorChroma
from mecanicoia.adaptadores.gerador_ollama import GeradorOllama
from mecanicoia.adaptadores.reranqueador_cross_encoder import ReranqueadorCrossEncoder
from mecanicoia.aplicacao.responder_pergunta import ResponderPergunta


def criar_responder_pergunta(modelo_llm="qwen3:8b", candidatos=20, quantidade=5) -> ResponderPergunta:
    return ResponderPergunta(
        buscador=BuscadorChroma(),
        reranqueador=ReranqueadorCrossEncoder(),
        gerador=GeradorOllama(modelo=modelo_llm),
        candidatos=candidatos,
        quantidade=quantidade,
    )