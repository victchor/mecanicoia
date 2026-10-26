from mecanicoia.aplicacao.responder_pergunta import ResponderPergunta
from mecanicoia.dominio.modelos import Trecho


class BuscadorFalso:
    def buscar(self, pergunta, candidatos):
        return [
            Trecho(arquivo="manual.pdf", pagina=10, texto="Texto irrelevante"),
            Trecho(arquivo="manual.pdf", pagina=158, texto="Capacidade: cerca de 55 litros"),
        ]


class ReranqueadorFalso:
    def reranquear(self, pergunta, trechos, quantidade):
        return list(reversed(trechos))[:quantidade]


class GeradorFalso:
    def __init__(self):
        self.recebido = None

    def gerar(self, instrucoes, mensagem):
        self.recebido = (instrucoes, mensagem)
        return "São cerca de 55 litros [página 158]."


def test_responde_usando_os_trechos_reranqueados():
    gerador = GeradorFalso()
    caso_de_uso = ResponderPergunta(BuscadorFalso(), ReranqueadorFalso(), gerador, quantidade=1)

    resposta = caso_de_uso.executar("Qual a capacidade do tanque?")

    assert resposta.texto == "São cerca de 55 litros [página 158]."
    assert [t.pagina for t in resposta.fontes] == [158]

    instrucoes, mensagem = gerador.recebido
    assert "SOMENTE" in instrucoes
    assert "[página 158]" in mensagem
    assert "Qual a capacidade do tanque?" in mensagem