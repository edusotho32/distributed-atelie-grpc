# Ateliê Distribuído com gRPC

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![gRPC](https://img.shields.io/badge/gRPC-Protocol%20Buffers-244C5A?logo=google&logoColor=white)](https://grpc.io/)
[![CI](https://github.com/edusotho32/distributed-atelie-grpc/actions/workflows/ci.yml/badge.svg)](https://github.com/edusotho32/distributed-atelie-grpc/actions/workflows/ci.yml)

Estudo de caso acadêmico que expõe regras de orçamento e consultas de ordens de serviço por RPC tipado. O foco técnico é mostrar a fronteira entre contrato (`.proto`), validação no servidor, serialização Protocol Buffers e teste de integração real cliente-servidor.

> Todos os registros são sintéticos. A versão pública não contém CPF, telefone, endereço, credenciais, runtime embarcado ou fontes Java de terceiros.

## Problema de engenharia

O protótipo original misturava código-fonte, runtimes pesados e dados de demonstração com aparência de dados pessoais. Esta versão isola o núcleo distribuído e torna verificáveis três comportamentos: contrato estável, regras de negócio determinísticas e falhas gRPC explícitas para entradas inválidas.

```mermaid
flowchart LR
    C[Cliente Python] -->|HTTP/2 + Protobuf| G[Servidor gRPC]
    G --> M[MuralService]
    G --> A[AtelieService]
    A --> R[Validação e regras de orçamento]
    R --> D[Fixtures sintéticas em memória]
    P[atelie.proto] --> C
    P --> G
```

## Regras demonstradas

- 10% de desconto quando o orçamento soma pelo menos cinco peças.
- taxa expressa de 25% aplicada depois do desconto.
- prazo expresso reduzido pela metade, com mínimo de um dia.
- rejeição explícita de serviço inexistente e quantidade não positiva.
- contador do mural protegido por lock para chamadas concorrentes.

## Executar localmente

Requer Python 3.11 ou superior.

```powershell
python -m pip install -e .
python scripts/demo.py
```

Para manter o servidor aberto, execute `python -m atelie_grpc.server`; em outro terminal, execute `python -m atelie_grpc.client`.

## Testes automatizados

```powershell
python -m unittest discover -s tests -v
```

Os testes cobrem regras de preço, validação de entrada e um round trip gRPC real em porta efêmera.

## Estrutura

```text
proto/atelie_grpc/atelie.proto   contrato público
src/atelie_grpc/                 servidor, cliente e fixtures sintéticas
tests/                           testes unitários e de integração
scripts/                         demo e regeneração de stubs
docs/schema.sql                  modelo relacional sanitizado de referência
PROVENANCE.md                    origem e limites de autoria
```

## Regenerar os stubs

```powershell
python -m pip install -e ".[dev]"
python scripts/generate_stubs.py
```

## Escopo e limitações

O servidor usa dados em memória para manter a demonstração reproduzível; `docs/schema.sql` documenta um desenho relacional, mas não está conectado ao serviço. O canal é inseguro e adequado apenas ao ambiente local. Consulte [PROVENANCE.md](PROVENANCE.md) antes de citar o projeto em currículo ou entrevista.
