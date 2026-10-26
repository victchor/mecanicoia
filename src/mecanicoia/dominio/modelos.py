from dataclasses import dataclass, field


@dataclass
class Trecho:
    arquivo: str
    pagina: int
    texto: str
    nota: float | None = None


@dataclass
class Resposta:
    texto: str
    fontes: list[Trecho] = field(default_factory=list)