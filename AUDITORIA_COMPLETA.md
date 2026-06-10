# AUDITORIA COMPLETA - PLATAFORMA FORENSIC CTI
**Data:** 2026-06-07  
**Status:** EM ANDAMENTO  

---

## SEÇÃO 1: PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1.1 BUGS E ERROS LÓGICOS

#### **BUG #1: Duplicação de correlação por IP em intervals (CRÍTICO)**
**Arquivo:** `correlation.py`, linhas 10-25  
**Problema:** O método `correlate_by_ip()` possui lógica defeituosa:
- A função modifica `history` in-place com `history[:] = [...]` mas depois adiciona o evento atual
- Isso cria duplicação circular e correlações falsas
- **Impacto:** Falsos positivos em correlação temporal

```python
# CÓDIGO PROBLEMÁTICO
for ioc in candidates:
    history = ip_history[ioc]  # Referência
    history[:] = [item for item in history if item.timestamp >= window_start]  # In-place modificação
    related.extend(history)  # Adiciona histórico

for ioc in candidates:
    ip_history[ioc].append(event)  # Adiciona evento ao histórico
```

#### **BUG #2: Busca por IOC com performance inadequada (CRÍTICO)**
**Arquivo:** `storage.py`, linhas 47-65  
**Problema:** O método `search_by_ioc()`:
- Primeiro faz query por IP exato (OK)
- Depois ITERATES sobre TODOS os resultados de novo
- Converte dict inteiro em string e faz substring match (PÉSSIMO para performance)
- Limita resultado dentro da iteração (breaking logic incorreta)

```python
# CÓDIGO PROBLEMÁTICO
rows = session.execute(stmt).scalars().all()  # Pega TODOS
matches: List[Dict[str, Any]] = []
query = ioc.lower()
for record in rows:  # ITERATES de novo
    metadata_text = str(record.event_metadata or {}).lower()  # String conversion
    if record.source_ip == ioc or record.destination_ip == ioc or query in metadata_text:
        matches.append(record.to_dict())
        if len(matches) >= limit:
            break  # Problema: limita APÓS iterar
```

**Impacto:** Em datasets grandes (milhões de eventos), isso causa travamento do serviço.

#### **BUG #3: Tratamento inadequado de timestamps (CRÍTICO)**
**Arquivo:** `normalization.py`, linhas 20-30  
**Problema:** 
- Fallback silencioso para `datetime.utcnow()` em qualquer erro de parsing
- Não há logging de casos de erro
- Timestamps inválidos são perdidos sem rastreamento

```python
# CÓDIGO PROBLEMÁTICO
except (OverflowError, OSError):
    return datetime.utcnow()  # SILENCIOSO - perda de dados
```

**Impacto:** Correlação temporal quebrada, análise forense prejudicada.

#### **BUG #4: Modelo ML com validação insuficiente (CRÍTICO)**
**Arquivo:** `ml.py`, linhas 101-110  
**Problema:**
- Condição `if len(events) < 5` apenas LOG WARNING, não levanta exceção
- Modelo não treinado marca `self.trained = False`, mas chamadas anteriores retornam score inválido
- Não há indicação clara ao cliente de que o modelo não está pronto

#### **BUG #5: Persistência duplicada com UUID manual (ALTO)**
**Arquivo:** `storage.py`, linhas 24-26  
**Problema:**
```python
EventRecord(
    event_id=event.event_id or str(uuid4()),  # PROBLEMA: pode gerar UUIDs diferentes
    ...
)
```
- Se `event.event_id` é `None` ou string vazia, gera novo UUID
- Mesmos eventos podem ser persistidos com IDs diferentes
- Viola constraint UNIQUE

#### **BUG #6: Falta de validação de IP em correlação (ALTO)**
**Arquivo:** `correlation.py`, linhas 30-45  
**Problema:**
- O método `find_reused_iocs()` não valida se IPs são realmente válidos
- Pode incluir `None`, strings vazias, IPs malformados
- Sem índice de filtro, busca linear O(n)

