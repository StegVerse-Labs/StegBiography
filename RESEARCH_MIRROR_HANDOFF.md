# StegBiography Research Mirror Handoff

## Authority
- goal_id: ERL-RESEARCH-SURFACE-STEGBIOGRAPHY-001
- repository: StegVerse-Labs/StegBiography
- branch: main
- canonical_owner: StegVerse-Labs/Executive_Rhetoric_Ledger Issue #60
- local_role: evidence-linked biographical source discovery and candidate production
- evaluation_authority: StegVerse-Labs/Executive_Rhetoric_Ledger
- credential_authority: TV/TVC where applicable
- github_token_authority: NONE

## Claim
- state: CLAIMED_FOR_VALIDATION
- release_condition: deterministic populated fixture + ERL intake validation + registry promotion

## Installed authoritative files
`research/README.md`, `research/frontier.json`, `research/acquisition_requests.jsonl`, `research/source_candidates.jsonl`, `research/research_receipts.jsonl`, `research/conformance.json`, `data/sources/sources_whitelist.csv`, `scripts/search_agent.py`.

Upstream standard: `StegVerse-Labs/Executive_Rhetoric_Ledger/standards/multi-trajectory-research-surface.v1.md`.
Upstream transport: `StegVerse-Labs/Executive_Rhetoric_Ledger/contracts/research-candidate-transport.v1.md`.

## Research posture
- recurrence: DELEGATED by default to the canonical registered subject-specific repository for each trajectory;
- umbrella recurrence must not duplicate subject-owned searches;
- if no subject-specific owner exists, the trajectory must be independently classified REQUIRED/SHOULD/NOT_REQUIRED;
- all plausible trajectories remain eligible for acquisition; local candidates remain lead-only/context-only until ERL review.

## Evidence
- research surface: `06857da5d83c26278ea21748173643b6ad6c0d47`
- conformance/recurrence profile: `2c27df3e76c7a4d76dc73126a0e3eb1aa94fd1f7`
- adapter transport alignment: `b183b841d10cd96db97bb8d8b5baed3045710512`

The adapter now emits `stegverse.erl.research_source_candidate.v1` with full repository identity, no native/evaluation mutation, TV/TVC credential authority, GitHub token authority NONE, and authority effect NONE.

## Remaining
1. populated deterministic fixture including delegated-recurrence behavior;
2. ERL candidate intake validation;
3. registry promotion to CONFORMING.

## Validation
- `python scripts/search_agent.py --base . --dry-run`
- `python <ERL>/scripts/validate_research_surface.py .`
- `python <ERL>/scripts/validate_research_candidate_intake.py research/source_candidates.jsonl`

## Completion accounting
- developed-files: 9/9 = 100%
- scaffolding/stubs: 0
- validation: 0/3
- integration: 2/3
- goal-activation: 75%
