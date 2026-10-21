from __future__ import annotations

from concurrent import futures
from datetime import date, datetime, timedelta
from threading import Lock

import grpc

from atelie_grpc import atelie_pb2, atelie_pb2_grpc
from atelie_grpc.data import CATALOGO_SERVICOS, NOMES_GRUPOS, ORDENS_SERVICO


class MuralService(atelie_pb2_grpc.MuralServiceServicer):
    def __init__(self) -> None:
        self._acessos = {grupo_id: 0 for grupo_id in NOMES_GRUPOS}
        self._lock = Lock()

    def ObterMural(self, request, context):  # noqa: N802 - nome definido no contrato gRPC
        if request.id_grupo not in NOMES_GRUPOS:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "grupo inexistente")

        with self._lock:
            self._acessos[request.id_grupo] += 1
            ranking = sorted(
                self._acessos.items(), key=lambda item: (-item[1], item[0])
            )

        agora = datetime.now().astimezone().isoformat(timespec="seconds")
        return atelie_pb2.RespostaMural(
            id_grupo=request.id_grupo,
            nome_grupo=NOMES_GRUPOS[request.id_grupo],
            ultima_atualizacao=agora,
            ranking=[
                atelie_pb2.ContadorGrupo(
                    id_grupo=grupo_id,
                    nome_grupo=NOMES_GRUPOS[grupo_id],
                    quantidade_utilizacoes=quantidade,
                )
                for grupo_id, quantidade in ranking
            ],
            avisos_grupo=[
                atelie_pb2.AvisoGrupo(
                    id_grupo=request.id_grupo,
                    titulo="Canal gRPC ativo",
                    mensagem="Contrato Protocol Buffers processado com sucesso.",
                    timestamp=agora,
                )
            ],
        )


class AtelieService(atelie_pb2_grpc.AtelieServiceServicer):
    def __init__(self, today_provider=date.today) -> None:
        self._today_provider = today_provider

    def ConsultarOrdemServico(self, request, context):  # noqa: N802
        ordem = ORDENS_SERVICO.get(request.id_ordem_servico)
        if ordem is None:
            return atelie_pb2.OrdemServicoResponse(
                encontrada=False,
                id=request.id_ordem_servico,
                mensagem_erro="ordem de serviço não encontrada",
            )
        return atelie_pb2.OrdemServicoResponse(encontrada=True, **ordem)

    def ListarTiposServico(self, request, context):  # noqa: N802
        return atelie_pb2.ListaTiposServicoResponse(
            servicos=[
                atelie_pb2.TipoServico(
                    id=servico_id,
                    nome=servico["nome"],
                    descricao=servico["descricao"],
                    preco_base=servico["preco"],
                    prazo_estimado_dias=servico["prazo_dias"],
                )
                for servico_id, servico in sorted(CATALOGO_SERVICOS.items())
            ]
        )

    def CalcularOrcamento(self, request, context):  # noqa: N802
        if not request.itens:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "informe ao menos um item")

        itens_resposta = []
        valor_bruto = 0.0
        total_pecas = 0
        maior_prazo = 0

        for item in request.itens:
            if item.quantidade_pecas <= 0:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "a quantidade deve ser maior que zero",
                )
            servico = CATALOGO_SERVICOS.get(item.id_tipo_servico)
            if servico is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"tipo de serviço {item.id_tipo_servico} não encontrado",
                )

            subtotal = servico["preco"] * item.quantidade_pecas
            valor_bruto += subtotal
            total_pecas += item.quantidade_pecas
            maior_prazo = max(maior_prazo, servico["prazo_dias"])
            itens_resposta.append(
                atelie_pb2.ItemOrcamentoResponse(
                    nome_servico=servico["nome"],
                    quantidade_pecas=item.quantidade_pecas,
                    preco_unitario=servico["preco"],
                    subtotal=subtotal,
                    prazo_dias=servico["prazo_dias"],
                )
            )

        regras = []
        desconto = valor_bruto * 0.10 if total_pecas >= 5 else 0.0
        if desconto:
            regras.append("DESCONTO_VOLUME_10")

        base_apos_desconto = valor_bruto - desconto
        taxa_urgencia = base_apos_desconto * 0.25 if request.entrega_expressa else 0.0
        prazo_final = max(1, maior_prazo // 2) if request.entrega_expressa else maior_prazo
        if request.entrega_expressa:
            regras.append("ENTREGA_EXPRESSA_25")

        return atelie_pb2.OrcamentoResponse(
            codigo_cliente=request.codigo_cliente or "CLIENTE-ANONIMO",
            itens=itens_resposta,
            valor_bruto=round(valor_bruto, 2),
            desconto=round(desconto, 2),
            taxa_urgencia=round(taxa_urgencia, 2),
            valor_final=round(base_apos_desconto + taxa_urgencia, 2),
            prazo_total_dias=prazo_final,
            data_estimada_entrega=(
                self._today_provider() + timedelta(days=prazo_final)
            ).isoformat(),
            regras_aplicadas=regras,
        )


def create_server(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atelie_pb2_grpc.add_MuralServiceServicer_to_server(MuralService(), server)
    atelie_pb2_grpc.add_AtelieServiceServicer_to_server(AtelieService(), server)
    bound_port = server.add_insecure_port(f"127.0.0.1:{port}")
    if bound_port == 0:
        raise RuntimeError(f"não foi possível vincular a porta {port}")
    return server, bound_port


def main() -> None:
    server, port = create_server()
    server.start()
    print(f"Servidor gRPC disponível em 127.0.0.1:{port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=2)


if __name__ == "__main__":
    main()
