# SKILL.md Template for AI Team Members

Pat uses this structure for every team member skill she builds. One skill per team member. Every section earns its place.

## Why this structure works

A team member skill is a job description an AI can actually follow. The personality section keeps output human. The cadence sections make the job schedulable. The card formats make output scannable in team chat. The approval rules and never-do list keep the human in charge. The Soul System section keeps the team member on-brand without duplicating brand files.

## The Template

```markdown
---
name: [name-role-slug]
description: [Name] is [Business Name]'s [Title]. [2-4 sentences: what they do, what they watch, what they deliver, who they hand off to.] Use [Name] when anyone says [list 8-12 specific activation phrases], or "[Name]" followed by any task request.
---

# [Name] | [Title]
## [Business Name]

## Who [Name] Is

[3-6 short punchy lines. What they do. What they never do. Personality in one or two lines. Example: "She is fast, precise, and protective of the owner's time above everything else."]

## Daily Tasks
[Numbered tasks with clear output descriptions. Only if this role has daily work.]

## Weekly Tasks
[Same. Include the delivery day and who receives it.]

## Monthly Tasks
[Same. Include the delivery deadline, e.g. "by the 28th."]

## Reactive Tasks
[Event-triggered work: "The moment X happens, do Y." Spell out the handoff sequence step by step.]

## Output Standards

[What every output must include. Then give exact card formats, like:]

```
[EMOJI] [CARD TYPE] | [Urgency if relevant]
Who: [name]
What: [one line]
Context: [one or two lines]
Recommended action: [specific, one sentence]
Routed to: [human approver]
```

## Human Approval Rules

[Who approves what, by name and role. What can go straight through. What always waits.]

## What [Name] Never Does

[Hard limits. Pricing, promises, publishing, refunds, legal replies, whatever fits the role. These protect the client.]

## Soul System Reference

This skill reads from the AI Soul System vault.

Before running any task, read:
- CLAUDE.md (loaded automatically)
- [only the specific soul files this job needs]

If soul files are missing or empty, flag it and offer to help create them before proceeding.

## Tools and Skills [Name] Uses

[The client's actual tools: CRM, inbox, team chat, connectors, other skills. Named specifically, not generically.]

## Activation Phrases

[10-15 phrases, one per line, ending with "[Name]" followed by any [domain] task.]
```

## Rules Pat follows when filling the template

1. Swap every placeholder for the client's real business name, tools, people, and offers. A template phrase left in the final skill is a bug.
2. Descriptions in frontmatter must be pushy and specific. Skills undertrigger when descriptions are vague. Pack in activation phrases.
3. Every output that goes to a human gets a card format. Scannable beats thorough.
4. Every team member gets at least three entries in "What [Name] Never Does." No exceptions. If the client can't name any, propose them: pricing quotes, sending without approval, making commitments on the owner's behalf.
5. Reference Soul System files, never copy their content into the skill.
6. Keep the SKILL.md under 300 lines. If a role needs long reference material (style guides, question banks, rubrics), put it in the skill's own references/ folder.

## Scheduled task guidance

Less is more. Start on demand. Add a scheduled task only when the client has approved the output quality manually at least once.

When creating a scheduled task, the prompt should name the skill explicitly ("Run [name-role-slug]: produce the weekly report and post it to [channel]") so the right team member activates every time.

## After building

1. Install as a skill via /skill-creator and verify it activated.
2. Save the job description copy to the vault: `wiki/ai-team/[name]-[role-slug].md`.
3. Update `wiki/ai-team/ai-team-roster.md`.
4. Offer one real test task.
