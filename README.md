# Bob Modernization Navigator
**IBM Bob Dev Day Hackathon — Complete Setup & Usage Guide**

---

## Table of Contents
1. [What This Project Does](#1-what-this-project-does)
2. [Project Structure](#2-project-structure)
3. [Setup: VS Code + Python](#3-setup-vs-code--python)
4. [Setup: IBM Bob IDE](#4-setup-ibm-bob-ide)
5. [Running the Analyzer](#5-running-the-analyzer)
6. [Using Bob IDE to Fix Issues](#6-using-bob-ide-to-fix-issues)
7. [The Full Hackathon Workflow](#7-the-full-hackathon-workflow)
8. [Exporting Bob Sessions for Judging](#8-exporting-bob-sessions-for-judging)
9. [Bob Prompts Reference](#9-bob-prompts-reference)

---

## 1. What This Project Does

Bob Modernization Navigator is a CLI agent that scans legacy Java/Spring Boot and Node.js
repositories, identifies modernization issues, and generates IBM Bob IDE prompts to implement fixes.

**What the scanner detects:**

| Category | Examples |
|---|---|
| Dependencies | Old Java version, old Spring Boot, legacy JUnit 4, deprecated Node packages |
| Deprecated APIs | `javax.*` imports, `WebSecurityConfigurerAdapter`, `var` in JavaScript |
| Security | SQL injection, hardcoded secrets, disabled CSRF, permissive CORS, weak hashes |
| Test Gaps | Source files with no corresponding test class |

**What it generates (in the output directory):**

| File | Purpose |
|---|---|
| `modernization-report.md` | Full technical findings + migration roadmap |
| `bob-prompts.md` | Ready-to-paste prompts for IBM Bob IDE |
| `judge-summary.md` | Concise summary for hackathon judges |
| `dashboard.html` | Visual findings dashboard — open in any browser |

---

## 2. Project Structure

```
bob-modernization-navigator/
│
├── main.py                          ← CLI entry point  (bmn analyze ...)
├── setup.py                         ← Makes `bmn` command available
├── requirements.txt
│
├── src/
│   ├── models.py                    ← Finding, RepoProfile, ModernizationResult
│   ├── scanner.py                   ← Detects project type, build tool, CI status
│   ├── analyzers/
│   │   ├── base.py                  ← Abstract base class for all analyzers
│   │   ├── dependency_analyzer.py   ← pom.xml / package.json checks
│   │   ├── deprecated_api_analyzer.py ← javax, old Spring Security, var, etc.
│   │   ├── security_analyzer.py     ← Secrets, SQL injection, CORS, eval()
│   │   └── test_gap_analyzer.py     ← Missing test file detection
│   └── report/
│       └── report_generator.py      ← Generates all 4 output files
│
├── scripts/
│   └── compare_runs.py              ← Before vs after comparison table
│
├── sample-apps/
│   └── legacy-spring-app/           ← Intentionally legacy Spring Boot 2 app
│       ├── pom.xml                  ← Old Java 11, Spring Boot 2.7, JUnit 4
│       └── src/main/java/com/example/
│           ├── SecurityConfig.java  ← WebSecurityConfigurerAdapter (deprecated)
│           ├── controller/UserController.java  ← @CrossOrigin("*")
│           ├── repository/UserRepository.java  ← SQL injection via concatenation
│           └── resources/application.properties ← Hardcoded secrets
│
└── bob_sessions/                    ← Put your exported Bob task reports here
```

---

## 3. Setup: VS Code + Python

### Step 1 — Open the project

```bash
# Unzip the project (or clone it)
unzip bob-modernization-navigator.zip
cd bob-modernization-navigator

# Open in VS Code
code .
```

### Step 2 — Create a Python virtual environment

Open the **VS Code Terminal** (`Ctrl+`` ` ``  or  `Terminal → New Terminal`) and run:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` appear in your terminal prompt.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

The `-e .` installs the project in editable mode and makes the `bmn` command available.

### Step 4 — Confirm installation

```bash
bmn --help
```

Expected output:
```
Usage: bmn [OPTIONS] COMMAND [ARGS]...
  Bob Modernization Navigator — legacy code modernization agent.

Commands:
  analyze  Scan a repository and generate modernization reports.
```

### Step 5 — Select Python interpreter in VS Code

Press `Ctrl+Shift+P` → type **"Python: Select Interpreter"** → choose the one from `.venv`.

This ensures VS Code uses your virtual environment for IntelliSense and running files.

---

## 4. Setup: IBM Bob IDE

### Step 1 — Install Bob IDE

Download and install Bob IDE from the link in your hackathon invitation email.

Bob IDE is a standalone desktop application (not a VS Code extension).
You can run it alongside VS Code — both open at the same time.

### Step 2 — Log in to Bob IDE

1. Open Bob IDE
2. Click **"Log in to Bob"**
3. Complete the IBMid authentication in your browser
4. Return to Bob IDE once authentication succeeds

### Step 3 — Switch to the hackathon account

> ⚠️ This step is critical. If you skip it, you will spend Bobcoins from your personal account.

1. In Bob IDE, click the **Settings icon** (⚙️) in the top-right
2. Under **General → Team**, click the dropdown
3. Select the team named **`ibm-coding-challenge-xxx`** (your hackathon team)
4. Confirm **Budget: 40 Bobcoins** is shown

### Step 4 — Open the project workspace in Bob IDE

1. In Bob IDE, click **"Open Folder"** (or use the folder icon)
2. Navigate to and select the `bob-modernization-navigator` folder
3. Bob will index the workspace — this gives it full context of your code

### Step 5 — Open Bob Chat

Click the **Bob icon** in the Bob IDE sidebar to open the chat panel.
Bob chat is where you paste prompts to analyze, fix, and document code.

---

## 5. Running the Analyzer

### First scan (baseline — before fixes)

```bash
# In VS Code terminal, with .venv activated
bmn analyze \
  --repo sample-apps/legacy-spring-app \
  --output modernization-output-before
```

This generates 4 files in `modernization-output-before/`:

```
modernization-output-before/
  modernization-report.md   ← Open this first
  bob-prompts.md            ← Use these in Bob IDE
  judge-summary.md          ← For judges
  dashboard.html            ← Open in browser for visual summary
```

**Open the dashboard:**
```bash
# macOS
open modernization-output-before/dashboard.html

# Windows
start modernization-output-before/dashboard.html

# Linux
xdg-open modernization-output-before/dashboard.html
```

### Second scan (after Bob fixes)

```bash
bmn analyze \
  --repo sample-apps/legacy-spring-app \
  --output modernization-output-after
```

### Compare before vs after

```bash
python scripts/compare_runs.py \
  modernization-output-before \
  modernization-output-after
```

Example output:
```
╔══════════════════╦══════════╦══════════╦════════════╗
║ Severity         ║  Before  ║  After   ║  Δ Change  ║
╠══════════════════╬══════════╬══════════╬════════════╣
║ Critical         ║        2 ║        0 ║      ▼ 2   ║
║ High             ║        6 ║        3 ║      ▼ 3   ║
║ Medium           ║        4 ║        2 ║      ▼ 2   ║
║ Low              ║        0 ║        0 ║          — ║
╠══════════════════╬══════════╬══════════╬════════════╣
║ TOTAL            ║       12 ║        5 ║      ▼ 7   ║
╚══════════════════╩══════════╩══════════╩════════════╝

✅ Improvement: 7 findings resolved (58% reduction)
```

---

## 6. Using Bob IDE to Fix Issues

This section shows the **exact workflow** for each Bob prompt.

### How to use Bob chat

1. Open `modernization-output-before/bob-prompts.md` in VS Code
2. Copy a prompt block (everything inside the code fences)
3. Paste it into Bob IDE chat
4. Review Bob's plan — read it carefully before approving
5. Approve only when you understand the change
6. Run the analyzer again to verify the fix

### Step-by-step Bob workflow

#### Step A — Understand the codebase (Prompt 1)

Paste Prompt 1 from `bob-prompts.md` into Bob chat.

Bob will:
- Explain what the legacy Spring Boot app does
- Summarize the key files and their purpose
- Rank findings from most to least important
- Tell you which fix to start with

**Do not approve any file changes in this step.** This is analysis only.

#### Step B — Fix SQL injection (Prompt 2)

Paste Prompt 2 into Bob chat.

Bob will propose changes to `UserRepository.java`:
- Replace `String sql = "SELECT..." + username` with `PreparedStatement` or Spring Data JPA
- Keep the method signatures unchanged so no other code breaks
- Explain every file it wants to touch

**Review Bob's diff carefully:**
- ✅ Accept if it uses parameterized queries and only touches the repository
- ❌ Reject if it tries to change Spring Boot version or rewrite multiple classes at once

#### Step C — Add tests (Prompt 3)

Paste Prompt 3 into Bob chat.

Bob will add:
- A test proving the normal case works correctly
- A test proving a SQL injection attempt is safely rejected
- The test will run with the existing Maven test setup

**Verify the test:**
```bash
cd sample-apps/legacy-spring-app
mvn test
```

#### Step D — Improve the analyzer (Prompt 4)

Paste Prompt 4 into Bob chat.

Bob will add new detection rules to the analyzer itself (your project's own code).

#### Step E — Generate final docs (Prompts 5 & 6)

Paste Prompts 5 and 6. Bob will:
- Update the README with a complete hackathon-ready write-up
- Generate a judge summary from the before/after reports

---

## 7. The Full Hackathon Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HACKATHON DEMO LOOP                              │
│                                                                     │
│  1. bmn analyze --repo sample-apps/... --output before              │
│     └─► Opens modernization-report.md + dashboard.html             │
│                                                                     │
│  2. In Bob IDE:                                                     │
│     └─► Paste Prompt 1 → Bob explains the findings                 │
│     └─► Paste Prompt 2 → Bob fixes SQL injection                   │
│     └─► Paste Prompt 3 → Bob adds tests                            │
│                                                                     │
│  3. bmn analyze --repo sample-apps/... --output after               │
│     └─► Finding count drops                                        │
│                                                                     │
│  4. python scripts/compare_runs.py before after                     │
│     └─► Shows measurable improvement table                         │
│                                                                     │
│  5. Paste Prompts 4–6 in Bob → updated docs + judge summary        │
│                                                                     │
│  6. Export Bob task sessions → bob_sessions/                        │
│                                                                     │
│  7. git add . && git commit -m "feat: Bob-assisted modernization"   │
└─────────────────────────────────────────────────────────────────────┘
```

**Your strongest demo story:**
> "The scanner finds issues → Bob explains them → Bob fixes them →
> tests prove the fix → the scanner confirms the improvement."

---

## 8. Exporting Bob Sessions for Judging

> ⚠️ Required. Your submission will not be scored without these files.

### In Bob IDE:

1. Click **"Views and More Actions"** (`···` icon in the top-right of Bob chat)
2. Select **"History"**
3. In the History panel, confirm the workspace is correct
4. Click each task related to your project
5. Click the **task header** — a consumption summary appears showing:
   - Context Length, Task ID, Tokens, Cache, API Cost, Size
6. **Take a screenshot** of this summary
7. Click the **Export icon** (↓) to download the task as a `.md` file
8. Repeat for every task

### Save in your repository:

```
bob_sessions/
  01-repo-analysis-summary.png
  01-repo-analysis-history.md
  02-sql-fix-summary.png
  02-sql-fix-history.md
  03-test-generation-summary.png
  03-test-generation-history.md
  04-readme-generation-summary.png
  04-readme-generation-history.md
```

---

## 9. Bob Prompts Reference (Quick Copy)

See `modernization-output-before/bob-prompts.md` for the full prompts.

| Prompt | Purpose |
|---|---|
| Prompt 1 | Understand the repo, rank findings, get recommended fix order |
| Prompt 2 | Implement safest fix: SQL injection → parameterized queries |
| Prompt 3 | Add unit tests proving the fix works |
| Prompt 4 | Add new detection rules to the analyzer itself |
| Prompt 5 | Generate hackathon-ready README |
| Prompt 6 | Generate judge summary from before/after reports |

---

## Quick Reference: Key Commands

```bash
# Activate virtual environment
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\Activate.ps1         # Windows

# Run the analyzer
bmn analyze --repo sample-apps/legacy-spring-app --output modernization-output-before

# View dashboard (macOS)
open modernization-output-before/dashboard.html

# Re-run after Bob fixes
bmn analyze --repo sample-apps/legacy-spring-app --output modernization-output-after

# Compare before and after
python scripts/compare_runs.py modernization-output-before modernization-output-after

# Commit everything
git add .
git commit -m "feat: Bob-assisted modernization with before/after evidence"
```
