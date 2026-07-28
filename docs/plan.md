# TalentLens — Project Plan

> AI-assisted Applicant Tracking System (ATS) for recruiting teams.
> Stack: React + TypeScript (frontend) · Flask + Python (backend) · PostgreSQL (database)

## Product Summary

TalentLens is a B2B ATS. Recruiting teams from a single company (an "organization")
sign up, post jobs, add/track candidates against those jobs, and use an AI feature to
analyze how well a candidate's resume matches a given job description — producing a
match score, strengths, missing skills, and suggested interview questions.

## Build Sequence

1. **Core loop (v1)** — Auth → Jobs (CRUD) → Candidates (CRUD) → AI Analysis
2. **v2** — Analytics dashboard, Settings (org/notifications/appearance), 404/403 polish,
   job distribution (publish to job boards) stub, bulk actions, exports

## Core Entities

```
Organization
- id, name, created_at

User
- id, organization_id, email, password_hash, first_name, last_name,
  role (admin/recruiter/viewer), avatar_url, email_verified, created_at, updated_at

PasswordResetToken
- id, user_id, token_hash, expires_at, used_at, created_at

Job
- id, organization_id, created_by, title, department, location, employment_type,
  years_experience, salary_min, salary_max, description,
  required_skills[], preferred_skills[], benefits, status (draft/active/closed),
  application_deadline, created_at, updated_at

Candidate
- id, organization_id, first_name, last_name, email, phone, location,
  linkedin_url, other_url (optional), resume_file_path, resume_text (parsed),
  skills[], created_at

Application  (join of Candidate <-> Job — a candidate can apply to multiple jobs)
- id, candidate_id, job_id, status (new/screening/interview/offer/hired/rejected),
  source (linkedin/referral/manual/etc), applied_at, updated_at

AIAnalysis  (versioned — one Application can have many, ordered by created_at)
- id, application_id, overall_match_score, technical_skills_score,
  experience_score, culture_score, strengths[] (json), missing_skills[] (json),
  suggested_questions[] (json), model_used, created_at

RecruiterNote
- id, application_id, author_id, content, created_at

JobDistribution  (v2 — publish-to-job-boards stub, adapter pattern)
- id, job_id, channel, status (pending/published/failed), external_url,
  published_at, created_at
```

See `erd.md` in this same folder for the visual entity-relationship diagram
and full SQL `CREATE TABLE` statements.

## User Stories (core loop, v1)

1. As a recruiter, I can sign up (creating a new organization), verify my account
   conceptually, and log in.
2. As a recruiter, I can create/edit/view/delete a job posting with all fields from
   the Create Job screen.
3. As a recruiter, I can see a paginated, searchable, filterable list of jobs.
4. As a recruiter, I can add a candidate manually (name, email, resume upload) and
   associate them with a job (creates an Application).
5. As a recruiter, I can see a paginated, searchable, filterable list of candidates.
6. As a recruiter, I can view a candidate's detail page showing parsed resume info.
7. As a recruiter, I can trigger AI analysis on a candidate+job pair and see the match
   score, strengths, missing skills, and generated interview questions.
8. As a recruiter, I can move a candidate through pipeline stages
   (new → screening → interview → offer → hired/rejected).

## Acceptance Criteria

### Job creation (maps to Create Job screen)
- Form requires: title, department, location, employment type. Salary/deadline/skills
  optional.
- On submit, POST to backend, validated server-side with the same rules as client-side
  (shared validation logic/schema).
- New job defaults to `draft` status unless "Publish" is clicked (→ `active`).
- Success → redirect to job detail or list, with a toast confirmation.
- Failure (validation or server error) → inline field errors, no data loss on the form.

### Jobs list
- (fill in during Step 4 planning — pagination size, filter fields, sort columns)

### Candidate creation
- (fill in — required fields, resume upload constraints, file types accepted)

### AI Analysis
- (fill in — what triggers a new analysis run, how the versioned history is displayed,
  loading/error states while waiting on the LLM)

### Pipeline stage transitions
- (fill in — which transitions are allowed, whether moving stages requires confirmation,
  whether rejecting requires a reason)

> Fill in the remaining acceptance criteria as an exercise before building each screen —
> this is deliberately left incomplete so you practice writing them yourself, the same
> way you'd need to on a real team before a feature is signed off.

## Open Questions (resolved)

- **Should AIAnalysis be versioned or overwritten?** → Versioned. Every re-analysis
  creates a new row; the "current" analysis is the latest by `created_at`.
- **How is Candidate linked to Job?** → Through the `Application` join table
  (many-to-many), not a direct foreign key on Candidate.
- **Should job-board publishing (LinkedIn/Internshala) be built for real?** → No —
  no public/partner API access is available. Built as a stub using an adapter pattern
  (`JobDistribution` table + a `MockJobBoardAdapter`) so a real integration is a
  drop-in replacement later, not a rewrite. Scheduled for v2.
- **Does signup join an existing org or always create one?** → v1: signup always
  creates a new organization. "Invite teammate" (join existing org) is deferred to v2,
  since it requires its own invite-token/acceptance flow similar to password reset.

## Assumptions

- Email verification and "invite teammate" flows are simplified/stubbed for v1 unless
  time allows for the real email-sending integration.
- Multi-tenancy is enforced by filtering every query on `organization_id` server-side —
  never trusted from the client.
- Skills are stored as Postgres `TEXT[]` arrays for v1 rather than a normalized join
  table — a deliberate simplicity trade-off (documented in `docs/architecture.md`).
