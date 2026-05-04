# Supervised MVP Test Plan

This plan is written for a non-technical supervisor. Follow the steps in order. At each step,
compare the screen output with the expected success text.

## Before You Start

Open PowerShell in the repository folder:

```powershell
cd "D:\Agent Growth Layer"
```

Make sure Docker Desktop is open.

## Step 1: Confirm The Project Is Clean

Command:

```powershell
git status --short
```

Success:

- The command prints nothing.

Failure:

- Any file names appear.
- Stop and ask the developer what changed before continuing.

## Step 2: Confirm Docker Is Running

Command:

```powershell
docker version
```

Success:

- You see both `Client:` and `Server:` sections.
- The `Server` section mentions Docker Desktop or Docker Engine.

Failure:

- You see `failed to connect to the docker API`.
- You see `dockerDesktopLinuxEngine` not found.
- Open Docker Desktop, wait until it says it is running, then try again.

## Step 3: Build And Start The Docker MVP

Command:

```powershell
docker compose up --build -d
```

Success:

- You see `Image agentgrowthlayer-api Built`.
- You see `Container agentgrowthlayer-api-1 Started`.

Failure:

- You see build errors, Python install errors, or container startup errors.
- Copy the last 30 lines and give them to the developer.

## Step 4: Check API Health

Command:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Success:

- The response includes `status : ok`.

Failure:

- The command cannot connect.
- The response is not `ok`.
- Run `docker compose ps` and give the output to the developer.

## Step 5: Run The Basic MVP Chain In Docker

Command:

```powershell
python scripts\verify_local_mvp.py --base-url http://127.0.0.1:8000
```

Success:

- The final line is `Local MVP verification passed.`
- You should also see lines for:
  - `health: ok`
  - `seed guidance`
  - `experience learning`
  - `feedback`
  - `prompt import`
  - `skill exam`
  - `audit`
  - `verified guidance: ok`

Failure:

- The script stops before `Local MVP verification passed.`
- If it says `extraction failed`, the learning step failed.
- If it says `timed out`, the background extraction did not finish in time.

## Step 6: Run The Project-Level MVP Chain In Docker

Command:

```powershell
python scripts\verify_project_mvp.py --base-url http://127.0.0.1:8000
```

Success:

- The final line starts with `Project MVP verification passed`.
- You should also see:
  - `project initial guidance`
  - `project experience`
  - `project experience review`
  - `project cognition review`
  - `project skill build`
  - `project exam`
  - `needs_review`
  - `project skill review`
  - `project verified guidance: ok`

Failure:

- No `needs_review` line means the human review gate did not work.
- No `project verified guidance: ok` means the approved skill did not enter guidance.

## Step 7: Stop Docker

Command:

```powershell
docker compose down
```

Success:

- You see the container stopped and removed.
- You see the network removed.

Failure:

- The container remains running.
- Run `docker compose ps` and give the output to the developer.

## Step 8: Run Full Python Tests

Command:

```powershell
python -m pytest
```

Success:

- The final result says `36 passed`.

Failure:

- Any `FAILED` line appears.
- Copy the failed test name and error block.

## Step 9: Run Code Quality Check

Command:

```powershell
python -m ruff check .
```

Success:

- The output says `All checks passed!`

Failure:

- Any file and line number appears.
- Give the output to the developer.

## Step 10: Run Python Compile Check

Command:

```powershell
python -m compileall server sdk examples scripts
```

Success:

- The command exits without an error.
- It may print many `Listing` lines. That is normal.

Failure:

- You see `SyntaxError`, `PermissionError`, or `failed`.

## Step 11: Run JavaScript SDK Build

Commands:

```powershell
cd "D:\Agent Growth Layer\sdk\javascript"
npm.cmd ci
npm.cmd run build
cd "D:\Agent Growth Layer"
```

Success:

- `npm.cmd ci` says `found 0 vulnerabilities`.
- `npm.cmd run build` exits without errors.

Failure:

- `npm.ps1 cannot be loaded` means the wrong npm command was used. Use `npm.cmd`.
- TypeScript errors mean the JS SDK is broken.

## Step 12: Secret Scan

Commands:

```powershell
rg -n 'sk-[A-Za-z0-9]{16,}' -S . -g '!sdk/javascript/node_modules/**' -g '!data/**' -g '!*.sqlite*'
rg -n 'Authorization: Bearer [A-Za-z0-9_-]{16,}' -S . -g '!sdk/javascript/node_modules/**' -g '!data/**' -g '!*.sqlite*'
```

Success:

- Both commands print nothing.

Failure:

- Any API key-like value appears.
- Do not commit. Ask the developer to remove it and rotate the exposed key.

## Step 13: Optional DeepSeek LLM Test

Only run this if you have a fresh temporary DeepSeek key.

Do not write the key into a file.

Commands:

```powershell
$env:AGL_LLM_PROVIDER="openai_compatible"
$env:AGL_LLM_BASE_URL="https://api.deepseek.com"
$env:AGL_LLM_API_KEY="paste_new_temporary_key_here"
$env:AGL_LLM_MODEL="deepseek-v4-flash"
$env:AGL_LLM_TIMEOUT_SECONDS="45"
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Open a second PowerShell window:

```powershell
cd "D:\Agent Growth Layer"
python scripts\verify_llm_provider.py --base-url http://127.0.0.1:8000
```

Success:

- The final line starts with `LLM provider verification passed`.
- You see:
  - `llm extraction`
  - `llm prompt import`
  - `llm judge`

Failure:

- `LLM extraction failed` means the provider output did not match the expected schema or the
  provider request failed.
- `401` or `403` means the key is invalid or unauthorized.
- After testing, revoke or rotate the temporary key.

## Final Pass Criteria

The MVP is accepted only when all required checks pass:

- Docker health passes.
- Docker basic MVP chain passes.
- Docker project MVP review-gate chain passes.
- `python -m pytest` passes.
- `python -m ruff check .` passes.
- Python compile check passes.
- JS SDK build passes.
- Secret scan prints nothing.

The optional DeepSeek test is only required when validating real BYOK LLM behavior.
