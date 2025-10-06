<!--
Sync Impact Report - Constitution Update
═══════════════════════════════════════════════════════════════════════════

Version Change: [TEMPLATE] → 1.0.0 (Initial ratification)

Modified Principles:
  - All principles newly defined from template

Added Sections:
  - Core Principles (5 principles)
  - Code Quality Standards
  - Development Workflow
  - Governance

Removed Sections:
  - Template placeholders removed

Templates Status:
  ✅ plan-template.md - Constitution Check section references this file
  ✅ spec-template.md - No structural changes needed, aligns with principles
  ✅ tasks-template.md - TDD and parallel execution align with principles
  ⚠ commands/*.md - No command files exist yet in .specify/templates/commands/

Follow-up TODOs:
  - None. All placeholders resolved.
  - Ratification date set to today (initial adoption)

═══════════════════════════════════════════════════════════════════════════
-->

# mlc_dashboard Constitution

## Core Principles

### I. Clean and Modular Code (NON-NEGOTIABLE)
Every component, service, and function MUST have a single, clear responsibility. Code MUST be organized into logical modules with well-defined boundaries. Avoid monolithic files exceeding 300 lines; refactor into smaller, focused modules. Dependencies between modules MUST flow in one direction (no circular dependencies).

**Rationale**: Modular code is easier to test, debug, maintain, and scale. It enables parallel development and reduces cognitive load when making changes.

### II. FastAPI Best Practices
Backend code MUST follow FastAPI conventions and idioms:
- Use async/await for I/O-bound operations (database, external APIs)
- Define Pydantic models for request/response validation
- Implement dependency injection for shared resources (database sessions, auth)
- Use APIRouter for logical endpoint grouping
- Document all endpoints with proper OpenAPI metadata (descriptions, tags, examples)
- Handle errors with HTTPException and custom exception handlers
- Implement proper CORS, authentication, and security middleware

**Rationale**: FastAPI provides built-in tools for security, validation, and documentation. Following framework conventions ensures consistency and leverages ecosystem best practices.

### III. React Best Practices
Frontend code MUST follow React conventions and modern patterns:
- Use functional components with hooks (avoid class components)
- Implement proper component composition and prop drilling avoidance (Context API, state management)
- Follow single responsibility principle for components (<200 lines)
- Use TypeScript for type safety across all components
- Implement proper error boundaries and loading states
- Follow accessibility standards (WCAG 2.1 AA minimum)
- Use semantic HTML and proper ARIA attributes
- Optimize re-renders with useMemo, useCallback, and React.memo where appropriate

**Rationale**: Modern React patterns improve code readability, performance, and maintainability. TypeScript catches errors at compile-time, reducing runtime bugs.

### IV. Test-First Development (NON-NEGOTIABLE)
TDD MUST be followed for all features:
- Write tests BEFORE implementation (Red-Green-Refactor)
- Backend: pytest with fixtures, async tests, and database mocking
- Frontend: Vitest/React Testing Library for component and integration tests
- Achieve minimum 80% code coverage
- Contract tests MUST verify API request/response schemas
- Integration tests MUST validate end-to-end user flows
- Tests MUST be independent and runnable in any order

**Rationale**: Writing tests first ensures code is testable, prevents over-engineering, and catches regressions early. It serves as living documentation of intended behavior.

### V. Type Safety and Validation
Strong typing MUST be enforced at all boundaries:
- Backend: Pydantic models for all API inputs/outputs, SQLModel for database entities
- Frontend: TypeScript with strict mode enabled, no `any` types without justification
- Database: Use migrations (Alembic) with proper schema validation
- Validate data at system boundaries (API endpoints, database writes, external integrations)
- Use type guards and runtime validation where static typing is insufficient

**Rationale**: Type safety catches errors at compile-time, improves IDE support, and serves as self-documenting code. Runtime validation prevents invalid data from entering the system.

## Code Quality Standards

### Formatting and Linting
- **Python**: Black (line length 100), isort (STDLIB → THIRDPARTY → FIRSTPARTY)
- **TypeScript**: ESLint with TypeScript rules, Prettier for formatting
- **Consistency**: Run formatters before all commits
- **Configuration**: Centralize in pyproject.toml (.flake8 for flake8) and package.json

### Code Review Requirements
- All changes MUST pass automated linting and tests
- Reviews MUST check for: modularity, test coverage, type safety, naming clarity
- No PR merges without passing CI/CD pipeline
- Constitutional violations MUST be documented and justified in PR description

### Documentation Standards
- API endpoints: OpenAPI/Swagger documentation (auto-generated by FastAPI)
- Complex functions: Docstrings explaining purpose, parameters, return values, and side effects
- Architecture decisions: Document in CLAUDE.md or architecture decision records (ADRs)
- User-facing features: Update quickstart guides and user documentation

## Development Workflow

### Version Control
- Feature branches from main: `###-feature-name` format
- Atomic commits with clear messages
- Commit message format: `type(scope): description` (e.g., `feat(auth): add OAuth2 login`)
- Squash commits before merging to main

### CI/CD Pipeline
- Automated: linting, type checking, tests, security scans
- Manual: code review, acceptance testing, deployment approval
- All checks MUST pass before merge to main

### Database Migrations
- Use Alembic for all schema changes
- Migrations MUST be reversible (downgrade scripts required)
- Test migrations on staging before production
- Never modify existing migrations; create new ones

### Environment Configuration
- Use .env files for local development (never committed)
- Centralized config in backend/app/core/config.py using Pydantic BaseSettings
- Environment-specific configs: development, staging, production
- Secrets MUST use environment variables or secret management services (never hardcoded)

## Governance

This Constitution supersedes all other development practices and preferences. Any deviation from these principles MUST be documented with:
1. Clear rationale for why deviation is necessary
2. Evidence that simpler constitutional approaches were considered
3. Approval from project lead or team consensus

### Amendment Process
- Proposed changes MUST include rationale and impact analysis
- Constitution version follows semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Principle removed or fundamentally redefined
- MINOR: New principle or section added
- PATCH: Clarifications, wording improvements, non-semantic fixes
- All amendments update LAST_AMENDED_DATE and increment version

### Compliance Review
- Code reviews MUST verify constitutional compliance
- Unjustified complexity or violations MUST be rejected
- Periodic audits (quarterly) to ensure ongoing adherence
- Constitution violations found in production MUST be tracked and remediated

### Tool-Specific Guidance
- Claude Code: See CLAUDE.md for AI-assisted development guidance
- GitHub Copilot: See .github/copilot-instructions.md (when applicable)
- All AI tools MUST follow constitutional principles

**Version**: 1.0.0 | **Ratified**: 2025-10-04 | **Last Amended**: 2025-10-04