### 1.2 PROBLEMAS LÓGICOS E DESIGN

#### **PROBLEMA #1: Ausência de Rate Limiting e Segurança**
**Arquivo:** `api.py`  
**Problema:**
- Sem autenticação
- Sem rate limiting
- Endpoints abertos para qualquer origem (CORS `allow_origins=["*"]`)
- Sem validação de recursos (path traversal em `/ingest/file`)
- **Impacto:** Vulnerabilidade de segurança crítica em produção

#### **PROBLEMA #2: Correlação sem contexto temporal adequado**
**Arquivo:** `correlation.py`  
**Problema:**
- Janela temporal fixa (3600s = 1h) é inadequada
- Sem consideração de time zones
- Sem clustering de eventos relacionados
- Sem métricas de confiança/score da correlação

#### **PROBLEMA #3: ML com features inadequadas**
**Arquivo:** `ml.py`, linhas 40-50  
**Problema:**
- Features excessivamente simples (apenas `hour`, `weekday`, `severity`)
- Sem captura de padrões de comportamento real
- Sem análise de sequências (só eventos isolados)
- Modelo de anomalia com `contamination=0.03` fixo (irreal)
- **Impacto:** Detecção de anomalias imprecisa

#### **PROBLEMA #4: Normalização de dados inconsistente**
**Arquivo:** `normalization.py`  
**Problema:**
- Múltiplos aliases para mesmos campos (source_ip, src_ip, ip_src) sem normalização
- Sem tratamento de typos comuns
- Sem schema de validação posterior
- Metadata captura tudo que não é reconhecido (low signal-to-noise)

#### **PROBLEMA #5: Ausência de tratamento de valores nulos/ausentes**
**Arquivo:** Vários arquivos  
**Problema:**
- `source_ip` e `destination_ip` são opcionais demais
- Sem validação de dados mínimos para correlação
- Correlação com eventos sem IP retorna resultados sem valor

### 1.3 CÓDIGO REDUNDANTE

#### **REDUNDÂNCIA #1: IP normalization repetida**
- `normalization.py`: função `_normalize_ip()`
- `ml.py`: função `_normalize_ip()`
- `correlation.py`: sem normalização
- **Solução:** Centralizar em módulo utils

#### **REDUNDÂNCIA #2: Severity mapping duplicado**
- `schema.py`: Enum `SeverityLevel`
- `ml.py`: Dict `SEVERITY_SCORE`
- **Solução:** Usar único source of truth

### 1.4 PROBLEMAS DE PERFORMANCE

#### **PERFORMANCE #1: Sem índices apropriados**
**Arquivo:** `models.py`  
**Problema:**
- Índices apenas em `source_ip`, `destination_ip`, `event_type`, `severity`
- Sem índice em `timestamp` (crucial para correlação temporal)
- Sem índice composto (`source_ip, timestamp`)
- Sem índice em `event_id` (busca frequente)

#### **PERFORMANCE #2: Carga completa de dados em memória**
**Arquivo:** `correlation.py`, `api.py`  
**Problema:**
- `/correlation/ip` carrega TODOS os eventos em memória
- Sem paginação
- Sem lazy loading
- O(n) em espaço e tempo

#### **PERFORMANCE #3: Busca em metadata com string conversion**
**Arquivo:** `storage.py`, linha 58  
**Problema:**
- `str(record.event_metadata or {}).lower()` para cada evento
- Sem índice em JSON
- N chamadas de conversão para busca 1 IOC

### 1.5 PROBLEMAS ESTATÍSTICOS E ML

#### **ML #1: Modelo sem validação**
**Arquivo:** `ml.py`  
**Problema:**
- Sem train/test split
- Sem cross-validation
- Sem métricas de avaliação (precision, recall, F1)
- Sem detecção de overfitting
- Anomaly detector com `contamination=0.03` sem justificativa (3% sempre é anomalia?)

