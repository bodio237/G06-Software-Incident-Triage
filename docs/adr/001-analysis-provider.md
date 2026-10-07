# ADR 001: Use an AnalysisProvider abstraction

* **Status:** Accepted
* **Date:** 2026-10-07

## Context

The Software Incident Triage application must use a local model through LM Studio, while CI must be able to run without LM Studio, a GPU or API tokens.

The project also requires provider code to remain outside the Streamlit UI and the business service.

Using the LM Studio implementation directly throughout the application would make automated testing and CI dependent on a running local model.

## Decision

We use an `AnalysisProvider` contract as the boundary between the application and the analysis implementation.

Two implementations are provided:

* `LocalAnalysisProvider` communicates with the LM Studio OpenAI-compatible API.
* `MockAnalysisProvider` provides deterministic behaviour for automated tests and CI.

The `AnalysisService` depends on the provider contract rather than directly depending on LM Studio.

The UI communicates with the API and does not contain provider-specific logic.

## Consequences

### Positive consequences

* CI can run without LM Studio, a GPU or an API token.
* The local model integration can be tested independently.
* The business service remains independent of the model transport.
* The provider can be replaced without changing the UI or API contract.
* HTTP communication can be tested using `httpx.MockTransport`.
* The architecture remains aligned with the required provider boundary.

### Negative consequences

* The project contains additional provider and interface code.
* The local provider and mock provider must both remain compatible with the same analysis contract.
* Some behaviour must be tested separately in mock mode and local-model mode.

## Alternatives considered

### Direct LM Studio calls from the API or UI

Rejected because this would couple application components to the local model and make CI dependent on LM Studio.

### Using only a mock provider

Rejected because the project explicitly requires integration with LM Studio and measured local-model evaluation.

### Calling LM Studio directly from the Streamlit UI

Rejected because provider code must remain outside the UI and business service.
