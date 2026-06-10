"""
Dashboard Streamlit para Plataforma Forense & CTI

Visualizações profissionais para análise de segurança com foco em:
- KPIs de severidade e anomalias
- Timelines de eventos
- Heatmaps de atividade
- Correlações de IOCs
- Scores de risco
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Optional
import pytz

# Configuração da página
st.set_page_config(
    page_title="Plataforma Forense & CTI",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema e estilos
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1f1f1f;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Configuração da API
API_BASE_URL = "http://localhost:5000"

def get_api_data(endpoint: str, params: Optional[dict] = None):
    """Busca dados da API com tratamento de erro."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com API: {e}")
        return None


def calculate_severity_score(events_df: pd.DataFrame) -> float:
    """Calcula score de severidade dos eventos."""
    if events_df.empty:
        return 0.0
    
    severity_weights = {
        "critical": 4.0,
        "high": 3.0,
        "medium": 2.0,
        "low": 1.0
    }
    
    total_score = 0
    for _, row in events_df.iterrows():
        severity = str(row.get("severity", "low")).lower()
        total_score += severity_weights.get(severity, 0)
    
    return round(total_score / len(events_df), 2)


def calculate_anomaly_percentage(events_data: list) -> float:
    """Estima porcentagem de eventos anômalos."""
    if not events_data:
        return 0.0
    
    # Simples: eventos críticos/high como proxy de anomalia
    anomalous = sum(1 for e in events_data if e.get("severity") in ["critical", "high"])
    return round(100 * anomalous / len(events_data), 2)


