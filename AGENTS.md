Repository Guidelines

---

## Project Structure & Module Organization
- **src/** – TypeScript source code (React components, hooks, utilities).
- **tests/** – Jest unit tests mirroring the `src` tree.
- **public/** – Static assets served by Vite (images, fonts).
- **scripts/** – Helper shell scripts used during CI or local development.
- **package.json** – Project dependencies and npm scripts.

All code is written in TypeScript; keep source inside `src/` and tests next to their module under `tests/`. Do not store large binaries—use the `public/` folder instead.

## Build, Test, and Development Commands
| Command | What it does |
|---------|--------------|
| `npm run dev` | Starts Vite dev server with hot‑reload. |
| `npm run build` | Builds a production bundle into `dist/`. |
| `npm test` | Runs Jest unit tests. |
| `npm run lint` | Executes ESLint & Prettier checks. |

Scripts are defined in **package.json** and invoked via `npm run <name>`.

## Coding Style & Naming Conventions
- **Indentation:** 2 spaces per level, no tabs.
- **ESLint:** `@typescript-eslint/recommended` + React hooks rules; run `npm run lint` before committing.
- **Prettier:** line‑length 80 chars, semicolons mandatory.
- **Component names:** PascalCase (`UserProfile.tsx`).
- **Hook names:** `useXxx` prefix (`useAuth`).
- **Constants:** Uppercase with underscores (`MAX_RETRIES`).

Formatting is auto‑applied by Prettier; run it locally or rely on the pre‑commit hook.

## Testing Guidelines
The test suite uses Jest + React Testing Library. Test files are `*.test.tsx` under `tests/`.
- Run all tests: `npm test`
- Watch mode: `npm test -- --watch`
- Coverage report: `npm test -- --coverage`
Coverage should stay above **80 %** for new code; add unit tests if a feature requires more coverage.

## Commit & Pull Request Guidelines
### Commit messages
Follow conventional‑commits (see commit history):
```
type(scope?): subject
```
Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`. Subject line ≤ 72 characters.
### Pull requests
- Clear title & description referencing any linked issue.
- Include screenshots/GIFs if UI changes occur.
- Run `npm test && npm run lint` locally before submitting.
- Ensure CI passes (GitHub Actions runs tests, linting, and build).
After approval and passing checks, merge with a **squash‑merge** to keep history tidy.

---
