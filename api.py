from fastapi import FastAPI
from pydantic import BaseModel

from mecanicoia.montagem import criar_responder_pergunta

app = FastAPI(title="MecânicoIA")
responder_pergunta = criar_responder_pergunta()


class PerguntaEntrada(BaseModel):
    pergunta: str


class Fonte(BaseModel):
    arquivo: str
    pagina: int
    nota: float | None


class RespostaSaida(BaseModel):
    resposta: str
    fontes: list[Fonte]


@app.post("/perguntas", response_model=RespostaSaida)
def perguntar(entrada: PerguntaEntrada):
    resposta = responder_pergunta.executar(entrada.pergunta)
    fontes = [Fonte(arquivo=t.arquivo, pagina=t.pagina, nota=t.nota) for t in resposta.fontes]
    return RespostaSaida(resposta=resposta.texto, fontes=fontes)