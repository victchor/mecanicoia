# MecânicoIA: por onde começar

Ideia central: **montar primeiro um "fio" de ponta a ponta bem fino** (pergunta → busca nos manuais → resposta do qwen3 com citação) e só depois engrossar com tools, agente, avaliação e observabilidade. Assim você tem algo funcionando cedo e cada etapa seguinte é mensurável.

---

## Etapa 0: ambiente (meio dia)

Primeiro passo concreto, antes de qualquer código:

```bash
# Ollama
ollama pull qwen3:8b
ollama pull bge-m3
# (reranker: bge-reranker-v2-m3 via sentence-transformers / FlagEmbedding, roda em Python)

# teste rápido
ollama run qwen3:8b "Explique o que é uma junta de cabeçote em 2 frases."
```

- Python 3.12 + `uv` (ou poetry) para dependências.
- `docker compose` com **PostgreSQL** (e, depois, Phoenix). ChromaDB pode rodar embutido (persistente em disco) no começo.
- Separe 2 ou 3 manuais em PDF (de preferência de carros diferentes, um em português) em `data/manuais/`. Comece pequeno.

Critério de pronto: qwen3:8b responde e `bge-m3` gera um embedding via API do Ollama.

---

## Etapa 1: esqueleto hexagonal (1 dia)

Estrutura sugerida:

```
mecanicoia/
├── src/mecanicoia/
│   ├── domain/            # entidades e regras puras (sem LangChain, sem FastAPI)
│   │   ├── models.py      # Veiculo, TrechoManual, Recall, Resposta, Citacao
│   │   └── services.py    # casos de uso: responder_pergunta, consultar_veiculo
│   ├── ports/             # interfaces (Protocol/ABC)
│   │   ├── llm.py         # LLMPort
│   │   ├── embeddings.py  # EmbeddingPort
│   │   ├── retriever.py   # RetrieverPort (busca + rerank)
│   │   ├── vehicle_data.py# VehicleDataPort (vPIC, recalls, FIPE)
│   │   ├── geo.py         # GeoPort (ViaCEP, Nominatim, Overpass)
│   │   └── repository.py  # ConversaRepository (Postgres)
│   ├── adapters/
│   │   ├── ollama/        # implementa LLMPort e EmbeddingPort
│   │   ├── chroma/        # implementa RetrieverPort
│   │   ├── http/          # clientes das APIs públicas
│   │   ├── postgres/      # SQLAlchemy/psycopg
│   │   └── api/           # FastAPI (adapter de entrada)
│   └── config.py
├── scripts/indexar.py     # indexação única (entrada separada)
├── tests/
├── data/manuais/
└── docker-compose.yml
```

Regra de ouro: `domain/` e `ports/` **não importam** LangChain, Chroma, httpx ou FastAPI. LangChain/LangGraph vivem nos adapters (ou numa camada de orquestração que só fala com ports). Isso deixa trocar Chroma, modelo ou reranker sem tocar no domínio, e permite testar o domínio com fakes.

Critério de pronto: `pytest` roda com um teste de domínio usando fakes dos ports.

---

## Etapa 2: indexação única dos manuais (1 a 2 dias)

Script `scripts/indexar.py`, rodado uma vez (idempotente):

1. **Extrair** texto dos PDFs (`pymupdf` é rápido e preserva página). Guarde metadados: `marca`, `modelo`, `ano`, `arquivo`, `pagina`, `secao` (se der para inferir pelos títulos).
2. **Chunking**: comece com ~800 tokens e overlap de ~100, respeitando títulos/seções quando possível. Tabelas de torque e capacidades merecem atenção (não quebre no meio).
3. **Embeddings** com `bge-m3` via Ollama, em lote.
4. **Gravar** no ChromaDB persistente com id determinístico (`hash(arquivo+pagina+indice)`) para que rodar de novo não duplique.
5. Registrar um manifesto (`data/index_manifest.json` ou tabela no Postgres) com hash de cada PDF: se já foi indexado, pula.

Critério de pronto: uma busca por "pressão dos pneus" no manual X retorna os trechos certos com página.

---

## Etapa 3: RAG básico, sem agente (1 a 2 dias)

