from pathlib import Path

import pymupdf

from mecanicoia.dominio.modelos import Pagina
from mecanicoia.dominio.portas import LeitorDeDocumentos


class LeitorPyMuPDF(LeitorDeDocumentos):
    def ler(self, caminho: Path) -> list[Pagina]:
        paginas = []
        with pymupdf.open(caminho) as documento:
            for numero, pagina in enumerate(documento, start=1):
                texto = pagina.get_text()
                if texto.strip():
                    paginas.append(Pagina(arquivo=caminho.name, numero=numero, texto=texto))
        return paginas