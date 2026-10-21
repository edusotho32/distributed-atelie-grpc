"""Fixtures sintéticas; nenhum registro representa pessoa ou empresa real."""

CATALOGO_SERVICOS = {
    1: {
        "nome": "Ajuste e barra simples",
        "descricao": "Ajuste de comprimento em peças de demonstração",
        "preco": 35.0,
        "prazo_dias": 2,
    },
    2: {
        "nome": "Ajuste de cintura",
        "descricao": "Ajuste de cós e pences",
        "preco": 55.0,
        "prazo_dias": 3,
    },
    3: {
        "nome": "Aplicação de pedraria",
        "descricao": "Aplicação manual em peça de demonstração",
        "preco": 120.0,
        "prazo_dias": 7,
    },
    4: {
        "nome": "Bordado computadorizado",
        "descricao": "Bordado personalizado",
        "preco": 65.0,
        "prazo_dias": 4,
    },
}
ORDENS_SERVICO = {
    1: {
        "id": 1,
        "codigo_cliente": "CLIENTE-DEMO-001",
        "status": "CONCLUIDA",
        "valor_total": 190.0,
    },
    2: {
        "id": 2,
        "codigo_cliente": "CLIENTE-DEMO-002",
        "status": "EM_EXECUCAO",
        "valor_total": 300.0,
    },
}

NOMES_GRUPOS = {
    1: "Ateliê de customização",
    2: "Sistema de barbearia",
    3: "Gestão de pet shop",
}
