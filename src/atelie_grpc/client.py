import grpc

from atelie_grpc import atelie_pb2, atelie_pb2_grpc


def run(target: str = "127.0.0.1:50051") -> None:
    with grpc.insecure_channel(target) as channel:
        mural = atelie_pb2_grpc.MuralServiceStub(channel)
        atelie = atelie_pb2_grpc.AtelieServiceStub(channel)

        resposta_mural = mural.ObterMural(atelie_pb2.MuralRequest(id_grupo=1))
        print(f"Mural: {resposta_mural.nome_grupo}")

        resposta = atelie.CalcularOrcamento(
            atelie_pb2.OrcamentoRequest(
                codigo_cliente="CLIENTE-DEMO-CLI",
                itens=[
                    atelie_pb2.ItemOrcamentoRequest(
                        id_tipo_servico=1, quantidade_pecas=5
                    )
                ],
                entrega_expressa=True,
            )
        )
        print(
            "Orçamento: "
            f"bruto={resposta.valor_bruto:.2f}, "
            f"desconto={resposta.desconto:.2f}, "
            f"urgência={resposta.taxa_urgencia:.2f}, "
            f"final={resposta.valor_final:.2f}"
        )


if __name__ == "__main__":
    run()
