# Contributing to CocoaBench

Thank you for your interest in contributing to CocoaBench! 🎉

We'd love to have your help in building a diverse and challenging benchmark. The best tasks come from real problems you've encountered — if it challenged you, it'll likely challenge AI agents too! Contributors with **3 accepted tasks** are eligible for co-authorship on the CocoaBench paper, which we plan to submit to a top-tier ML conference. We'll work with you through iterative refinement to help get your tasks accepted and ensure they meet benchmark standards. Particularly interesting or creative tasks may count for more at the discretion of project leads.

This guide will walk you through the process of creating and submitting a new task. Don't worry if it's your first time — we've tried to make it as straightforward as possible.

> 💡 **Quick tip:** Please encrypt your task files before submitting. This keeps our benchmark data safe from being found by LLM agents that can search online, which helps ensure fair evaluation for everyone.


## Quick Start

```bash
cd contrib

# 1. Create your task using the wizard
python create_task.py

# 2. Validate your task
python validate_task.py your-task-name

# 3. Test with an AI agent (Required!)
#    Recommended agents: Gemini 3 Pro, ChatGPT Agent, Claude 4.5
#    Update evaluation.md with results and chat transcript link

# 4. Encrypt before submitting PR
python encrypt_tasks.py --task your-task-name

# 5. Validate encryption
python validate_task.py your-task-name --check-encrypted

# 6. Submit Pull Request
```

---

## What Makes a Good Task?

Great tasks tend to share these qualities:

- 🧩 Require **multi-step solutions** — not just a single lookup
- ✓ Have **clear, verifiable answers** — so we can evaluate automatically
- 🌐 Involve **web browsing, visual perception, or file processing**
- 🔧 Combine **multiple tools** (e.g., search + calculation + code)

