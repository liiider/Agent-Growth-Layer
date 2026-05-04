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

export type SkillBuildRequest = {
  agent_id: string
  domain: string
  intent: string
  name: string
  cognition_ids: string[]
}

export type ExamRequest = {
  evaluator?: 'manual_score' | 'llm_judge'
  score?: number
  cases?: Array<Record<string, unknown>>
  require_human_review?: boolean
}

export class SkillsResource {
  constructor(private readonly baseUrl: string) {}

  async build(request: SkillBuildRequest): Promise<Record<string, unknown>> {
    const response = await fetch(`${this.baseUrl}/v1/skills/build`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Skill build failed: ${response.status}`)
    }

    return response.json()
  }

  async get(skillId: string): Promise<Record<string, unknown>> {
    const response = await fetch(`${this.baseUrl}/v1/skills/${skillId}`)
    if (!response.ok) {
      throw new Error(`Skill get failed: ${response.status}`)
    }
    return response.json()
  }

  async runExam(skillId: string, request: ExamRequest): Promise<Record<string, unknown>> {
    const response = await fetch(`${this.baseUrl}/v1/skills/${skillId}/exam`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        evaluator: 'manual_score',
        cases: [],
        ...request,
      }),
    })

    if (!response.ok) {
      throw new Error(`Skill exam failed: ${response.status}`)
    }

    return response.json()
  }
}

export type ReviewCreateRequest = {
  object_type: 'experience' | 'cognition' | 'skill'
  object_id: string
  decision: 'approve' | 'reject' | 'revise' | 'quarantine'
  reviewer: string
  notes?: string
  metadata?: Record<string, unknown>
}

export class ReviewsResource {
  constructor(private readonly baseUrl: string) {}

  async create(request: ReviewCreateRequest): Promise<Record<string, unknown>> {
    const response = await fetch(`${this.baseUrl}/v1/reviews`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        notes: '',
        metadata: {},
        ...request,
      }),
    })

    if (!response.ok) {
      throw new Error(`Review create failed: ${response.status}`)
    }

    return response.json()
  }
}

export class AgentGrowthClient {
  readonly guidance: GuidanceResource
  readonly experiences: ExperiencesResource
  readonly skills: SkillsResource
  readonly reviews: ReviewsResource

  constructor(baseUrl = 'http://localhost:8000') {
    const normalizedBaseUrl = baseUrl.replace(/\/$/, '')
    this.guidance = new GuidanceResource(normalizedBaseUrl)
    this.experiences = new ExperiencesResource(normalizedBaseUrl)
    this.skills = new SkillsResource(normalizedBaseUrl)
    this.reviews = new ReviewsResource(normalizedBaseUrl)
  }
}
