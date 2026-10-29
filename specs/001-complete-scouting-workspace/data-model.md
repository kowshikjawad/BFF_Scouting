# Data model

Player: existing ORM columns, no migration. `id` is required; all other stored facts are nullable.
`name` falls back to ID in presentation. Tactical metrics are nullable finite floats, never implied zero.

Search: q (trimmed, max 100 characters); position (max 50); max_age (0..100); max_value_eur
(finite >=0); strong_foot (Left/Right/Both); eligibility_status (three existing status values or
NOT_ASSESSED); sort (name, age_asc, value_desc). Unknown age/value sort last. ID breaks ties.

Shortlist: JSON string array under shonartalent.shortlist.v1; no player copies, maximum 500 IDs.
Storage parse/write failures are handled, and persistence limitations shown to the user.

Eligibility facts: integer years 0..100; years after 18 cannot exceed total years. False ancestry
claims ignore/reset documentation checkboxes. Existing output fields remain, adding reasons and
review_required. Prior youth caps without approval require manual association review.

Report: A4 one-page binary PDF, sanitized ASCII Content-Disposition filename, generation date,
profile facts, metrics and clear limitations. Arbitrary text is escaped before ReportLab markup.
