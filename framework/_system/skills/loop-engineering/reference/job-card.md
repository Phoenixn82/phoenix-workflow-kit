# The job card (write this before building any loop)

Owain's governance card. Don't start by copying labels or tools — start with the job. The
**FORBIDDEN** list and the **EVALUATION** line are the load-bearing parts: if you can't answer
"how would I know the agent did this job well?", you're not ready to run it autonomously.

```
JOB:        what does this agent own?
INPUTS:     what does it inspect?
ALLOWED:    what may it change?
FORBIDDEN:  what must it never do?
OUTPUT:     what exists after a good run?
EVALUATION: how do I know it did well?
```

## Filled example — the manager loop

```
JOB:        keep the agentic-os-97 backlog classified, routed, and safe to hand to agents.
INPUTS:     open issues, labels, comments, linked PRs, board state, repo docs.
ALLOWED:    create the 11 managed labels; add risk/type/agent labels (gaps only); Agent
            Assessment comments; evidence-backed maintenance issues; status sync from merged PRs.
FORBIDDEN:  writing code; opening/merging PRs; speculative tickets; marking medium/high-risk work
            agent:ready; removing existing managed labels; deleting branches; spending past budget.
OUTPUT:     a clean, labelled, risk-classified queue + an inspectable Agent Assessment per issue.
EVALUATION: risky work stays away from agents; vague work gets a specific needs:human question;
            agent:ready only on low-risk, clear, verifiable tickets; no speculative noise.
```

A loop whose card you can't fill is not ready to run unattended. Start with the manager loop
alone — even if no agent ever writes code, a self-maintaining risk-classified backlog is worth it.
