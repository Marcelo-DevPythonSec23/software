# 🔒 Plataforma Inteligente de Análise Forense Digital & CTI

**Versão:** 0.2.0 | **Status:** Análise-Ready ✅  
**Últimas Mudanças:** Refatoração completa com 6 bugs corrigidos, dashboard profissional, ML otimizado

---

## 📋 Visão Geral

Plataforma modular enterprise-ready para análise forense digital e Cyber Threat Intelligence com:
- 🔍 **Ingestão** de logs e dados de segurança
- 📊 **Normalização** em schema unificado
- 🔗 **Correlação** inteligente de eventos e IOCs
- 🤖 **Machine Learning** para detecção de anomalias
- 📈 **Dashboards** profissionais com KPIs
- 📋 **Relatórios** estruturados em HTML
- 🔐 **Segurança** com validação de inputs

---

## 🏗️ Arquitetura

```
Ingestão (CSV/JSON/LOG)
    ↓
Normalização (Schema Unificado)
    ↓
Storage (SQLAlchemy + SQLite/PostgreSQL)
    ↓
├─→ Correlation Engine (Análise de IOCs)
├─→ ML Pipeline (Detecção de Anomalias)
└─→ REST API (FastAPI)
    ↓
├─→ Dashboard (Streamlit)
└─→ Relatórios (HTML/PDF)
```

---

## 🚀 Quick Start

### 1. Instalação

```bash
cd /home/devm/projetos/software
.venv/bin/python -m pip install -r requirements.txt
```

### 2. Executar API

```bash
cd software
PYTHONPATH=sorce .venv/bin/uvicorn forensic_cti.api:app --reload --host 127.0.0.1 --port 5000
```

**API estará disponível em:** `http://localhost:5000/docs`

### 3. Executar Dashboard

```bash
cd software
.venv/bin/streamlit run sorce/forensic_cti/dashboard.py
```

**Dashboard em:** `http://localhost:8501`

### 4. Executar Testes

```bash
cd software
PYTHONPATH=sorce .venv/bin/pytest tests/test_complete.py -v
```

---

## 📊 Endpoints da API

### Health & Status
```bash
GET /health
GET /model/status
```

### Ingestão
```bash
POST /ingest/file?path=/caminho/para/arquivo.csv
```

### Eventos
```bash
GET /events?limit=100&offset=0
GET /events/search?ioc=192.168.1.1&limit=100
```

### Correlação
```bash
GET /correlation/ip?limit=100&time_window=3600
```

### Machine Learning
```bash
POST /ml/train?limit=500
POST /ml/score                          # Body: NormalizedEvent
GET /ml/cluster?limit=100
```

---

## 📁 Estrutura do Projeto

```
software/
├── sorce/forensic_cti/
│   ├── __init__.py
│   ├── __main__.py
│   ├── api.py                    # FastAPI endpoints (REFATORADO)
│   ├── config.py                 # Configurações
│   ├── correlation.py            # Engine de correlação (BUGFIX)
│   ├── db.py                     # Session de BD
│   ├── dashboard.py              # ✨ Dashboard Streamlit (NOVO)
│   ├── ingestion.py              # Ingestão de arquivos
│   ├── ml.py                     # ML pipeline (REFATORADO)
│   ├── models.py                 # ORM models (ÍNDICES ADICIONADOS)
│   ├── normalization.py          # Normalização (BUGFIX)
│   ├── reports.py                # ✨ Sistema de relatórios (NOVO)
│   ├── schema.py                 # Schemas Pydantic
│   └── storage.py                # Persistência (BUGFIX + PERFORMANCE)
├── tests/
│   ├── test_schema.py            # Testes originais
│   └── test_complete.py          # ✨ Suite completa (NOVO - 17 testes)
├── AUDITORIA_COMPLETA.md         # ✨ Auditoria detalhada (NOVO)
├── REVISAO_MELHORIAS.md          # ✨ Resumo de mudanças (NOVO)
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🎯 Principais Melhorias v0.2.0

### 🔧 Bugs Corrigidos
- ✅ **BUG #1:** Correlação circular de IPs (lógica de histórico)
- ✅ **BUG #2:** Performance crítica em search_by_ioc (O(n²) → O(1))
- ✅ **BUG #3:** Timestamps silenciosos sem logging
- ✅ **BUG #4:** ML com validação insuficiente
- ✅ **BUG #5:** Duplicação de UUIDs na persistência
- ✅ **BUG #6:** Validação ausente de IPs em correlação

### 🚀 Novas Funcionalidades
- 📊 **Dashboard Streamlit:** KPIs, timelines, heatmaps, correlações
- 📋 **Sistema de Relatórios:** HTML estruturado com descobertas e IOCs
- 🧪 **Suite de Testes:** 17 testes abrangentes (era 1)
- 📈 **ML Melhorado:** Features sofisticadas, explicabilidade, training stats

### 🔐 Segurança
- ✅ CORS restritivo (localhost only)
- ✅ Validação de path traversal
- ✅ Input validation com min/max
- ✅ Rate limiting

### 📊 Performance
- ✅ Novos índices em DB (timestamp, IPs, compostos)
- ✅ Query otimizada para search_by_ioc
- ✅ Paginação em eventos

---

## 💡 Exemplos de Uso

### Exemplo 1: Ingestão e Correlação

```bash
# 1. Ingestão de arquivo CSV
curl -X POST "http://localhost:5000/ingest/file?path=/dados/logs.csv"

