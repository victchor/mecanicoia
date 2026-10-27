from decimal import Decimal

import httpx

from mecanicoia.adaptadores.consulta_fipe_parallelum import URL_BASE, ConsultaFipeParallelum, converter_valor

RESPOSTAS = {
    "/marcas": [{"codigo": "21", "nome": "Fiat"}, {"codigo": "44", "nome": "Peugeot"}],
    "/marcas/44/modelos": {
        "modelos": [
            {"codigo": 7554, "nome": "208 Allure 1.2 Flex 12V 5p Mec."},
            {"codigo": 7555, "nome": "208 Griffe 1.6 Flex 16V 5p Aut."},
        ],
        "anos": [],
    },
    "/marcas/44/modelos/7554/anos": [{"codigo": "2019-5", "nome": "2019 Flex"}, {"codigo": "2018-5", "nome": "2018 Flex"}],
    "/marcas/44/modelos/7554/anos/2018-5": {
        "Valor": "R$ 48.344,00", "Marca": "Peugeot", "Modelo": "208 Allure 1.2 Flex 12V 5p Mec.",
        "AnoModelo": 2018, "Combustivel": "Flex", "CodigoFipe": "024221-7", "MesReferencia": "outubro de 2026",
    },
}


def api_falsa(requisicao: httpx.Request) -> httpx.Response:
    caminho = requisicao.url.path.removeprefix("/fipe/api/v1/carros")
    return httpx.Response(200, json=RESPOSTAS[caminho])


def criar_consulta() -> ConsultaFipeParallelum:
    cliente = httpx.Client(base_url=URL_BASE, transport=httpx.MockTransport(api_falsa))
    return ConsultaFipeParallelum(cliente)


def test_converte_valor_em_reais():
    assert converter_valor("R$ 48.344,00") == Decimal("48344.00")


def test_encontra_preco_do_208_allure_2018():
    precos = criar_consulta().consultar("peugeot", "208 Allure", 2018)

    assert len(precos) == 1
    assert precos[0].valor == Decimal("48344.00")
    assert precos[0].codigo_fipe == "024221-7"


def test_marca_inexistente_devolve_lista_vazia():
    assert criar_consulta().consultar("Ferrari", "F40", 1990) == []