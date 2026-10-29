# API contracts

- GET /api/v1/players: existing array response retained. Accept existing filters plus q,
eligibility_status and sort. Canonical position matching includes secondary positions.
- GET /api/v1/players/{id}: all stored nullable profile and metric fields; 404 if absent.
- GET /api/v1/players/{id}/report.pdf: application/pdf download, one A4 page; 404 if absent.
- GET /api/v1/players/{id}/similar?top_k=5: existing array, top_k bounded 1..50; 404 if absent;
empty array when no usable metrics/candidates.
- POST /api/v1/players/{id}/eligibility: stateless screening, 422 for invalid facts; existing
status/switch fields plus reasons (string array), review_required (boolean), ruleset (string).
- GET /health: API health. Unknown /api paths stay JSON 404, never SPA HTML.
- Production GET / and valid client routes serve built frontend; assets preserve HTTP 404s.
