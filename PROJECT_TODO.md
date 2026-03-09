# Jarvis Project Review & TODO

## Current State Summary

- Local Ollama integration works and supports `/api/chat` with `/api/generate` fallback.
- GUI text chat is active in `main.py` and voice loop is optional.
- Task commands are routed by code first, then conversational fallback goes to Ollama.
- Basic persistent memory exists (`user_memory.json` for user name).
- `main.py` was reduced by extracting command routing to `Jarvis/features/command_router.py`.

## Priority TODO (Do Next)

- [ ] **P0 - Environment parity**: Ensure runtime dependencies install in active venv (`PyQt5`, `pyautogui`, `pywhatkit`, `pyjokes`).
- [ ] **P0 - Split remaining main.py responsibilities**: Move memory + LLM orchestration helpers from `main.py` to `Jarvis/features/local_brain.py`.
- [ ] **P0 - Improve task feedback in UI**: Replace generic `Task completed.` with action-specific responses.
- [ ] **P0 - Add startup health check**: Validate Ollama reachability/model availability at app start and show status in UI.

## Architecture Improvements

- [ ] **P1 - Skill registry**: Define a formal registry for task skills (`name`, `matcher`, `handler`, `description`).
- [ ] **P1 - Intent router**: Let Ollama return structured intents for ambiguous requests while deterministic commands stay local.
- [ ] **P1 - Memory expansion**: Add preferences/reminders/history summary beyond just `name`.
- [ ] **P1 - Config hygiene**: Add comments/examples and safer defaults in `Jarvis/config/config.py`.

## Reliability & UX

- [ ] **P1 - Non-blocking status line**: Show `Listening`, `Thinking`, `Executing task`, `Done/Error` states in UI.
- [ ] **P1 - Voice robustness**: Add explicit microphone device selection and timeout controls.
- [ ] **P1 - URL command quality**: Support multi-word domain phrases and better disambiguation (`open my github profile`).
- [ ] **P2 - Error taxonomy**: Standardize user-facing errors vs debug logs.

## Performance

- [ ] **P1 - Fast-path map**: Expand instant local handlers (battery, IP, date/time, basic calculations).
- [ ] **P1 - Adaptive model routing**: Optional `fast_model` and `deep_model` for speed vs quality.
- [ ] **P2 - Response streaming in UI**: Stream partial LLM output to improve perceived speed.

## Code Quality

- [ ] **P1 - Remove wildcard Qt imports** where possible and keep explicit imports only.
- [ ] **P1 - Add type hints** on new modules (`command_router`, memory/orchestrator code).
- [ ] **P1 - Add lint/format config** (`ruff` or `flake8` + `black`) and run in CI/local task.
- [ ] **P2 - Reduce legacy cloud code paths** if local-only is permanent goal.

## Testing

- [ ] **P0 - Add smoke test script** for startup + Ollama ping + one prompt roundtrip.
- [ ] **P1 - Add unit tests** for memory command parsing (`remember my name`, `what is my name`).
- [ ] **P1 - Add command routing tests** for key task handlers (`open`, `time/date`, `exit`).

## Documentation

- [ ] **P0 - Keep README synced** with architecture changes after each refactor.
- [ ] **P1 - Add developer guide**: module responsibilities and extension pattern for new skills.
- [ ] **P1 - Add troubleshooting matrix** for common local issues (PyAudio, Ollama port, model mismatch).

## Suggested Implementation Order

1. P0 environment/install reliability
2. P0 split remaining `main.py` logic into modules
3. P0 startup health checks + specific task feedback
4. P1 memory expansion and intent router
5. P1 tests and linting
