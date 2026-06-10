"""
Sistema de Geração de Relatórios para Plataforma Forense & CTI

Exporta análises em formatos profissionais (HTML, PDF)
com foco em descobertas, IoCs e recomendações investigativas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
from pathlib import Path


class ReportGenerator:
    """Gera relatórios profissionais em HTML/PDF."""
    
    def __init__(self, title: str = "Relatório de Análise Forense & CTI"):
        self.title = title
        self.timestamp = datetime.utcnow()
        self.findings = []
        self.iocs = []
        self.recommendations = []
    
    def add_finding(
        self,
        title: str,
        description: str,
        severity: str = "medium",
        events_count: int = 0,
        timeline: Optional[str] = None
    ):
        """Adiciona uma descoberta principal ao relatório."""
        self.findings.append({
            "title": title,
            "description": description,
            "severity": severity,
            "events_count": events_count,
            "timeline": timeline,
        })
    
    def add_ioc(
        self,
        ioc_value: str,
        ioc_type: str,
        threat_level: str,
        source: str,
        context: str = "",
        recommendations: Optional[List[str]] = None
    ):
        """Adiciona um IOC (Indicator of Compromise) ao relatório."""
        self.iocs.append({
            "value": ioc_value,
            "type": ioc_type,  # ip, domain, hash, email, url
            "threat_level": threat_level,
            "source": source,
            "context": context,
            "recommendations": recommendations or [],
        })
    
    def add_recommendation(self, recommendation: str, priority: str = "medium"):
        """Adiciona uma recomendação ao relatório."""
        self.recommendations.append({
            "text": recommendation,
            "priority": priority,
        })
    
    def _get_severity_color(self, severity: str) -> str:
        """Retorna cor para severidade."""
        colors = {
            "critical": "#FF6B6B",
            "high": "#FF9800",
            "medium": "#FFC300",
            "low": "#4CAF50",
        }
        return colors.get(severity.lower(), "#999")
    
    def generate_html(self) -> str:
        """Gera relatório em HTML."""
        
        findings_html = ""
        for i, finding in enumerate(self.findings, 1):
            severity_color = self._get_severity_color(finding["severity"])
            findings_html += f"""
            <div style="background-color: #f9f9f9; border-left: 4px solid {severity_color}; 
                        padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: {severity_color};">
                    🔍 Descoberta #{i}: {finding['title']}
                </h4>
                <p style="margin: 5px 0;"><strong>Descrição:</strong> {finding['description']}</p>
                <p style="margin: 5px 0;"><strong>Eventos Relacionados:</strong> {finding['events_count']}</p>
                {f"<p style='margin: 5px 0;'><strong>Timeline:</strong> {finding['timeline']}</p>" if finding.get('timeline') else ""}
                <p style="margin: 5px 0;"><strong>Severidade:</strong> 
                    <span style="background-color: {severity_color}; color: white; 
                                 padding: 3px 8px; border-radius: 3px; font-size: 12px;">
                        {finding['severity'].upper()}
                    </span>
                </p>
            </div>
            """
        
        iocs_html = ""
        for ioc in self.iocs:
            threat_color = self._get_severity_color(ioc["threat_level"])
            iocs_html += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-family: monospace; font-size: 12px;">{ioc['value']}</td>
                <td style="padding: 10px;">{ioc['type'].upper()}</td>
                <td style="padding: 10px;"><span style="background-color: {threat_color}; 
                                                        color: white; padding: 3px 8px; 
                                                        border-radius: 3px; font-size: 12px;">
                                            {ioc['threat_level'].upper()}</span></td>
                <td style="padding: 10px;">{ioc['source']}</td>
                <td style="padding: 10px; font-size: 12px;">{ioc['context']}</td>
            </tr>
            """
        
        recommendations_html = ""
        priority_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        priority_colors = {"critical": "#FF6B6B", "high": "#FF9800", "medium": "#FFC300", "low": "#4CAF50"}
        
        for rec in self.recommendations:
            icon = priority_icons.get(rec["priority"], "•")
            color = priority_colors.get(rec["priority"], "#999")
            recommendations_html += f"""
            <div style="background-color: #f5f5f5; padding: 10px; margin: 8px 0; border-left: 4px solid {color}; border-radius: 3px;">
                <strong>{icon} [{rec['priority'].upper()}]</strong> {rec['text']}
            </div>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #333;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header {{
            border-bottom: 3px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #0066cc;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        h2 {{
            color: #0066cc;
            font-size: 24px;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        h3 {{
            color: #333;
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .executive-summary {{
            background-color: #e3f2fd;
            border-left: 4px solid #0066cc;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .metadata-item {{
            border-left: 3px solid #0066cc;
            padding-left: 10px;
        }}
        .metadata-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: bold;
        }}
        .metadata-value {{
            font-size: 16px;
            color: #333;
            font-weight: bold;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        table th {{
            background-color: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        .risk-level {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
        .risk-critical {{ background-color: #FF6B6B; }}
        .risk-high {{ background-color: #FF9800; }}
        .risk-medium {{ background-color: #FFC300; color: #333; }}
        .risk-low {{ background-color: #4CAF50; }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .page-break {{
            page-break-after: always;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔒 {self.title}</h1>
            <p style="color: #666; margin-top: 10px;">Relatório de Análise de Segurança</p>
        </header>

        <h2>📌 Resumo Executivo</h2>
        <div class="executive-summary">
            <p>Este relatório apresenta as principais descobertas da análise forense e CTI realizada 
               na infraestrutura de segurança. São destacadas anomalias detectadas, IOCs comprometidos 
               e recomendações investigativas prioritárias.</p>
        </div>

        <div class="metadata">
            <div class="metadata-item">
                <div class="metadata-label">📅 Data do Relatório</div>
                <div class="metadata-value">{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">📊 Total de Descobertas</div>
                <div class="metadata-value">{len(self.findings)}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">🎯 IOCs Identificados</div>
                <div class="metadata-value">{len(self.iocs)}</div>
            </div>
        </div>

        <h2>🔍 Principais Descobertas</h2>
        {findings_html if findings_html else "<p style='color: #999;'>Nenhuma descoberta registrada.</p>"}

        <h2>🎯 Indicadores de Compromisso (IOCs)</h2>
        {f"""
        <table>
            <thead>
                <tr>
                    <th>IOC</th>
                    <th>Tipo</th>
                    <th>Nível de Ameaça</th>
                    <th>Fonte</th>
                    <th>Contexto</th>
                </tr>
            </thead>
            <tbody>
                {iocs_html if iocs_html else "<tr><td colspan='5' style='text-align: center; padding: 20px; color: #999;'>Nenhum IOC registrado.</td></tr>"}
            </tbody>
        </table>
        """ if iocs_html else "<p style='color: #999;'>Nenhum IOC registrado.</p>"}

        <h2>💡 Recomendações Investigativas</h2>
        {recommendations_html if recommendations_html else "<p style='color: #999;'>Nenhuma recomendação registrada.</p>"}

        <h2>📋 Próximos Passos</h2>
        <ol>
            <li><strong>Investigação Imediata</strong>: Priorize eventos críticos e IOCs com ameaça alta</li>
            <li><strong>Enriquecimento de Dados</strong>: Correlacione com bases de reputação externas</li>
            <li><strong>Resposta a Incidentes</strong>: Isole sistemas afetados se necessário</li>
            <li><strong>Análise Forense</strong>: Preserve logs e artefatos para investigação detalhada</li>
            <li><strong>Monitoramento Contínuo</strong>: Configure alertas para padrões similares</li>
        </ol>

        <footer>
            <p>Este relatório é confidencial e destinado apenas a pessoal autorizado.</p>
            <p>Plataforma Forense & CTI v0.2.0</p>
        </footer>
    </div>
</body>
</html>
"""
        return html_content
    
    def save_html(self, output_path: str = "report.html") -> str:
        """Salva relatório em HTML."""
        html = self.generate_html()
        path = Path(output_path)
        path.write_text(html, encoding="utf-8")
        return str(path.absolute())
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporta relatório como dicionário."""
        return {
            "title": self.title,
            "timestamp": self.timestamp.isoformat(),
            "findings": self.findings,
            "iocs": self.iocs,
            "recommendations": self.recommendations,
        }


class AnalysisReport:
    """Classe utilitária para gerar relatórios baseados em dados de análise."""
    
    @staticmethod
    def from_correlation_analysis(
        correlation_data: Dict[str, Any],
        time_window_hours: int = 24
    ) -> ReportGenerator:
        """Gera relatório baseado em análise de correlação."""
        report = ReportGenerator(
            f"Relatório de Correlação de IOCs - {time_window_hours}h"
        )
        
        if correlation_data.get("total_reused_iocs", 0) > 0:
            report.add_finding(
                title="IOCs Reutilizados Detectados",
                description=f"Foram identificados {correlation_data['total_reused_iocs']} IOCs "
                           f"reutilizados em múltiplos eventos, indicando possível atividade maliciosa.",
                severity="high",
                events_count=correlation_data.get("total_matched", 0),
            )
        
        # Adiciona IOCs
        for ioc_info in correlation_data.get("reused_iocs", [])[:10]:
            report.add_ioc(
                ioc_value=ioc_info["ioc"],
                ioc_type="ip",
                threat_level=ioc_info.get("severity_max", "medium"),
                source="Correlação de Eventos",
                context=f"{ioc_info['occurrence_count']} ocorrências",
                recommendations=["Bloquear na firewall", "Investigar padrão de conexão"]
            )
        
        report.add_recommendation(
            "Correlacione IPs suspeitas com bases de reputação (VirusTotal, Shodan, AbuseIPDB)",
            priority="high"
        )
        report.add_recommendation(
            "Implemente alertas automáticos para reutilização de IOCs",
            priority="high"
        )
        
        return report
    
    @staticmethod
    def from_ml_analysis(
        ml_results: Dict[str, Any],
        anomaly_threshold: float = 0.7
    ) -> ReportGenerator:
        """Gera relatório baseado em análise de ML."""
        report = ReportGenerator("Relatório de Anomalias Detectadas")
        
        if ml_results.get("is_anomaly"):
            report.add_finding(
                title="Anomalia Detectada pelo Modelo ML",
                description=f"Score de anomalia: {ml_results.get('score', 0):.4f}. "
                           f"Evento diverge significativamente do comportamento normal.",
                severity=ml_results.get("severity", "medium"),
                events_count=1,
            )
            
            report.add_recommendation(
                f"Investigar: {ml_results.get('explanation', 'Padrão anômalo detectado')}",
                priority="high"
            )
        
        return report


if __name__ == "__main__":
    # Exemplo de uso
    report = ReportGenerator("Relatório de Análise Forense - Teste")
    
    report.add_finding(
        title="Atividade de Reconhecimento Detectada",
        description="Múltiplas tentativas de conexão para puertos diversos detectadas de IP 192.168.1.100",
        severity="high",
        events_count=45,
        timeline="2026-06-07 14:30 UTC - 2026-06-07 15:45 UTC"
    )
    
    report.add_ioc(
        ioc_value="192.168.1.100",
        ioc_type="ip",
        threat_level="high",
        source="Detecção de Anomalia",
        context="Source IP em múltiplas tentativas de login",
        recommendations=["Bloquear IP", "Verificar logs de acesso", "Investigar conta"]
    )
    
    report.add_recommendation(
        "Isole o host 192.168.1.100 para análise forense",
        priority="critical"
    )
    
    # Salva relatório
    html_path = report.save_html("/tmp/forensic_report_test.html")
    print(f"✅ Relatório salvo em: {html_path}")
