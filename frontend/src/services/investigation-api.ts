import { API_BASE_URL } from "@/services/api-client"

export type DatasetUploadResponse = {
  dataset_id: string
  filename: string
  rows: number
  columns: number
}

export type SemanticColumnResponse = {
  name: string
  data_type: string
  primitive: string
  missing_values: number
  unique_values: number
}

export type SemanticProfileResponse = {
  dataset_id: string
  dataset_name: string
  rows: number
  columns: number
  measures: number
  dimensions: number
  health_score: number
  warnings: string[]
  columns_profile: SemanticColumnResponse[]
}

export type BusinessGoalResponse = {
  goal_id: string
  name: string
  description: string
  business_purpose: string
  tags: string[]
}

export type StartInvestigationResponse = {
  investigation_id: string
  status: string
  progress: number
  current_step: string
}

export type InvestigationStatusResponse = {
  investigation_id: string
  status: string
  progress: number
  current_step: string
  warnings: string[]
}

export type FindingEvidenceResponse = {
  capability_name: string
  evidence_type: string
  confidence: number
  trace_reference: string
  evidence_value: string
}

export type FindingResponse = {
  id: string
  title: string
  description: string
  category: string
  severity: string
  confidence: number
  business_impact: string
  supporting_analyses: string[]
  supporting_evidence: FindingEvidenceResponse[]
}

export type FindingCollectionResponse = {
  investigation_id: string
  findings: FindingResponse[]
  summary: Record<string, unknown>
  statistics: Record<string, unknown>
  warnings: string[]
  execution_metadata: Record<string, unknown>
}

export type InvestigationFindingsResponse = {
  investigation_id: string
  status: string
  confidence: number
  findings_collection: FindingCollectionResponse
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = "Request failed"
    try {
      const payload = await response.json()
      detail = payload?.detail ?? detail
    } catch {
      // Keep default message when parsing fails.
    }
    throw new Error(detail)
  }

  return response.json() as Promise<T>
}

export async function uploadDataset(file: File): Promise<DatasetUploadResponse> {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${API_BASE_URL}/investigation-pipeline/datasets/upload`, {
    method: "POST",
    body: formData,
  })

  return parseJson<DatasetUploadResponse>(response)
}

export async function generateSemanticProfile(datasetId: string): Promise<SemanticProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/investigation-pipeline/datasets/${datasetId}/semantic-profile`, {
    method: "POST",
  })

  return parseJson<SemanticProfileResponse>(response)
}

export async function getBusinessGoals(): Promise<BusinessGoalResponse[]> {
  const response = await fetch(`${API_BASE_URL}/investigation-pipeline/business-goals`, {
    method: "GET",
  })

  return parseJson<BusinessGoalResponse[]>(response)
}

export async function startInvestigation(datasetId: string, goalId: string): Promise<StartInvestigationResponse> {
  const response = await fetch(`${API_BASE_URL}/investigation-pipeline/investigations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      dataset_id: datasetId,
      goal_id: goalId,
    }),
  })

  return parseJson<StartInvestigationResponse>(response)
}

export async function getInvestigationStatus(investigationId: string): Promise<InvestigationStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/investigation-pipeline/investigations/${investigationId}/status`, {
    method: "GET",
  })

  return parseJson<InvestigationStatusResponse>(response)
}

export async function getInvestigationFindings(investigationId: string): Promise<InvestigationFindingsResponse> {
  const response = await fetch(`${API_BASE_URL}/investigation-pipeline/investigations/${investigationId}/findings`, {
    method: "GET",
  })

  return parseJson<InvestigationFindingsResponse>(response)
}