Feel free to browse our [example tasks](https://cocoabench.github.io/#examples) for inspiration!

### Things to Keep in Mind

- ❌ Too easy (directly solvable by ChatGPT with searching)
- ❌ Time-sensitive data that will become stale (e.g., the solution relies on a website that will likely update)
- ❌ Subjective or opinion-based answers
- ❌ Impossible to evaluate automatically
- ❌ Require excessive resources or paid APIs

---

## Task Structure

Your contributed tasks will go in the `contributed-tasks/` folder. (The `cocoabench-example-tasks/` folder contains reference examples you can learn from.)

**Before encryption:**
```
contributed-tasks/
└── your-task-name/
    ├── instruction.md        # Task instruction (required)
    ├── evaluation.md         # Evaluation criteria (required)
    ├── solution.md           # Solution walkthrough (required)
    ├── metadata.json         # Task metadata (required)
    ├── Dockerfile            # Container setup (optional)
    ├── docker-compose.yaml   # Docker config (optional)
    └── assets/               # Resource URLs or files (optional)
        └── urls.txt          # URLs to download files
```

**After encryption (ready for PR):**
```
contributed-tasks/
└── your-task-name/
    ├── instruction.md.enc    # Encrypted instruction
    ├── evaluation.md.enc     # Encrypted evaluation
    ├── solution.md.enc       # Encrypted solution
    ├── metadata.json.enc     # Encrypted metadata
    ├── canary.txt            # Encryption key
    ├── Dockerfile            # (unchanged)
    ├── docker-compose.yaml   # (unchanged)
    └── assets/               # (unchanged, e.g., urls.txt)
```

---

## Step-by-Step Guide

Here's a detailed walkthrough of creating your task. Take your time — quality matters more than speed!

### Step 1: Create Your Task Files

All commands should be run from the `contrib/` directory:

```bash
cd contrib
```

**Option A: Use the Task Wizard (Recommended)**
```bash
python create_task.py
```
The wizard will guide you through creating all required files and save them to `contributed-tasks/your-task-name/`.

**Option B: Create files manually**

```bash
mkdir -p ../contributed-tasks/your-task-name
```

Then create these files in your task folder:

- `instruction.md` - Task prompt for the AI agent
- `evaluation.md` - Expected answer and evaluation criteria
- `solution.md` - Step-by-step human solution
- `metadata.json` - Task metadata

See the templates below or check `cocoabench-example-tasks/` for examples.

### Step 2: Validate Your Task

```bash
python validate_task.py your-task-name
```

### Step 3: Test with an AI Agent (Required)

> ⚠️ **Important:** Please test your task with at least one AI agent before submitting.

**Recommended agents:** Gemini 3 Pro, ChatGPT Agent, Claude 4.5

After testing, update `evaluation.md` with the agent's performance and **include a link to the chat transcript**.

### Step 4: Encrypt Your Task

Almost there! Just one more step before submitting — encrypting your task. This keeps our benchmark data safe and ensures fair evaluation for everyone.

```bash
python encrypt_tasks.py --task your-task-name
```

This will:
- Encrypt `instruction.md` → `instruction.md.enc`
- Encrypt `evaluation.md` → `evaluation.md.enc`
- Encrypt `solution.md` → `solution.md.enc`
- Encrypt `metadata.json` → `metadata.json.enc`
- Create `canary.txt`
- Remove the original files

### Step 5: Validate Encryption

```bash
python validate_task.py your-task-name --check-encrypted
```

### Step 6: Submit Pull Request

You're ready to share your work! 🎉

```bash
git checkout -b task/your-task-name
git add contributed-tasks/your-task-name/
git commit -m "Add task: your-task-name"
git push origin task/your-task-name
```

Then open a PR on GitHub. We'd love to hear:
- What your task is about
- What skills it tests
- Any interesting challenges you encountered while creating it

---

## Submitting a Pull Request

Once your task is ready and encrypted:

1. **Fork the repository** (if you haven't already)

2. **Create a new branch** for your task:
   ```bash
   git checkout -b task/<your-task-name>
```

3. **Commit your changes**:
   ```bash
   git add contributed-tasks/<your-task-name>/
   git commit -m "Add task: <your-task-name>"
   ```

4. **Push to your fork**:
   ```bash
   git push origin task/<your-task-name>
   ```

5. **Open a Pull Request** on GitHub with:
   - A clear title: `[New Task] <your-task-name>`
   - Description of what the task tests
   - Confirmation that you've validated and encrypted the task

6. **Wait for review** — we'll take a look and may have some feedback. Thanks for your patience!

---

## Useful Commands

```bash
# Run from the contrib/ directory
cd contrib

# Create a new task interactively
python create_task.py

# Validate a specific task
python validate_task.py <task-name>

# Validate all tasks
python validate_task.py --all

# Encrypt a specific task
python encrypt_tasks.py --task <task-name>

# Encrypt all tasks
python encrypt_tasks.py
```

---

## File Specifications

### 1. `instruction.md` – The Task Prompt

This file contains **only** the task prompt. It should be ready to send directly to an AI agent.

**Rules:**
- ✅ Start directly with the task description
- ✅ Use clear, unambiguous language
- ✅ Include all necessary context and constraints
- ✅ Always end with an **Output Format** section using `<answer>` tags

**Template:**

```markdown
[Task description - clearly explain what the agent should do, 
including all necessary context and constraints]

**Output Format:**

Submit your answer in the following format:

\`\`\`
<answer>your_answer_here</answer>
\`\`\`
```

---

### 2. `evaluation.md` – Evaluation Criteria

Contains the expected answer and initialization resources.

**Template:**

```markdown
# Evaluation for Task [ID]

## Initialization

[Required resources: "Local: assets/", "Host UI: url", or "None"]

## Evaluation Criteria

[The correct answer - exact value, tolerance range, or matching criteria]

## Agent Output Example

[Agent name]: [result], ([Correct/Incorrect], [time])
Chat transcript: [link to chat]
```

> ⚠️ **Required:** Please test with at least one agent (recommended: Gemini 3 Pro, ChatGPT Agent, Claude 4.5) and include the chat transcript link.

**⚠️ Evaluation Criteria Rule:**

The final output of an agent should be easy to evaluate programmatically, ideally as a **simple string or number** that can be verified using a lightweight Python script. This enables reliable automatic evaluation without requiring complex verification logic.

- ✅ Good: `$52.10` or `London` or `{"a": 1, "b": 3}`
- ✅ Good: Numeric with tolerance or string with fuzzy match: `2.8 (±0.1)`
- ❌ Avoid: Open-ended output that require human evaluation
- ❌ Avoid: Tasks that need a very complex evaluation scripts to verify correctness

**Initialization Types:**

| Type | Format |
|------|--------|
| Image file | `Image: https://drive.google.com/file/d/...` |
| Web UI | `Host UI: https://example.com/page` |
| Google Drive folder | `Folder: https://drive.google.com/drive/folders/...` |
| Local files | `Local: assets/` |
| None needed | `None` or `None (web browsing only)` |

**Multiple Resources:**

When a task requires multiple resources, list each on a separate line with clear labels:

```markdown
## Initialization

- Image: https://drive.google.com/file/d/abc123/view
- Data: https://drive.google.com/file/d/xyz789/view
- Host UI: https://example.com/app
```

Or use a structured format:

```markdown
## Initialization

| Resource | URL/Path |
|----------|----------|
| Input Image | https://drive.google.com/file/d/abc123/view |
| Reference Data | https://drive.google.com/file/d/xyz789/view |
| Web Portal | https://example.com/app |
```

---

### 3. `solution.md` – Human Solution Walkthrough

Documents how a human would solve the task step-by-step.

**Template:**

```markdown
# Solution

### Step 1: [Step Title]
[Detailed explanation with sub-steps if needed]

### Final Answer
[The correct answer]
```

---

### 4. `metadata.json` – Task Metadata

**Template:**

```json
{
  "id": 99,
  "name": "your-task-name",
  "brainstorm_by": "Your Name",
  "stage": "Brainstorm",
  "self_checked": "no",
  "reviewers": {},
  "task_properties": {},
  "human_performance": {}
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique task ID (wizard auto-generates) |
| `name` | string | Matches folder name (kebab-case) |
| `brainstorm_by` | string | Your name |
| `stage` | string | `"Brainstorm"` → `"Approved"` (after review) |
| `self_checked` | string | `"yes"` after you've verified the solution |
| `reviewers` | object | Filled by reviewers: `{"reviewer_1_name": "Pass"}` |

---

## Output Format Standards

All tasks must use one of these standardized output formats:

### Simple Answer Tag (Most Common)
```
<answer>value</answer>
```

### Multi-line Answer Tag
```
<answer>
Line 1
Line 2
</answer>
```

### JSON Output
```json
{
  "field": "value"
}
```

### File Output
Specify exact file path and format in the instruction.

---

## Best Practices

1. **Ensure tasks are deterministic** – Same input should always yield same answer
2. **Include clear success criteria** – The answer should be unambiguous
3. **Test your task thoroughly** – Solve it yourself before submission

---

## Review Process

1. **Brainstorm** – Create your task with `"stage": "Brainstorm"`
2. **Self-Check** – Verify solution works, set `"self_checked": "yes"`
3. **Peer Review** – Another contributor validates and adds to `reviewers`
4. **Approval** – After passing review, stage changes to `"Approved"`

---

## Task Categories

Consider which category your task fits:

| Category | Examples |
|----------|----------|
| **Research & Analysis** | Paper analysis, citation networks, genealogy |
| **Visual Perception** | Image recognition, country identification, figure analysis |
| **Web Navigation** | Multi-step web tasks, form filling, data extraction |
| **Data Processing** | CSV analysis, statistical computation, visualization |
| **Reasoning** | Constraint satisfaction, optimization, logical deduction |
| **Domain Knowledge** | Sports, music, pharmaceuticals, AI/ML trends |

---

## Need Help?

We're here to help! Here are some resources:

- 📂 Check existing tasks in `cocoabench-example-tasks/` for reference
- 📖 See `TASKS_WITH_INITIALIZATION.md` for initialization patterns
- 🔍 Run `python validate_task.py --all` to explore how other tasks are structured

If you have questions or run into issues, feel free to open an issue on GitHub. We're happy to help!

Thanks for contributing — we really appreciate it! 🙏