Caso de uso `responder_pergunta(pergunta, veiculo?)`:

1. Busca vetorial top-20 no Chroma (filtrando por modelo/ano se o usuário informou o veículo).
2. **Rerank** com `bge-reranker-v2-m3` → top-4/5.
3. Prompt para o qwen3:8b com os trechos numerados e instrução de **citar [arquivo, página]** e dizer "não encontrei no manual" quando for o caso.
4. Dica: o qwen3 tem modo de "thinking"; para respostas diretas use `/no_think` ou desligue o raciocínio na chamada, e ligue só onde ajudar.

Exponha via FastAPI: `POST /perguntas`. Critério de pronto: resposta correta e citada para 5 perguntas que você mesmo escreveu.

---

## Etapa 4: conjunto de avaliação + RAGAS (1 dia)

Faça isso **antes** de otimizar qualquer coisa:

- Escreva 20 a 30 pares `pergunta / resposta esperada / página de referência` em `tests/eval/dataset.jsonl`.
- Rode RAGAS (faithfulness, answer relevancy, context precision/recall) usando o próprio qwen3 via Ollama como juiz (é mais lento e mais ruidoso que um modelo grande, mas é gratuito; trate os números como comparação relativa entre versões).
- Guarde o resultado de cada rodada (data, config de chunk, top-k, reranker on/off) para comparar.

A partir daqui, toda mudança de chunking, top-k ou prompt é medida.

---

## Etapa 5: adapters das APIs públicas (2 dias)

Cada API é um adapter atrás de um port, com `httpx`, timeout, retry e cache simples (as APIs são gratuitas, então respeite limites; Nominatim exige `User-Agent` próprio e no máximo 1 req/s).

| Port | API | Para quê |
|---|---|---|
| VehicleDataPort | NHTSA vPIC | decodificar VIN → marca/modelo/ano/motor |
| VehicleDataPort | NHTSA Recalls | recalls por marca/modelo/ano |
| VehicleDataPort | FIPE (ex.: parallelum) | preço de referência |
| GeoPort | ViaCEP | CEP → endereço |
| GeoPort | Nominatim | endereço → lat/lon |
| GeoPort | Overpass | oficinas/autopeças próximas (`shop=car_repair`, `shop=car_parts`) |

Testes com respostas gravadas (ex.: `respx` ou `vcrpy`) para não depender da rede.

---

## Etapa 6: agente com LangGraph + tool calling (2 a 3 dias)

- Transforme os casos de uso em **tools**: `buscar_manual`, `decodificar_vin`, `consultar_recalls`, `consultar_fipe`, `oficinas_proximas(cep)`.
- Grafo simples primeiro: `roteador → (tools)* → resposta`. Limite o número de passos (o qwen3:8b às vezes entra em loop).
- Valide os argumentos das tools com Pydantic; modelos de 8B erram formato com alguma frequência, então trate o erro e devolva uma mensagem que o modelo consiga corrigir.
- Persista conversas e chamadas de tool no **PostgreSQL** (checkpointer do LangGraph para Postgres + tabelas próprias de histórico).

---

## Etapa 7: observabilidade com Arize Phoenix (meio dia)

- Suba o Phoenix no docker compose e instrumente LangChain/LangGraph com OpenInference.
- Você passa a ver cada passo: retrieval, rerank, prompts, tool calls, latência. Use isso para depurar as perguntas que o RAGAS marcou como ruins.

---

## Ordem resumida

1. Ollama + modelos + compose com Postgres
2. Esqueleto hexagonal com testes de domínio
3. Indexação única e idempotente
4. RAG básico com rerank e citações, via FastAPI
5. Dataset de avaliação + RAGAS (linha de base)
6. Adapters das APIs públicas
7. Agente LangGraph com tools + histórico no Postgres
8. Phoenix para observar e iterar

## Decisões que ficam em aberto (dá para seguir com o padrão)

- **Gerenciador de dependências:** padrão `uv`.
- **Chroma:** padrão embutido/persistente em disco (servidor só se precisar).
- **Idioma dos nomes no código:** padrão domínio em português (Veiculo, TrechoManual), infraestrutura em inglês.
