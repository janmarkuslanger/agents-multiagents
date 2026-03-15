# Extensions

Project-specific add-ons that extend a base configuration.

An extension is a markdown file that gets appended to the base `AGENTS.md`
system prompt for a specific project or domain context.

## Usage

Append an extension to your agent system prompt:

```python
base   = Path("agents/architect.md").read_text()
extra  = Path("agents/extensions/my-extension.md").read_text()
system = base + "\n\n---\n\n" + extra
```

Or reference it at the bottom of your project's `AGENTS.md`:

```markdown
## Project-specific rules
See `agents/extensions/my-extension.md`.
```

## Creating an extension

Create a new `.md` file in this folder. Name it after the domain or project.
Only include rules that are genuinely specific to that context — rules that
belong to all projects go in `simple/` or `multiagent/` instead.