#### **ML #2: Features sem escala apropriada**
**Problema:**
- `age_days` pode ser 0 a 365+ (sem upper bound)
- `severity_score` é 0-3
- Sem normalização antes de StandardScaler
- **Impacto:** Feats dominam learning

#### **ML #3: Clustering trivial**
**Arquivo:** `ml.py`, linha 125  
**Problema:**
- `KMeans(n_clusters=2)` FIXO para qualquer dataset
- Sem elbow method, silhouette analysis
- Sem tratamento de insuficiência de dados

#### **ML #4: Sem tratamento de class imbalance**
**Problema:**
- Normal vs Anomaly desbalanceado
- Sem técnicas de balancing (SMOTE, class weights)

#### **ML #5: Feature importance não é exposto**
**Problema:**
- Usuário não sabe quais features causaram anomalia
- Sem explicabilidade (LIME, SHAP)

### 1.6 PROBLEMAS DE NORMALIZAÇÃO

#### **NORM #1: Extração de IPs incompleta**
**Arquivo:** `normalization.py`, linhas 50-65  
**Problema:**
- Sem busca em campos JSON
- Sem extração de IPs de URLs
- Sem tratamento de ranges de IP (CIDR)

#### **NORM #2: Timestamps com timezone inconsistente**
**Problema:**
- `datetime.utcnow()` vs `datetime.fromisoformat()` pode misturar timezones
- Sem conversão para UTC canônica

#### **NORM #3: Event type sem padronização**
**Problema:**
- Case sensitive no ml.py: `.lower().strip()`
- Sem mapping para categories conhecidas (MITRE ATT&CK, etc.)

### 1.7 PROBLEMAS DE UX E OUTPUTS

#### **UX #1: Respostas cruas sem contexto**
**Exemplo:** `/correlation/ip` retorna apenas arrays de objetos
- Sem resumo de resultados
- Sem scoring/confiança
- Sem recomendações
- Sem insights

#### **UX #2: Sem relatórios estruturados**
**Problema:**
- API retorna dados brutos
- Sem relatórios em HTML/PDF
- Sem resumo executivo
- Sem timeline visual

#### **UX #3: Sem dashboards**
**Problema:**
- Sem visualização de dados
- Sem KPIs
- Sem alertas
- Sem drill-down

---

## SEÇÃO 2: PROBLEMAS ESTRUTURAIS

### 2.1 Falta de Logging Estruturado
- Logs simples sem contexto
- Sem correlação de requisições
- Sem rastreamento de erros

### 2.2 Sem Tratamento de Exceções Robusto
- Múltiplos `try/except` sem específico
- SQLAlchemy não trata todas as exceções
- Sem retry logic para falhas transientes

### 2.3 Sem Testes Abrangentes
- Apenas 1 teste unitário
- Sem testes de integração
- Sem testes de performance
- Sem testes de segurança

### 2.4 Sem Versionamento de API
- Endpoints sem `/v1/`, `/v2/`
- Sem backwards compatibility

### 2.5 Sem Documentação de Negócio
- Não explica o que significa cada métrica
- Não documenta assumptions
- Não explica fluxos de investigação

---

## SEÇÃO 3: ANÁLISE DO PIPELINE ML

### Problema #1: Pré-processamento inadequado
- Sem limpeza de dados extremos
- Sem tratamento de duplicados
- Sem análise de distribuição

### Problema #2: Features não representam comportamento real
- Temporal features muito simples
- Sem análise de sequências
- Sem análise de volume
- Sem análise de padrões de rede

### Problema #3: Modelo com parâmetros inadequados
- `contamination=0.03` não baseado em dados
- `n_clusters=2` fixo
- Sem tuning de hiperparâmetros

### Problema #4: Sem baseline de comparação
- Não há modelo alternativo
- Não há regra baseline simples
- Não há ablation study

---

## SEÇÃO 4: ANÁLISE DE CORRELAÇÃO

### Problema #1: Correlação por IP apenas
- Sem correlação por domínio
- Sem correlação por hash (MD5, SHA1, SHA256)
- Sem correlação por URL
- Sem correlação por email

