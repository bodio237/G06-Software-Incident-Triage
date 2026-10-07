# ADR 002: Validate analysis output and require human review

* **Status:** Accepted
* **Date:** 2026-10-07

## Context

The application uses a local language model to propose an initial routing decision for software incidents.

Model output cannot be assumed to be valid or safe. The project requires the application to reject invalid JSON and unknown categories, validate the structured result, and ensure that ambiguous requests remain reviewable.

The application must also never claim that a production action, rollback or fix has been performed.

## Decision

We validate both incoming requests and model-generated analysis using Pydantic models.

Incoming requests must satisfy the required subject and request-text length limits.

The model response must contain the expected structured fields:

* `summary`
* `category`
* `priority`
* `next_action`

The application validates the generated JSON before saving it.

The category must belong to the scenario's allowed categories:

* `availability`
* `performance`
* `release`

Priority is restricted to:

* `low`
* `medium`
* `high`

Invalid JSON, malformed model output or an invalid category results in a controlled API error rather than a stored analysis.

Validated records are stored in SQLite only after successful validation.

Every returned record keeps:

```text
requires_review = true
```

The application only proposes a next action for a human reviewer. It does not perform production commands, rollback operations or other remediation actions.

## Consequences

### Positive consequences

* Invalid model responses are rejected before persistence.
* The API contract remains predictable.
* Scenario categories cannot be silently replaced by arbitrary model output.
* Failed inference does not create a successful history record.
* Every analysis remains explicitly subject to human review.
* The system does not falsely represent a proposed action as an executed production action.
* Automated tests can verify validation and failure behaviour deterministically.

### Negative consequences

* The application requires additional validation logic around model output.
* Some model responses may be rejected even when they contain potentially useful information.
* Human review remains necessary for every result.

## Alternatives considered

### Trust the model output directly

Rejected because language-model output is not guaranteed to follow the required JSON structure or scenario contract.

### Automatically execute the proposed next action

Rejected because the project explicitly requires a routing proposal without running production commands or performing a rollback.

### Store invalid results for later inspection

Rejected because the project requires only validated analysis records to be stored as successful results.
