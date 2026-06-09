// Event types
export interface EventRecord {
  id: string
  event_id: string
  timestamp: string
  source_ip: string
  destination_ip: string
  event_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  raw_source: string
  metadata?: Record<string, any>
}

export interface NormalizedEvent {
  event_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  source_ip: string
  destination_ip: string
  timestamp: string
  raw_source: string
  metadata?: Record<string, any>
}

// Correlation types
export interface CorrelationMatch {
  anchor_event_id: string
  related_event_count: number
  severity_levels: string[]
  first_event_timestamp: string
  last_event_timestamp: string
}

export interface ReusedIOC {
  ioc: string
  occurrence_count: number
  severity_max: string
  event_types: string[]
  first_seen: string
  last_seen: string
}

export interface CorrelationResponse {
  total_matched: number
  total_reused_iocs: number
  correlation_matches: CorrelationMatch[]
  reused_iocs: ReusedIOC[]
  analysis_timestamp: string
}

// ML types
export interface AnomalyScore {
  score: number
  is_anomaly: boolean
  confidence: number
  explanation: string
}

export interface AnomalyDetail {
  event_id: string
  score: number
  is_anomaly: boolean
  severity: string
  confidence: number
  reason: string
  explanation: string
}

export interface TrainingStats {
  events_trained: number
  anomalies_detected: number
  anomaly_percentage: number
  anomaly_score_min: number
  anomaly_score_max: number
  anomaly_score_mean: number
  clusters: number
}

export interface ModelStatus {
  model_loaded: boolean
  model_trained: boolean
  stats?: TrainingStats
  last_training?: string
}

export interface ClusterResult {
  cluster_id: number
  events_count: number
  severity_levels: string[]
  event_types: string[]
}

// Query types
export interface QueryResponse {
  total: number
  page: number
  limit: number
  items: EventRecord[]
}

export interface UploadResponse {
  ingested: number
}

// API types
export interface ApiError {
  detail: string
}

export interface PaginationParams {
  limit?: number
  offset?: number
}

export interface FilterParams extends PaginationParams {
  start_date?: string
  end_date?: string
  severity?: string
  event_type?: string
}
