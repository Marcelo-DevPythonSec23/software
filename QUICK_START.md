# 🚀 QUICK START - FORENSIC CTI v0.2.0

## ✅ PRÉ-REQUISITOS

- Python 3.11+
- pip com acesso a PyPI
- ~500MB de espaço em disco

## 🔧 INSTALAÇÃO (5 minutos)

### Passo 1: Ativar venv e instalar dependências

```bash
cd /home/dev_marcelo/projetos/software
source .venv/bin/activate
pip install -r requirements.txt
```

### Passo 2: Criar arquivo `.env` (opcional)

```bash
cat > /home/dev_marcelo/projetos/software/software/.env << EOF
DATABASE_URL=sqlite:///forensic_cti.db
API_HOST=127.0.0.1
API_PORT=5000
LOG_LEVEL=INFO
MODEL_PATH=sorce/models/threat_model.joblib
EOF
```

---

## 🚀 INICIAR O SISTEMA

### Terminal 1: API FastAPI

```bash
cd /home/dev_marcelo/projetos/software/software
export PYTHONPATH=sorce
.venv/bin/uvicorn forensic_cti.api:app --reload --host 127.0.0.1 --port 5000
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:5000
INFO:     Application startup completed
```

Acesse: http://localhost:5000/docs (Swagger UI)

### Terminal 2: Dashboard Streamlit

```bash
cd /home/dev_marcelo/projetos/software/software
export PYTHONPATH=sorce
.venv/bin/streamlit run sorce/forensic_cti/dashboard.py
```

**Saída esperada:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

Acesse: http://localhost:8501

---

## 📊 PRIMEIROS PASSOS

### 1️⃣ Ingestão de Dados

**Criar arquivo de teste:**
```bash
cat > /tmp/test_events.csv << 'EOF'
timestamp,source_ip,destination_ip,event_type,severity
2026-06-07T14:00:00,192.168.1.100,10.0.0.1,login_attempt,high
2026-06-07T14:05:00,192.168.1.100,10.0.0.2,access_denied,medium
2026-06-07T14:10:00,192.168.1.100,10.0.0.3,file_access,low
2026-06-07T14:15:00,192.168.1.101,10.0.0.1,login_attempt,critical
2026-06-07T14:20:00,192.168.1.100,10.0.0.4,process_execution,high
EOF
```

**Ingestão via API:**
```bash
curl -X POST "http://localhost:5000/ingest/file?path=/tmp/test_events.csv"
```

**Resposta esperada:**
```json
{"ingested": 5}
```

### 2️⃣ Visualizar Eventos

**Via API:**
```bash
curl "http://localhost:5000/events?limit=10" | jq '.'
```

**Via Dashboard:**
- Acesse http://localhost:8501
- Vá para a aba "📊 EVENTOS"
- Visualize os KPIs e timeline

### 3️⃣ Treinar Modelo ML

**Via API:**
```bash
curl -X POST "http://localhost:5000/ml/train?limit=100"
```

**Resposta esperada:**
```json
{
  "trained": true,
  "events_used": 5,
  "stats": {
    "events_trained": 5,
    "anomalies_detected": 1,
    "anomaly_percentage": 20.0
  }
}
```

### 4️⃣ Buscar por IOC

**Via API:**
```bash
curl "http://localhost:5000/events/search?ioc=192.168.1.100&limit=10" | jq '.'
```

**Via Dashboard:**
- Acesse http://localhost:8501
- Vá para a aba "🔗 CORRELAÇÃO"
- Digite o IOC (IP, domínio)
- Clique em "🔍 Buscar"

### 5️⃣ Correlacionar IPs

**Via API:**
```bash
curl "http://localhost:5000/correlation/ip?time_window=3600" | jq '.'
```

**Via Dashboard:**
- Clique em "🔗 Correlacionar"
- Ajuste a janela temporal
- Visualize IOCs reutilizadas

### 6️⃣ Gerar Relatório

**Python:**
```python
from forensic_cti.reports import ReportGenerator

report = ReportGenerator("Meu Primeiro Relatório")
report.add_finding(
    "Atividade Suspeita Detectada",
    "IP 192.168.1.100 com múltiplas tentativas de login",
    severity="high",
    events_count=5
)
report.add_ioc(
    "192.168.1.100",
    "ip",
    "high",
    "Detecção ML",
    "Source IP em múltiplos eventos críticos"
)
report.add_recommendation(
    "Bloquear IP na firewall e investigar histórico",
    priority="critical"
)
html_path = report.save_html("/tmp/relatorio.html")
print(f"✅ Relatório: {html_path}")
```

---

## 🧪 EXECUTAR TESTES

```bash
cd /home/dev_marcelo/projetos/software/software
export PYTHONPATH=sorce
.venv/bin/pytest tests/test_complete.py -v
```