# 2. Correlacionar IPs
curl "http://localhost:5000/correlation/ip?time_window=3600"

# 3. Buscar por IOC
curl "http://localhost:5000/events/search?ioc=192.168.1.100"
```

### Exemplo 2: ML e Anomalias

```bash
# 1. Treinar modelo
curl -X POST "http://localhost:5000/ml/train?limit=500"

# 2. Avaliar evento
curl -X POST "http://localhost:5000/ml/score" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "login_attempt",
    "severity": "high",
    "source_ip": "192.168.1.100",
    "destination_ip": "10.0.0.1",
    "raw_source": "syslog"
  }'

# 3. Agrupar eventos
curl "http://localhost:5000/ml/cluster?limit=100"
```

### Exemplo 3: Relatórios

```python
from forensic_cti.reports import ReportGenerator, AnalysisReport

# Gerar a partir de análise de correlação
report = AnalysisReport.from_correlation_analysis(correlation_data)
report.add_recommendation("Investigar IP suspeita", priority="high")
html_path = report.save_html("analise_correlacao.html")

# Ou criar manualmente
report = ReportGenerator("Análise Customizada")
report.add_finding("Descoberta 1", "Descrição", severity="critical", events_count=45)
report.add_ioc("192.168.1.100", "ip", "high", "Detecção ML", "Source IP anômalo")
html_path = report.save_html("relatorio_customizado.html")
```

---

## 📊 Dashboard Streamlit

Acesse em: `http://localhost:8501`

### Abas Disponíveis

1. **📊 EVENTOS**
   - KPIs: Total, Severidade, Anomalias, Críticos
   - Distribuição de Severidade (pie chart)
   - Timeline (últimas 24h)
   - Tipos de Eventos (top 10)
   - Tabela de eventos recentes

2. **🔗 CORRELAÇÃO**
   - Busca por IOC
   - Correlação de IPs
   - Heatmap de IOCs reutilizados

3. **🤖 ML & ANOMALIAS**
   - Status do modelo
   - Ações: Treinar, Agrupar
   - Avaliador de eventos individual
   - Score com explicação

4. **📋 RELATÓRIOS**
   - Resumo executivo
   - Principais descobertas
   - Indicadores de ameaça
   - Recomendações

---

## 🧪 Testes

### Executar suite completa
```bash
PYTHONPATH=sorce pytest tests/test_complete.py -v
```

### Cobertura de testes
- ✅ Normalization: 6 testes
- ✅ Correlation: 3 testes
- ✅ ML: 4 testes
- ✅ Storage: 2 testes
- ✅ API: 2 testes
- **Total:** 17 testes

---

## 🔒 Configuração

### Variáveis de Ambiente

```bash
# .env
DATABASE_URL=sqlite:///forensic_cti.db
API_HOST=127.0.0.1
API_PORT=5000
LOG_LEVEL=INFO
MODEL_PATH=sorce/models/threat_model.joblib
```

### Segurança de CORS

```python
# api.py - Apenas localhost
allow_origins=["http://localhost:3000", "http://localhost:8501"]
```

---

## 📈 Roadmap (Fase 2)

- [ ] Autenticação (JWT/OAuth)
- [ ] RBAC (Role-Based Access Control)
- [ ] Integrações externas reais (VirusTotal, Shodan, AbuseIPDB)
- [ ] PostgreSQL em produção
- [ ] Elasticsearch/OpenSearch
- [ ] LIME/SHAP para explicabilidade
- [ ] Alertas em tempo real
- [ ] Export em PDF/Excel
- [ ] MITRE ATT&CK mapping

---

## 📚 Documentação

- **AUDITORIA_COMPLETA.md** - Análise detalhada de 42 problemas identificados
- **REVISAO_MELHORIAS.md** - Resumo executivo das mudanças
- **tests/test_complete.py** - Exemplos de testes
- **docstrings** - Documentação inline em todo o código

---

## 🤝 Contribuição

1. Mantenha a estrutura de pacotes em `sorce/`
2. Use `pydantic` para validação
3. Adicione testes em `tests/`
4. Documente novos endpoints em README

---

## 📄 Licença

Propriedade da Empresa.

---

## 🆘 Suporte

Para problemas ou dúvidas, verifique:
1. `AUDITORIA_COMPLETA.md` - Problemas conhecidos
2. `REVISAO_MELHORIAS.md` - Mudanças implementadas
3. Logs de API em `stdout` (LOG_LEVEL=DEBUG)

---

**Última atualização:** 2026-06-07 | **Versão:** 0.2.0 ✅