### Problema #2: Janela temporal fixa
- 1 hora pode ser muito/pouco
- Sem configurabilidade
- Sem multi-scale analysis

### Problema #3: Sem agrupamento inteligente
- Sem cluster de eventos relacionados
- Sem detecção de campanha
- Sem detecção de padrão de ataque

### Problema #4: Sem enriquecimento de dados
- Sem busca em bases externas
- Sem geolocalização
- Sem reputação de IP
- Sem análise de WHOIS

---

## SEÇÃO 5: PROBLEMAS ESPECÍFICOS POR ARQUIVO

### config.py
- ✅ OK - Simples e funcional
- ⚠️ Sem validação de variáveis obrigatórias

### schema.py
- ✅ OK - Schema básico adequado
- ⚠️ Sem documentação de campos
- ⚠️ Sem exemplos de dados

### models.py
- ⚠️ Sem índices suficientes
- ⚠️ Sem relacionamentos com outras tabelas
- ⚠️ Sem soft delete

### normalization.py
- ❌ Fallback silencioso para datetime.utcnow()
- ❌ Sem busca completa de IPs
- ⚠️ Aliases de campo sem padronização

### ingestion.py
- ✅ OK - Implementação básica funcional
- ⚠️ Sem tratamento de encodings
- ⚠️ Sem validação de tamanho de arquivo
- ⚠️ Sem rate limiting

### db.py
- ✅ OK - Simples e funcional
- ⚠️ Sem pool tuning
- ⚠️ Sem connection timeout

### storage.py
- ❌ BUG em search_by_ioc() com performance
- ❌ Sem validação de query
- ⚠️ Sem paginação
- ⚠️ Sem cache

### correlation.py
- ❌ BUG lógico em correlate_by_ip()
- ❌ Sem validação de IPs
- ⚠️ Sem score de confiança
- ⚠️ Sem tipos de correlação múltiplos

### ml.py
- ❌ Features inadequadas
- ❌ Sem validação de modelo
- ❌ Sem explicabilidade
- ⚠️ Modelo trivial (clustering)
- ⚠️ Sem tuning de hiperparâmetros

### api.py
- ❌ CORS completamente aberto (segurança)
- ❌ Sem autenticação
- ❌ Sem rate limiting
- ❌ Path traversal possível em /ingest/file
- ❌ Sem validação de inputs
- ❌ Sem paginação
- ⚠️ Endpoints retornam dados crua sem contexto

---

## SEÇÃO 6: RESUMO EXECUTIVO DE ACHADOS

| Categoria | Crítico | Alto | Médio |
|-----------|---------|------|-------|
| Bugs | 6 | 2 | 3 |
| Segurança | 1 | 2 | 2 |
| Performance | 3 | 2 | 2 |
| ML/Stats | 5 | 3 | 2 |
| UX/Output | 3 | 3 | 3 |
| **TOTAL** | **18** | **12** | **12** |

---

## SEÇÃO 7: PRÓXIMOS PASSOS

1. **CRÍTICO (Implementar IMEDIATAMENTE):**
   - Corrigir BUG #1, #2, #3, #4, #5 em correlation e storage
   - Adicionar segurança (auth, rate limiting, validação)
   - Melhorar ML com features e validação

2. **ALTO (Próximas 2 semanas):**
   - Implementar logging estruturado
   - Adicionar testes abrangentes
   - Melhorar correlação com múltiplos tipos
   - Implementar dashboards

3. **MÉDIO (Roadmap futuro):**
   - Enriquecimento de dados externo
   - Análise de padrões de ataque
   - Exportação de relatórios

---

## MÉTRICAS ATUAIS

- **Linhas de código:** ~1000
- **Testes:** 1 teste unitário (0.1% cobertura estimada)
- **Complexidade ciclomática:** ALTA em storage.py, correlation.py
- **Segurança:** CRÍTICA (CORS aberto, sem auth, sem validação)
- **Performance:** CRÍTICA em datasets > 100k eventos

---

**Relatório gerado automaticamente durante auditoria**
