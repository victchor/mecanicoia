import ollama

resposta = ollama.chat(
    model="qwen3:8b",
    messages=[{"role": "user","content": "O que é uma junta de cabeçote? Responda em 2 frases. /no_think"}]
)

print(resposta.message.content)