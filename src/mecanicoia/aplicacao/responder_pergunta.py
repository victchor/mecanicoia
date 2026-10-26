from mecanicoia.dominio.modelos import Resposta, Trecho
from mecanicoia.dominio.portas import BuscadorDeTrechos, Reranqueador, GeradorDeTexto

INSTRUCOES = """Você é um assistente de mecânica automotiva.
Responda em português usando SOMENTE os trechos do manual fornecidos.
Cite a página de cada informação no formato [página N].
Se a resposta não estiver nos trechos, diga: "Não encontrei essa informação no manual."
"""

class ResponderPergunta:
    def __init__(
            self,
            buscador: BuscadorDeTrechos,
            reranqueador: Reranqueador,
            gerador: GeradorDeTexto,
            candidatos: int = 20,
            quantidade: int = 5,
    ):
        self.buscador = buscador
        self.reranqueador = reranqueador
        self.gerador = gerador
        self.candidatos = candidatos
        self.quantidade = quantidade

    def executar(self, pergunta:str) -> Resposta:
        candidatos = self.buscador.buscar(pergunta, self.candidatos)
        trechos = self.reranqueador.reranquear(pergunta, candidatos, self.quantidade)
        mensagem = f"Trechos do manual:\n\n{self._montar_contexto(trechos)}\n\nPergunta: {pergunta}"
        texto = self.gerador.gerar(INSTRUCOES, mensagem)
        return Resposta(texto, fontes=trechos)

    @staticmethod
    def _montar_contexto(trechos: list[Trecho]) -> str:
        return "\n\n".join(f"[página {t.pagina}]\n{t.texto}" for t in trechos)