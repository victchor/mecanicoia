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


@dataclass
class Pagina:
    arquivo: str
    numero: int
    texto: str


@dataclass
class Chunk:
    arquivo: str
    pagina: int
    indice: int
    texto: str

    @property
    def id(self) -> str:
        return f"{self.arquivo}:p{self.pagina}:c{self.indice}"
