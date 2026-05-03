export type GuidanceRequest = {
  agent_id: string
  domain: string
  intent: string
  context?: Record<string, unknown>
  risk_level?: 'low' | 'medium' | 'high'
}

export class Guidance {
  constructor(readonly guidance: Record<string, any>) {}

  toPrompt(): string {
    const seedSkills = this.guidance.seed_skills ?? []
    const candidateSkills = this.guidance.candidate_skills ?? []
    const verifiedSkills = this.guidance.verified_skills ?? []

    return [
      'Runtime Guidance',
      renderSection('Verified Skills', verifiedSkills),
      renderSection('Candidate Skills', candidateSkills),
      renderSection('Seed Skills', seedSkills),
    ].join('\n\n')
  }
}

export class GuidanceResource {
  constructor(private readonly baseUrl: string) {}

  async get(request: GuidanceRequest): Promise<Guidance> {
    const response = await fetch(`${this.baseUrl}/v1/guidance`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        context: {},
        risk_level: 'low',
        ...request,
      }),
    })

    if (!response.ok) {
      throw new Error(`Guidance request failed: ${response.status}`)
    }

    const body = await response.json()
    return new Guidance(body.guidance)
  }
}

function renderSection(title: string, skills: Array<Record<string, any>>): string {
  if (!skills.length) {
    return `${title}:\nNone.`
  }

  const rendered = skills.map((skill, index) => {
    const instructions = skill.instructions ?? []
    return [
      `${index + 1}. ${skill.name ?? skill.id ?? 'Unnamed Skill'}`,
      ...instructions.map((instruction: string) => `- ${instruction}`),
    ].join('\n')
  })

  return `${title}:\n${rendered.join('\n\n')}`
}