**Saída esperada:**
```
tests/test_complete.py::TestNormalization::test_normalize_record_with_all_fields PASSED
tests/test_complete.py::TestCorrelation::test_correlate_by_ip_same_window PASSED
tests/test_complete.py::TestMachineLearning::test_threat_model_train_sufficient_events PASSED
...
=================== 17 passed in 0.50s ===================
```

---

## 📚 DOCUMENTAÇÃO

| Arquivo | Conteúdo |
|---------|----------|
| `README.md` | Guia completo de uso |
| `AUDITORIA_COMPLETA.md` | Análise de 42 problemas encontrados |
| `REVISAO_MELHORIAS.md` | Detalhamento de 6 bugs corrigidos |
| `SUMARIO_EXECUTIVO.md` | Resumo executivo das mudanças |
| `tests/test_complete.py` | 17 testes de validação |

---

## 🎯 CASOS DE USO COMUNS

### Caso 1: Análise de Investigação Rápida

```bash
# 1. Ingestão
curl -X POST "http://localhost:5000/ingest/file?path=/logs/investigation.csv"

# 2. Buscar IOC
curl "http://localhost:5000/events/search?ioc=SUSPICIOUS_IP"

# 3. Correlacionar
curl "http://localhost:5000/correlation/ip"

# 4. Gerar relatório
# (via Python ou Dashboard)
```

### Caso 2: Detecção de Anomalias

```bash
# 1. Treinar modelo
curl -X POST "http://localhost:5000/ml/train"

# 2. Avaliar evento
curl -X POST "http://localhost:5000/ml/score" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "suspicious_activity",
    "severity": "high",
    "source_ip": "192.168.1.100",
    "destination_ip": "10.0.0.1",
    "raw_source": "investigation"
  }'
```

### Caso 3: Análise de Padrão de Ataque

```bash
# 1. Ingestão de múltiplos logs
for file in /logs/*.csv; do
  curl -X POST "http://localhost:5000/ingest/file?path=$file"
done

# 2. Agrupar em clusters
curl "http://localhost:5000/ml/cluster?limit=1000"

# 3. Visualizar no Dashboard
# Vá para aba "🤖 ML & ANOMALIAS"
```

---

## ⚙️ CONFIGURAÇÃO

### Variáveis de Ambiente

```bash
# Database
DATABASE_URL=sqlite:///forensic_cti.db

# API
API_HOST=127.0.0.1
API_PORT=5000

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# ML
MODEL_PATH=sorce/models/threat_model.joblib
```

### Limites e Timeouts

```python
# api.py - Ajustáveis
MAX_QUERY_LIMIT = 500
MAX_INGEST_SIZE = 100 * 1024 * 1024  # 100MB
ML_CONTAMINATION = 0.05
ML_MIN_EVENTS = 50
```

---

## 🆘 TROUBLESHOOTING

### Problema: "ModuleNotFoundError: No module named 'forensic_cti'"

**Solução:**
```bash
export PYTHONPATH=sorce  # Antes de rodar
```

### Problema: "Address already in use"

**Solução:**
```bash
# Encontre o processo
lsof -i :5000
lsof -i :8501

# Mate o processo
kill -9 <PID>
```

### Problema: "Banco de dados vazio"

**Solução:**
```bash
# Remova o DB e reinicie
rm forensic_cti.db
# API recriará na próxima execução
```

---

## 🔗 Links Úteis

- 📖 **API Docs:** http://localhost:5000/docs
- 📊 **Dashboard:** http://localhost:8501
- 📁 **Projeto:** /home/dev_marcelo/projetos/software/software
- 📝 **Logs:** stdout (ou configurar arquivo)

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [ ] API rodando em localhost:5000
- [ ] Dashboard rodando em localhost:8501
- [ ] Arquivo de teste CSV criado
- [ ] Ingestão de dados concluída
- [ ] Modelo ML treinado
- [ ] Correlação funcionando
- [ ] Relatório gerado com sucesso
- [ ] Todos os 17 testes passando

---

## 🎓 PRÓXIMAS AÇÕES

1. **Explorar Dashboard:** Familiarizar-se com as visualizações
2. **Testar com Dados Reais:** Usar seus próprios CSVs/JSONs
3. **Ajustar Parâmetros:** Tunar time_window, contamination, etc
4. **Gerar Relatórios:** Automatizar geração de análises
5. **Integrar Dados Externos:** (Fase 2) VirusTotal, Shodan

---

## 📞 SUPORTE

**Documentação Técnica:**
- `AUDITORIA_COMPLETA.md` - Problemas conhecidos
- `REVISAO_MELHORIAS.md` - O que foi corrigido
- `README.md` - Referência completa

**Contato:**
- Código comentado em cada módulo
- Docstrings com exemplos de uso

---

**Última atualização:** 2026-06-07  
**Versão:** 0.2.0  
**Status:** ✅ Pronto para uso
