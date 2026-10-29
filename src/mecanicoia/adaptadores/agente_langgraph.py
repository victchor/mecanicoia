from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool, tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from mecanicoia.dominio.portas import Assistente, BuscadorDeTrechos, ConsultaDePrecos, Reranqueador

INSTRUCOES = """Você é o MecânicoIA, assistente de mecânica automotiva. Responda em português.
Use as ferramentas para obter informações; não responda de memória.
Toda informação tirada do manual deve terminar com a página no formato [página N].
Se a consulta de preços trouxer mais de uma versão, mostre todas."""


class AgenteLangGraph(Assistente):
    def __init__(
            self,
            consulta_de_precos: ConsultaDePrecos,
            buscador: BuscadorDeTrechos,
            reranqueador: Reranqueador,
            modelo: str = "qwen3:8b",
            max_passos: int = 10,
            checkpointer: BaseCheckpointSaver | None = None,
    ):
        ferramentas = self._criar_ferramentas(consulta_de_precos, buscador, reranqueador)
        self.llm = ChatOllama(model=modelo, reasoning=False).bind_tools(ferramentas)
        self.max_passos = max_passos
        self.grafo = self._montar_grafo(ferramentas, checkpointer or InMemorySaver())

    def responder(self, pergunta: str, conversa_id: str) -> str:
        configuracao = {"configurable": {"thread_id": conversa_id}, "recursion_limit": self.max_passos}
        resultado = self.grafo.invoke({"messages": [HumanMessage(pergunta)]}, configuracao)
        return resultado["messages"][-1].content

    def _agente(self, estado: MessagesState) -> dict:
        resposta = self.llm.invoke([SystemMessage(INSTRUCOES)] + estado["messages"])
        return {"messages": [resposta]}

    def _montar_grafo(self, ferramentas: list[BaseTool], checkpointer: BaseCheckpointSaver):
        grafo = StateGraph(MessagesState)
        grafo.add_node("agente", self._agente)
        grafo.add_node("tools", ToolNode(ferramentas))
        grafo.add_edge(START, "agente")
        grafo.add_conditional_edges("agente", tools_condition)
        grafo.add_edge("tools", "agente")
        return grafo.compile(checkpointer=checkpointer)

    @staticmethod
    def _criar_ferramentas(
            consulta_de_precos: ConsultaDePrecos,
            buscador: BuscadorDeTrechos,
            reranqueador: Reranqueador,
    ) -> list[BaseTool]:
        @tool(parse_docstring=True)
        def consultar_preco_fipe(marca: str, modelo: str, ano: int) -> str:
            """Consulta o preço de referência de um carro na tabela FIPE.

            Args:
                marca: marca do carro, ex.: Peugeot
                modelo: modelo e versão, ex.: 208 Allure
                ano: ano do modelo, ex.: 2018
            """
            precos = consulta_de_precos.consultar(marca, modelo, int(ano))
            if not precos:
                return "Nenhum veículo encontrado na FIPE."
            return "\n".join(f"{p.modelo} {p.ano_modelo} {p.combustivel}: R$ {p.valor} ({p.mes_referencia})" for p in precos)

        @tool(parse_docstring=True)
        def buscar_no_manual(pergunta: str) -> str:
            """Busca trechos no manual do proprietário do Peugeot 208 (2017/2018): manutenção,
            pneus, fluidos, painel, fusíveis, bateria e especificações técnicas.

            Args:
                pergunta: o que procurar no manual, ex.: pressão dos pneus
            """
            candidatos = buscador.buscar(pergunta, 20)
            trechos = reranqueador.reranquear(pergunta, candidatos, 5)
            return "\n\n".join(f"[página {t.pagina}]\n{t.texto}" for t in trechos)

        return [consultar_preco_fipe, buscar_no_manual]