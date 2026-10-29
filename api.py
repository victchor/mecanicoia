from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal

from mecanicoia.montagem import criar_responder_pergunta, criar_consulta_de_precos, criar_assistente

app = FastAPI(title="MecânicoIA")
responder_pergunta = criar_responder_pergunta()
consulta_de_precos = criar_consulta_de_precos()
assistente = criar_assistente()


class AssistenteEntrada(BaseModel):
    pergunta: str
    conversa_id: str | None = None


class AssistenteSaida(BaseModel):
    resposta: str
    conversa_id: str


class PerguntaEntrada(BaseModel):
    pergunta: str


class Fonte(BaseModel):
    arquivo: str
    pagina: int
    nota: float | None


class RespostaSaida(BaseModel):
    resposta: str
    fontes: list[Fonte]


class PrecoSaida(BaseModel):
    marca: str
    modelo: str
    ano_modelo: int
    combustivel: str
    codigo_fipe: str
    valor: Decimal
    mes_referencia: str


@app.get("/precos", response_model=list[PrecoSaida])
def consultar_preco(marca: str, modelo: str, ano: int):
    precos = consulta_de_precos.consultar(marca, modelo, ano)
    return [PrecoSaida(**vars(p)) for p in precos]


@app.post("/perguntas", response_model=RespostaSaida)
def perguntar(entrada: PerguntaEntrada):
    resposta = responder_pergunta.executar(entrada.pergunta)
    fontes = [Fonte(arquivo=t.arquivo, pagina=t.pagina, nota=t.nota) for t in resposta.fontes]
    return RespostaSaida(resposta=resposta.texto, fontes=fontes)


@app.post("/assistente", response_model=AssistenteSaida)
def perguntar_ao_assistente(entrada: AssistenteEntrada):
    conversa_id = entrada.conversa_id or str(uuid4())
    resposta = assistente.responder(entrada.pergunta, conversa_id)
    return AssistenteSaida(resposta=resposta, conversa_id=conversa_id)
