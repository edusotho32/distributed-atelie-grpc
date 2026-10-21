from datetime import date
import unittest

import grpc

from atelie_grpc import atelie_pb2, atelie_pb2_grpc
from atelie_grpc.server import AtelieService, create_server


class AbortError(Exception):
    def __init__(self, code, details):
        super().__init__(details)
        self.code = code


class FakeContext:
    def abort(self, code, details):
        raise AbortError(code, details)


class AtelieServiceUnitTests(unittest.TestCase):
    def setUp(self):
        self.service = AtelieService(today_provider=lambda: date(2026, 1, 10))
        self.context = FakeContext()

    def test_aplica_desconto_de_volume(self):
        response = self.service.CalcularOrcamento(
            atelie_pb2.OrcamentoRequest(
                codigo_cliente="TESTE",
                itens=[
                    atelie_pb2.ItemOrcamentoRequest(
                        id_tipo_servico=1, quantidade_pecas=5
                    )
                ],
            ),
            self.context,
        )
        self.assertEqual(175.0, response.valor_bruto)
        self.assertEqual(17.5, response.desconto)
        self.assertEqual(157.5, response.valor_final)
        self.assertEqual(["DESCONTO_VOLUME_10"], list(response.regras_aplicadas))

    def test_taxa_expressa_incide_apos_desconto(self):
        response = self.service.CalcularOrcamento(
            atelie_pb2.OrcamentoRequest(
                itens=[
                    atelie_pb2.ItemOrcamentoRequest(
                        id_tipo_servico=1, quantidade_pecas=5
                    )
                ],
                entrega_expressa=True,
            ),
            self.context,
        )
        self.assertEqual(39.38, response.taxa_urgencia)
        self.assertEqual(196.88, response.valor_final)
        self.assertEqual("2026-01-11", response.data_estimada_entrega)

    def test_rejeita_quantidade_invalida(self):
        with self.assertRaises(AbortError) as captured:
            self.service.CalcularOrcamento(
                atelie_pb2.OrcamentoRequest(
                    itens=[
                        atelie_pb2.ItemOrcamentoRequest(
                            id_tipo_servico=1, quantidade_pecas=0
                        )
                    ]
                ),
                self.context,
            )
        self.assertEqual(grpc.StatusCode.INVALID_ARGUMENT, captured.exception.code)

    def test_rejeita_servico_inexistente(self):
        with self.assertRaises(AbortError) as captured:
            self.service.CalcularOrcamento(
                atelie_pb2.OrcamentoRequest(
                    itens=[
                        atelie_pb2.ItemOrcamentoRequest(
                            id_tipo_servico=999, quantidade_pecas=1
                        )
                    ]
                ),
                self.context,
            )
        self.assertEqual(grpc.StatusCode.NOT_FOUND, captured.exception.code)


class GrpcIntegrationTests(unittest.TestCase):
    def test_round_trip_real(self):
        server, port = create_server(port=0)
        server.start()
        try:
            with grpc.insecure_channel(f"127.0.0.1:{port}") as channel:
                stub = atelie_pb2_grpc.AtelieServiceStub(channel)
                response = stub.ListarTiposServico(atelie_pb2.Vazio(), timeout=3)
                self.assertGreaterEqual(len(response.servicos), 4)
        finally:
            server.stop(grace=0).wait()


if __name__ == "__main__":
    unittest.main()