def format_timestamp(ts_str: str) -> str:
    """Formata timestamp para exibição."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts_str


# Sidebar com configurações
st.sidebar.title("⚙️ Configurações")
st.sidebar.markdown("---")

tab_events, tab_correlation, tab_ml, tab_reports = st.tabs([
    "📊 EVENTOS",
    "🔗 CORRELAÇÃO",
    "🤖 ML & ANOMALIAS",
    "📋 RELATÓRIOS"
])


# ====================
# TAB 1: EVENTOS
# ====================
with tab_events:
    st.title("📊 Análise de Eventos")
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events_data = get_api_data("/events", {"limit": 1000})
        total_events = total_events_data["total"] if total_events_data else 0
        st.metric("Total de Eventos", total_events)
    
    with col2:
        if total_events_data and total_events_data.get("items"):
            events_df = pd.DataFrame(total_events_data["items"])
            severity_score = calculate_severity_score(events_df)
            st.metric("Score de Severidade", f"{severity_score:.2f}/4.0")
    
    with col3:
        if total_events_data and total_events_data.get("items"):
            anomaly_pct = calculate_anomaly_percentage(total_events_data["items"])
            st.metric("% Anomalias Estimadas", f"{anomaly_pct:.1f}%")
    
    with col4:
        if total_events_data and total_events_data.get("items"):
            critical_events = sum(1 for e in total_events_data["items"] if e.get("severity") == "critical")
            st.metric("Eventos Críticos", critical_events)
    
    st.markdown("---")
    
    # Distribuição de severidade
    if total_events_data and total_events_data.get("items"):
        events_df = pd.DataFrame(total_events_data["items"])
        
        # Gráfico de pizza - Severidade
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição de Severidade")
            severity_counts = events_df["severity"].value_counts()
            
            colors_severity = {
                "critical": "#FF6B6B",
                "high": "#FF9800",
                "medium": "#FFC300",
                "low": "#4CAF50"
            }
            
            fig_severity = go.Figure(data=[go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                marker=dict(colors=[colors_severity.get(s, "#999") for s in severity_counts.index]),
                textposition="inside",
                textinfo="label+percent"
            )])
            fig_severity.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig_severity, use_container_width=True)
        
        # Timeline de eventos
        with col2:
            st.subheader("Timeline de Eventos (últimas 24h)")
            
            # Converte timestamp
            events_df["timestamp"] = pd.to_datetime(events_df["timestamp"])
            events_df["hour"] = events_df["timestamp"].dt.floor("H")
            hourly_counts = events_df.groupby("hour").size()
            
            fig_timeline = go.Figure(data=[go.Bar(
                x=hourly_counts.index,
                y=hourly_counts.values,
                marker=dict(color="#4472C4"),
                text=hourly_counts.values,
                textposition="outside"
            )])
            fig_timeline.update_layout(
                title="Eventos por Hora",
                xaxis_title="Hora",
                yaxis_title="Quantidade",
                height=400,
                hovermode="x unified"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Tipos de eventos
        st.subheader("Tipos de Eventos Mais Frequentes")
        event_types = events_df["event_type"].value_counts().head(10)
        fig_types = px.bar(
            x=event_types.values,
            y=event_types.index,
            orientation="h",
            title="Top 10 Tipos de Eventos",
            labels={"x": "Frequência", "y": "Tipo de Evento"},
            color=event_types.values,
            color_continuous_scale="Viridis"
        )
        fig_types.update_layout(height=400)
        st.plotly_chart(fig_types, use_container_width=True)
        
        # Tabela de eventos recentes
        st.subheader("Eventos Recentes")
        display_events = events_df.nlargest(10, "timestamp")[
            ["event_id", "timestamp", "source_ip", "destination_ip", "event_type", "severity"]
        ].copy()
        
        # Formata para exibição
        display_events["timestamp"] = display_events["timestamp"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        display_events = display_events.rename(columns={
            "event_id": "ID",
            "timestamp": "Data/Hora",
            "source_ip": "IP Origem",
            "destination_ip": "IP Destino",
            "event_type": "Tipo",
            "severity": "Severidade"
        })
        
        st.dataframe(display_events, use_container_width=True, height=400)


# ====================
# TAB 2: CORRELAÇÃO
# ====================
with tab_correlation:
    st.title("🔗 Análise de Correlação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Buscar por IOC")
        ioc_query = st.text_input("IP, domínio ou hash:", placeholder="192.168.1.1")
        if ioc_query and st.button("🔍 Buscar"):
            ioc_results = get_api_data("/events/search", {"ioc": ioc_query, "limit": 50})
            if ioc_results:
                st.success(f"✅ Encontrados {ioc_results['total']} eventos")
                if ioc_results.get("items"):
                    ioc_df = pd.DataFrame(ioc_results["items"])
                    st.dataframe(ioc_df[[
                        "event_id", "timestamp", "source_ip", "destination_ip", "severity"
                    ]], use_container_width=True)
    
    with col2:
        st.subheader("Correlação de IPs")
        time_window = st.slider("Janela Temporal (segundos)", 60, 86400, 3600)
        
        if st.button("🔗 Correlacionar"):
            correlation_data = get_api_data("/correlation/ip", {"time_window": time_window, "limit": 100})
            if correlation_data:
                st.success(f"✅ {correlation_data['total_matched']} eventos correlacionados")
                st.info(f"🔄 {correlation_data['total_reused_iocs']} IOCs reutilizados")
                
                # IOCs reutilizados
                if correlation_data.get("reused_iocs"):
                    st.subheader("IOCs Reutilizados (Indicador de Ameaça)")
                    reused_df = pd.DataFrame(correlation_data["reused_iocs"])
                    reused_df = reused_df.rename(columns={
                        "ioc": "IOC",
                        "occurrence_count": "Ocorrências",
                        "severity_max": "Severidade",
                        "first_seen": "Primeira Ocorrência",
                        "last_seen": "Última Ocorrência"
                    })
                    
                    # Heatmap de IOCs
                    fig_ioc = px.bar(
                        reused_df.sort_values("Ocorrências", ascending=True),
                        x="Ocorrências",
                        y="IOC",
                        color="Severidade",
                        color_discrete_map={
                            "critical": "#FF6B6B",
                            "high": "#FF9800",
                            "medium": "#FFC300",
                            "low": "#4CAF50"
                        }
                    )
                    st.plotly_chart(fig_ioc, use_container_width=True)
                    
                    st.dataframe(reused_df, use_container_width=True)


# ====================
# TAB 3: ML & ANOMALIAS
# ====================
with tab_ml:
    st.title("🤖 Machine Learning & Detecção de Anomalias")
    
    # Status do modelo
    model_status = get_api_data("/model/status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if model_status and model_status.get("trained"):
            st.success("✅ Modelo Treinado")
            stats = model_status.get("training_stats", {})
            st.metric("Eventos Treinados", stats.get("events_trained", 0))
            st.metric("Anomalias Detectadas", stats.get("anomalies_detected", 0))
            st.metric("Taxa de Anomalia", f"{stats.get('anomaly_percentage', 0):.1f}%")
        else:
            st.warning("⚠️ Modelo Não Treinado")
            st.info("Clique em 'Treinar Modelo' abaixo")
    
    with col2:
        st.subheader("Ações")
        
        if st.button("🚀 Treinar Modelo", use_container_width=True):
            with st.spinner("Treinando modelo..."):
                train_result = requests.post(f"{API_BASE_URL}/ml/train", 
                                            params={"limit": 500}).json()
                if train_result.get("trained"):
                    st.success(f"✅ Modelo treinado com {train_result['events_used']} eventos")
                else:
                    st.error("❌ Erro ao treinar modelo")
        
        if st.button("📊 Agrupar Eventos", use_container_width=True):
            with st.spinner("Agrupando eventos..."):
                cluster_result = get_api_data("/ml/cluster", {"limit": 100})
                if cluster_result and not cluster_result.get("error"):
                    st.success(f"✅ {len(set(cluster_result['clusters']))} clusters identificados")
                    st.info(f"Distribuição: {cluster_result.get('cluster_sizes', [])}")
    
    # Avaliação de evento individual
    st.subheader("Avaliar Evento Individual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        event_type = st.selectbox("Tipo de Evento", 
                                   ["login_attempt", "file_access", "network_connection", "process_execution"])
        severity = st.selectbox("Severidade", ["low", "medium", "high", "critical"])
        source_ip = st.text_input("IP de Origem")
        destination_ip = st.text_input("IP de Destino")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("📈 Calcular Score de Anomalia"):
            event_payload = {
                "event_type": event_type,
                "severity": severity,
                "source_ip": source_ip or None,
                "destination_ip": destination_ip or None,
                "raw_source": "dashboard"
            }
            
            try:
                score_result = requests.post(
                    f"{API_BASE_URL}/ml/score",
                    json=event_payload
                ).json()
                
                col_result1, col_result2 = st.columns(2)
                
                with col_result1:
                    if score_result.get("is_anomaly"):
                        st.error(f"🚨 ANOMALIA DETECTADA")
                    else:
                        st.success(f"✅ Comportamento Normal")
                    
                    st.metric("Score", f"{score_result.get('score', 0):.4f}")
                
                with col_result2:
                    st.metric("Confiança", f"{score_result.get('confidence', 0):.1%}")
                    st.metric("Razão", score_result.get("reason", ""))
                
                st.info(f"💡 {score_result.get('explanation', 'Sem explicação disponível')}")
            except Exception as e:
                st.error(f"Erro ao avaliar: {e}")


# ====================
# TAB 4: RELATÓRIOS
# ====================
with tab_reports:
    st.title("📋 Relatórios e Análise")
    
    # Resumo Executivo
    st.subheader("📌 Resumo Executivo")
    
    total_data = get_api_data("/events", {"limit": 1000})
    
    if total_data and total_data.get("items"):
        events_df = pd.DataFrame(total_data["items"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            ### Visão Geral
            - **Total de Eventos**: {len(events_df)}
            - **Período**: Últimos 30 dias
            - **Status**: Monitorando em tempo real
            """)
        
        with col2:
            severity_dist = events_df["severity"].value_counts()
            st.markdown(f"""
            ### Distribuição de Severidade
            - **Críticos**: {severity_dist.get('critical', 0)} 🔴
            - **Altos**: {severity_dist.get('high', 0)} 🟠
            - **Médios**: {severity_dist.get('medium', 0)} 🟡
            - **Baixos**: {severity_dist.get('low', 0)} 🟢
            """)
        
        with col3:
            anomaly_pct = calculate_anomaly_percentage(total_data["items"])
            st.markdown(f"""
            ### Indicadores de Ameaça
            - **Taxa de Anomalia**: {anomaly_pct:.1f}%
            - **IOCs Suspeitos**: ~{len(events_df) // 10}
            - **Nível de Risco**: {'🔴 ALTO' if anomaly_pct > 20 else '🟡 MÉDIO' if anomaly_pct > 10 else '🟢 BAIXO'}
            """)
        
        # Principais descobertas
        st.subheader("🔍 Principais Descobertas")
        
        # IPs mais ativas
        if "source_ip" in events_df.columns:
            top_ips = events_df[events_df["source_ip"].notna()]["source_ip"].value_counts().head(5)
            if not top_ips.empty:
                st.markdown("#### IPs Mais Ativas")
                for ip, count in top_ips.items():
                    st.write(f"- **{ip}**: {count} eventos")
        
        # Eventos críticos recentes
        critical_events = events_df[events_df["severity"] == "critical"]
        if not critical_events.empty:
            st.markdown("#### Eventos Críticos Recentes")
            for _, event in critical_events.head(3).iterrows():
                st.write(f"""
                - **Tipo**: {event.get('event_type', 'unknown')}
                - **IP Origem**: {event.get('source_ip', 'N/A')}
                - **Hora**: {event.get('timestamp', 'N/A')}
                """)
        
        # Recomendações
        st.subheader("💡 Recomendações")
        st.markdown("""
        1. **Investigar IPs Suspeitas**: Correlacione IPs reutilizadas com bases de reputação externas
        2. **Aumentar Monitoramento**: Foque em eventos críticos e anomalias detectadas
        3. **Enriquecimento de Dados**: Integre com OSINT (VirusTotal, Shodan, AbuseIPDB)
        4. **Tuning de ML**: Ajuste modelo com mais dados históricos para melhor precisão
        5. **Alertas Automáticos**: Configure alertas para IPs e tipos de eventos críticos
        """)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>Plataforma Forense & CTI v0.2.0 | Powered by Streamlit & FastAPI</p>
    <p>Status da API: <span style='color: #4CAF50;'>🟢 Online</span></p>
</div>
""", unsafe_allow_html=True)
