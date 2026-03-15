<!--
  Sync Impact Report
  ===================
  Version change: (new) → 1.0.0
  Modified principles: N/A (initial ratification)
  Added sections:
    - Core Principles (5 principles)
    - Platform Compatibility (Section 2)
    - Development Workflow (Section 3)
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no changes needed (Constitution Check section is generic)
    - .specify/templates/spec-template.md ✅ no changes needed (structure-agnostic)
    - .specify/templates/tasks-template.md ✅ no changes needed (phase structure accommodates principles)
  Follow-up TODOs: None
-->

# Smart Mirror Constitution

## Core Principles

### I. Layered Architecture

All code MUST respect the layer boundary: `core/` contains business
logic with zero UI dependencies; `ui/` handles presentation only;
`db/` handles persistence only. Screen classes MUST NOT contain
business logic. Services MUST NOT import from `ui/`. This separation
ensures testability and keeps the domain portable across interfaces.

### II. Non-Blocking UI

The main Qt thread MUST never perform blocking operations—camera
capture, face detection, AI inference, and database queries that
could exceed 50 ms MUST run in worker threads. All thread-to-UI
communication MUST use Qt signals/slots. Direct widget manipulation
from worker threads is forbidden.

### III. Platform Abstraction

Hardware-dependent functionality (camera, inference, face detection
model selection) MUST be accessed through abstract backends with
platform-specific implementations selected by factory functions at
runtime. Application code MUST NOT branch on platform outside
`config.py` and factory functions. Every feature MUST work on Desktop
macOS, Desktop Linux, and Jetson Orin Nano without code changes
beyond configuration.

### IV. Lazy Resource Loading

AI models (Stable Diffusion, face detection/recognition) and heavy
resources MUST be loaded on first use inside worker threads, never at
application startup. This keeps startup time fast and avoids loading
models that may not be needed in a given session.

### V. Simplicity First

Start with the simplest solution that works. No speculative
abstractions, no premature optimization, no features beyond current
requirements. Every added layer of complexity MUST be justified by a
concrete, present need. Prefer three similar lines of code over a
premature abstraction.

## Platform Compatibility

All features MUST be validated against three target platforms:

| Concern        | Desktop macOS | Desktop Linux | Jetson Orin Nano |
|----------------|---------------|---------------|------------------|
| Camera         | OpenCV        | OpenCV        | Jetson CSI       |
| Inference      | MPS / CPU     | CPU           | CUDA             |
| Resolution     | 640x480       | 640x480       | 1280x720         |
| Face model     | HOG           | HOG           | CNN              |

Platform detection is handled exclusively by `config.py`
(`detect_platform()`). New platform-specific behavior MUST be
introduced through the existing factory pattern, never through
ad-hoc conditionals scattered across the codebase.

## Development Workflow

- **Entry point**: `main.py` (`SmartMirrorController`) wires config,
  DB, services, inference backend, UI screens, worker threads, and
  the event loop. New features MUST integrate through this controller.
- **Database migrations**: Tables are auto-created and the hairstyle
  catalog is auto-seeded on first run. Schema changes MUST preserve
  this auto-initialization behavior.
- **Dependencies**: Desktop dependencies live in `requirements.txt`;
  Jetson dependencies in `requirements-jetson.txt`. New dependencies
  MUST be added to the appropriate file(s).
- **Configuration**: Environment-driven via `.env`. New configurable
  values MUST be added to `config.py` with sensible defaults and
  documented in `.env.example`.

## Governance

This constitution is the authoritative source for architectural
decisions in the Smart Mirror project. All code contributions MUST
comply with these principles. When a principle conflicts with a
proposed change, the principle wins unless the constitution is
amended first.

**Amendment process**:
1. Propose the change with rationale.
2. Document the amendment in this file with an updated Sync Impact
   Report.
3. Increment the version per semantic versioning (MAJOR for principle
   removal/redefinition, MINOR for new principles, PATCH for
   clarifications).
4. Propagate changes to dependent templates if affected.

**Compliance**: All code reviews and planning artifacts MUST verify
alignment with these principles. Use CLAUDE.md for runtime
development guidance.

**Version**: 1.0.0 | **Ratified**: 2026-03-15 | **Last Amended**: 2026-03-15
