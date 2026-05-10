# Plataforma Inteligente de Análise Forense & CTI

## Visão Geral

Esta documentação descreve a plataforma modular de análise forense digital e Cyber Threat Intelligence projetada para ingestão, normalização, correlação, persistência e análise de grandes volumes de dados de segurança.

A plataforma foi construída como um MVP enterprise-ready, com foco em arquitetura extensível, padrão de dados unificado e APIs REST para integração com dashboards e orquestração.

## Arquitetura

A plataforma está dividida em camadas principais:

- **Ingestion Layer**: coleta de logs e dados de segurança a partir de arquivos e fontes externas.
- **Normalization Layer**: converte dados heterogêneos em um schema único (`NormalizedEvent`).
- **Storage Layer**: persistência transacional com SQLAlchemy ORM e suporte inicial a SQLite/PostgreSQL.
- **Correlation Engine**: identifica relações entre eventos, IOC reutilizados e padrão de ataque.
- **ML Layer**: detecção de anomalias e agrupamento de eventos para investigação.
- **API Layer**: exposição de serviços via FastAPI, com endpoints para ingestão, consulta, correlação e análise.

## Fluxo de Dados

1. Coleta de dados de arquivos CSV/JSON/LOG e integrações externas.
2. Normalização para um schema centralizado.
3. Persistência em banco de dados relacional com modelo de eventos.
4. Correlação de eventos e busca de IOC.
5. Análise de anomalias via modelo ML.
6. Exposição de resultados via API para dashboards e automação.

## Componentes do Código

- `src/forensic_cti/ingestion.py`: ingestão de arquivos locais e stubs para fontes externas.
- `src/forensic_cti/normalization.py`: normalização de registros brutos para o schema de eventos.
- `src/forensic_cti/schema.py`: modelos Pydantic para validação e tipagem do evento.
- `src/forensic_cti/models.py`: mapeamento ORM de persistência de eventos.
- `src/forensic_cti/db.py`: configuração de conexão de banco e sessão.
- `src/forensic_cti/storage.py`: abstração de armazenamento e buscas.
- `src/forensic_cti/correlation.py`: regras de correlação e identificação de IOC reutilizados.
- `src/forensic_cti/ml.py`: modelo de detecção de anomalias e clusterização.
- `src/forensic_cti/api.py`: API FastAPI com endpoints de ingestão, consulta, correlação e ML.

## Instalação

```bash
cd /home/devm/projetos/software
.venv/bin/python -m pip install -r requirements.txt
```

## Configuração

As configurações base são carregadas por `src/forensic_cti/config.py` e podem ser definidas via variáveis de ambiente:

- `DATABASE_URL`: string de conexão do banco de dados (padrão `sqlite:///forensic_cti.db`)
- `API_HOST`: host do serviço FastAPI
- `API_PORT`: porta do serviço

Para carregar variáveis de ambiente, crie um arquivo `.env` no diretório raiz.

## Execução

```bash
cd /home/devm/projetos/software
PYTHONPATH=src .venv/bin/uvicorn forensic_cti.api:app --reload --host 127.0.0.1 --port 5000
```

Ou:

```bash
cd /home/devm/projetos/software
PYTHONPATH=src .venv/bin/python -m forensic_cti
```

## Endpoints da API

### Saúde do serviço
- `GET /health`
  - Retorna o status do serviço.

### Ingestão
- `POST /ingest/file`
  - Parâmetro: `path` (caminho do arquivo local)
  - Ingestão de CSV/JSON/LOG para o armazenamento.

### Eventos
- `GET /events`
  - Lista eventos persistidos.
  - Parâmetro opcional: `limit`.
- `GET /events/search`
  - Busca IOC em `source_ip`, `destination_ip` e metadados.
  - Parâmetros: `ioc`, `limit`.

### Correlação
- `GET /correlation/ip`
  - Correlaciona eventos por IP e identifica IOC reutilizados.

### Machine Learning
- `POST /ml/train`
  - Treina o modelo de anomalias com eventos existentes.
- `POST /ml/score`
  - Recebe um evento e retorna score de anomalia.

### Integrações externas
- `POST /external/virustotal`
- `POST /external/shodan`
- `POST /external/abuseipdb`

Esses endpoints atualmente usam stubs para simular ingestão de dados externos.

## Cenários de Uso

- Ingestão de logs de investigação forense
- Normalização de eventos para correlação e dashboard
- Busca de IOC e análise de comportamento suspeito
- Treinamento de modelos para detecção de anomalias em eventos de segurança

## Desenvolvimento

1. Ative o virtualenv:

```bash
source .venv/bin/activate
```

2. Execute o servidor:

```bash
PYTHONPATH=src uvicorn forensic_cti.api:app --reload
```

3. Rode testes com pytest após instalar as dependências:

```bash
.venv/bin/python -m pytest tests
```

## Roadmap

- Adicionar migrações com Alembic
- Suporte a PostgreSQL e OpenSearch/Elasticsearch
- Conectores para Sysmon, Zeek, Suricata
- Campos avançados de MITRE ATT&CK e IOC enrichment
- Dashboards interativos e relatórios automáticos
- Exportação de datasets em JSON/CSV/Parquet

## Contribuição

- Siga o padrão de pacotes em `src/`
- Utilize `pydantic` para validação de payloads
- Mantenha a separação entre ingestão, normalização, persistência e análise
- Documente novos endpoints e modelos no README
