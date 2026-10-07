# AI Usage

## Project

**G06 – Software Incident Triage**

## Students

* **Pricilia Bodio**
* **Danielle Keune**

## Use of coding assistants

During the development of this project, we used a coding assistant as a development support tool.

The assistant was used to help us:

* understand the project requirements and technical constraints;
* reason about the FastAPI, Pydantic, Streamlit, SQLite and `httpx` architecture;
* design and refine the `AnalysisProvider` abstraction;
* implement and debug the local LM Studio provider;
* improve validation and error handling;
* design and extend automated tests;
* investigate timeout and malformed-model-output cases;
* prepare the Dockerfile and Docker smoke test;
* prepare and validate the Terraform configuration;
* prepare the Jenkins pipeline;
* understand Git workflows, branches and pull requests;
* review implementation choices and identify possible missing requirements;
* improve project documentation.

## How AI-generated suggestions were used

AI suggestions were treated as development assistance rather than as authoritative code or project decisions.

We reviewed the proposed changes, adapted them to the supplied project structure and requirements, and tested the resulting implementation locally.

In particular, model-related behaviour was verified against the actual LM Studio environment rather than being assumed from generated suggestions.

Automated tests were used to validate important application behaviour, including:

* request validation;
* provider timeout handling;
* malformed model output;
* scenario cases;
* API behaviour;
* persistence of validated results.

Docker and Terraform configurations were also executed and validated locally.

## Human responsibility

The final implementation was reviewed and validated by the students.

We remained responsible for:

* choosing which suggestions to keep;
* adapting generated suggestions to the project architecture;
* running tests and interpreting their results;
* checking the application with LM Studio;
* validating Docker and Terraform behaviour;
* ensuring that the implementation follows the project brief;
* documenting limitations and observed behaviour.

The coding assistant was not used to claim that production actions had been performed. The application itself maintains `requires_review=true` and does not perform production remediation or rollback actions.

## Limitations

AI-generated suggestions may contain errors or assumptions that do not match the project's environment. For this reason, generated code and recommendations were not accepted without verification.

Observed behaviour from the actual project environment, test results and tool outputs takes precedence over suggestions from the coding assistant.

## Summary

AI assistance was used throughout the project as a support for development, debugging, testing, infrastructure configuration and documentation. The students remained responsible for the final code, technical decisions, verification and project deliverables.
