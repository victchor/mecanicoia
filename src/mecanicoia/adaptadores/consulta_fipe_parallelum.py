from decimal import Decimal

import httpx

from mecanicoia.dominio.modelos import PrecoFipe
from mecanicoia.dominio.portas import ConsultaDePrecos

URL_BASE = "https://parallelum.com.br/fipe/api/v1/carros"


class ConsultaFipeParallelum(ConsultaDePrecos):
    def __init__(self, cliente: httpx.Client | None = None):
        self.cliente = cliente or httpx.Client(base_url=URL_BASE, timeout=10.0)

    def consultar(self, marca: str, modelo: str, ano: int) -> list[PrecoFipe]:
        codigo_marca = self._codigo_da_marca(marca)
        if codigo_marca is None:
            return []

        precos = []
        for codigo_modelo in self._codigos_dos_modelos(codigo_marca, modelo):
            for codigo_ano in self._codigos_dos_anos(codigo_marca, codigo_modelo, ano):
                precos.append(self._preco(codigo_marca, codigo_modelo, codigo_ano))
        return precos

    def _get(self, caminho: str):
        resposta = self.cliente.get(caminho)
        resposta.raise_for_status()
        return resposta.json()

    def _codigo_da_marca(self, marca: str) -> str | None:
        for item in self._get("/marcas"):
            if item["nome"].lower() == marca.lower():
                return item["codigo"]
        return None

    def _codigos_dos_modelos(self, codigo_marca: str, modelo: str) -> list[int]:
        dados = self._get(f"/marcas/{codigo_marca}/modelos")
        termos = modelo.lower().split()
        return [m["codigo"] for m in dados["modelos"] if all(t in m["nome"].lower() for t in termos)]

    def _codigos_dos_anos(self, codigo_marca: str, codigo_modelo: int, ano: int) -> list[str]:
        dados = self._get(f"/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos")
        return [a["codigo"] for a in dados if a["codigo"].startswith(f"{ano}-")]

    def _preco(self, codigo_marca: str, codigo_modelo: int, codigo_ano: str) -> PrecoFipe:
        dados = self._get(f"/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos/{codigo_ano}")
        return PrecoFipe(
            marca=dados["Marca"],
            modelo=dados["Modelo"],
            ano_modelo=dados["AnoModelo"],
            combustivel=dados["Combustivel"],
            codigo_fipe=dados["CodigoFipe"],
            valor=converter_valor(dados["Valor"]),
            mes_referencia=dados["MesReferencia"],
        )


def converter_valor(texto: str) -> Decimal:
    numero = texto.replace("R$", "").strip().replace(".", "").replace(",", ".")
    return Decimal(numero)