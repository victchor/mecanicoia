from fastapi import FastAPI
from pydantic import BaseModel

from responder import responder

app = FastAPI(title="MecânicoIA")

class PerguntaEntrada(BaseModel):
    pergunta: str

class Fonte(BaseModel):
    arquivo: str
    pagina: int
    nota: float

class RespostaSaida(BaseModel):
    resposta: str
    fontes: list[Fonte]

@app.post("/perguntas", response_model=RespostaSaida)
def perguntar(entrada: PerguntaEntrada):
    texto, trechos = responder(entrada.pergunta)
    fontes = [Fonte(arquivo=t["arquivo"], pagina=t["pagina"], nota=t["nota"]) for t in trechos]
    return RespostaSaida(resposta=texto, fontes=fontes)