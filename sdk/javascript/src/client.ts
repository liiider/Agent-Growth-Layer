import { GuidanceResource } from './guidance'

export type ExperienceCreateRequest = {
  agent_id: string
  domain: string
  intent: string
  user_input: string
  agent_output: string
  tools_used?: string[]
  retrieved_context?: string[]
  feedback?: string
  result_status?: string
  risk_level?: 'low' | 'medium' | 'high'
  metadata?: Record<string, unknown>
}

export class ExperiencesResource {
  constructor(private readonly baseUrl: string) {}

  async create(request: ExperienceCreateRequest): Promise<Record<string, unknown>> {
    const response = await fetch(`${this.baseUrl}/v1/experiences`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        tools_used: [],
        retrieved_context: [],
        result_status: 'unknown',
        risk_level: 'low',
        metadata: {},
        ...request,
      }),
    })

    if (!response.ok) {
      throw new Error(`Experience create failed: ${response.status}`)
    }

    return response.json()
  }
}

export class AgentGrowthClient {
  readonly guidance: GuidanceResource
  readonly experiences: ExperiencesResource

  constructor(baseUrl = 'http://localhost:8000') {
    const normalizedBaseUrl = baseUrl.replace(/\/$/, '')
    this.guidance = new GuidanceResource(normalizedBaseUrl)
    this.experiences = new ExperiencesResource(normalizedBaseUrl)
  }
}
