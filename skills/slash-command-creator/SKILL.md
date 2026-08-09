---
name: slash-command-creator
description: Claude Code 슬래시 커맨드 저작 도구. 새 커맨드 작성, 기존 커맨드 수정, frontmatter 옵션(allowed-tools, argument-hint, disable-model-invocation 등) 문의에 사용. "커맨드 만들어줘", "슬래시 커맨드 작성", "command 생성" 요청에 반응. 커맨드는 정의상 user-invoked이며 다른 커맨드를 호출하지 않는다(절차 참조로 해결).
metadata:
  invocation: user-invoked
---

> **호출 계층: user-invoked** — 사용자가 직접 호출했거나 명시적으로 요청했을 때만 실행한다. 다른 user-invoked 스킬/커맨드를 호출하지 않는다.

# Slash Command Creator

Create custom slash commands for Claude Code to automate frequently-used prompts.

## Quick Start

Initialize a new command:
```bash
scripts/init_command.py <command-name> [--scope project|personal]
```

## Command Structure

Slash commands are Markdown files with optional YAML frontmatter:

```markdown
---
description: Brief description shown in /help
---

Your prompt instructions here.

$ARGUMENTS
```

### File Locations

| Scope    | Path                    | Shown as           |
|----------|-------------------------|-------------------|
| Project  | `.claude/commands/`     | (project)         |
| Personal | `~/.claude/commands/`   | (user)            |

### Namespacing

Organize commands in subdirectories:
- `.claude/commands/frontend/component.md` → `/component` shows "(project:frontend)"
- `~/.claude/commands/backend/api.md` → `/api` shows "(user:backend)"

## Features

### Arguments

**All arguments** - `$ARGUMENTS`:
```markdown
Fix issue #$ARGUMENTS following our coding standards
# /fix-issue 123 → "Fix issue #123 following..."
```

**Positional** - `$1`, `$2`, etc.:
```markdown
Review PR #$1 with priority $2
# /review 456 high → "Review PR #456 with priority high"
```

### Bash Execution

Execute shell commands with `!` prefix (requires `allowed-tools` in frontmatter):

```markdown
---
allowed-tools: Bash(git status:*), Bash(git diff:*)
---

Current status: !`git status`
Changes: !`git diff HEAD`
```

### File References

Include file contents with `@` prefix:

```markdown
Review @src/utils/helpers.js for issues.
Compare @$1 with @$2.
```

## Frontmatter Options

| Field                     | Purpose                                | Required |
|---------------------------|----------------------------------------|----------|
| `description`             | Brief description for /help            | Yes      |
| `allowed-tools`           | Tools the command can use              | No       |
| `argument-hint`           | Expected arguments hint                | No       |
| `model`                   | Specific model to use                  | No       |
| `disable-model-invocation`| Prevent SlashCommand tool invocation   | No       |

See [references/frontmatter.md](references/frontmatter.md) for detailed reference.

## 호출 계층 (이 저장소 규약)

**커맨드는 정의상 전부 user-invoked다.** 사용자가 타이핑해야 실행되는 것이 슬래시 커맨드의 존재 이유이므로 별도 표기를 하지 않는다. 전문: `docs/skill-invocation-tiers.md`

따라야 할 규칙:

- 커맨드는 다른 커맨드나 user-invoked 스킬을 **호출하지 않는다.**
- 다만 **절차를 복제하지도 않는다.** 같은 절차가 필요하면 원본 파일을 지정해 "그 파일을 읽고 그대로 수행하라"고 쓴다(절차 참조). 복제본은 원본이 바뀔 때 조용히 갈라진다. (`/dev-cycle`이 `~/.claude/commands/jira/start.md`의 단계 0~2를 읽어 스스로 수행하는 방식)
- 에이전트가 필요하면 Agent 도구로 직접 호출한다.
- model-invoked 스킬(`tdd-workflow`, `quality-gate`)은 자유롭게 끌어다 쓸 수 있다.

예외적으로 모델이 자유롭게 불러도 되는 커맨드만 명시적으로 opt-out 한다.

```yaml
metadata:
  invocation: model-invoked
```

모델이 절대 못 부르게 하드 차단하려면 네이티브 필드를 쓴다. 단 자연어 요청까지 막히므로 사용자가 매번 슬래시 커맨드를 타이핑해야 한다.

```yaml
disable-model-invocation: true
```

## Examples

See [references/examples.md](references/examples.md) for complete examples including:
- Simple review/explain commands
- Commands with positional arguments
- Git workflow commands with bash execution
- Namespaced commands for frontend/backend

## Creation Workflow

1. **Identify the use case**: What prompt do you repeat often?
2. **Choose scope**: Project (shared) or personal (private)?
3. **Initialize**: Run `scripts/init_command.py <name>`
4. **Edit**: Update description and body
5. **Test**: Run the command in Claude Code
