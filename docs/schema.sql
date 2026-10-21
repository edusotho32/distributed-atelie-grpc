-- Esquema público sanitizado. Todos os exemplos são sintéticos.
CREATE TABLE cliente_demo (
    id BIGSERIAL PRIMARY KEY,
    codigo_externo VARCHAR(40) UNIQUE NOT NULL
);
CREATE TABLE tipo_servico (
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    valor NUMERIC(10, 2) NOT NULL CHECK (valor >= 0),
    prazo_estimado_dias INTEGER NOT NULL CHECK (prazo_estimado_dias > 0)
);

CREATE TABLE ordem_servico (
    id BIGSERIAL PRIMARY KEY,
    cliente_id BIGINT NOT NULL REFERENCES cliente_demo(id),
    status VARCHAR(30) NOT NULL,
    valor_total NUMERIC(10, 2) NOT NULL CHECK (valor_total >= 0)
);
