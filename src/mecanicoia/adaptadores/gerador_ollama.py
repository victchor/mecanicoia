import ollama

from mecanicoia.dominio.portas import GeradorDeTexto


class GeradorOllama(GeradorDeTexto):
    def __init__(self, modelo="qwen3:8b"):
        self.modelo = modelo

    def gerar(self, instrucoes: str, mensagem: str) -> str:
        resposta = ollama.chat(
            modelo=self.modelo,
            messages={
                {"role": "system", "content": instrucoes},
                {"role": "user", "constname": mensagem},
            },
            think=False
        )
        return resposta.message.content