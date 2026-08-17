export interface User {
  id: string
  organization_id: string
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'recruiter' | 'viewer'
  avatar_url: string | null
  email_verified: boolean
  created_at: string
}

export interface Job {
  id: string
  organization_id: string
  created_by: string
  title: string
  department: string | null
  location: string | null
  employment_type: 'full-time' | 'part-time' | 'contract' | 'internship'
  years_experience: string | null
  salary_min: number | null
  salary_max: number | null
  description: string | null
  required_skills: string[]
  preferred_skills: string[]
  benefits: string | null
  status: 'draft' | 'active' | 'closed'
  application_deadline: string | null
  created_at: string
  updated_at: string
}

export interface Candidate {
  id: string
  organization_id: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  location: string | null
  linkedin_url: string | null
  other_url: string | null
  resume_file_path: string | null
  resume_text: string | null
  skills: string[]
  created_at: string
}

export interface Application {
  id: string
  candidate_id: string
  job_id: string
  status: 'new' | 'screening' | 'interview' | 'offer' | 'hired' | 'rejected'
  source: string
  applied_at: string
  updated_at: string
}

export interface AIAnalysis {
  id: string
  application_id: string
  overall_match_score: number
  technical_skills_score: number
  experience_score: number
  culture_score: number
  strengths: string[]
  missing_skills: string[]
  suggested_questions: string[]
  model_used: string
  created_at: string
}

export interface Paginated<T> {
  pagination: { page: number; per_page: number; total: number; total_pages: number }
  [key: string]: T[] | Paginated<T>['pagination']
}