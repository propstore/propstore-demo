# A reported result and its applicability

Does a reported result supply support in another context under an explicit
reviewer-authored transport assumption? What changes when that assumption or
the inference is challenged?

This is a knowledge-representation example. The paper-derived assertion
summarizes the web appendix to the
[ATT Collaboration's 2009 Lancet article](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736%2809%2960503-1/fulltext),
printed page 21, Web Figure 18. The original page image was checked. No papers
are included. The context bridge, transport permission, applicability inference
and scope objection are reviewer modelling assertions, not clinical findings
or patient advice. The example gives no numerical confidence or treatment
recommendation.

## Run

Prerequisites: Git, Python 3.13 and uv.

The required owner fix is under review in
[Propstore draft PR #311](https://github.com/propstore/propstore/pull/311).
Setup pins the published commit
[`d62a9736cd47e4c952ff34622a6257fc79bec257`](https://github.com/propstore/propstore/commit/d62a9736cd47e4c952ff34622a6257fc79bec257).
That fix remains unmerged at this demo's initial publication.

From a parent directory:

```powershell
git clone https://github.com/propstore/propstore.git
git -C propstore checkout --detach d62a9736cd47e4c952ff34622a6257fc79bec257
uv sync --project propstore --locked --no-dev --python 3.13
git clone https://github.com/propstore/propstore-demo.git
uv run --no-sync --project propstore python propstore-demo/demo.py
```

The locked setup installs dependencies into the new Propstore checkout's
environment. The runner authors and promotes a source excerpt into a temporary
repository, computes ASPIC arguments under grounded semantics, merges a reviewer
branch, prints every result and removes its temporary store.

## Observable answer

Assertions check these computed changes:

| Change | Historical report | Applicability inference |
| --- | --- | --- |
| Original ATT context | accepted | inactive |
| Explicit target context bridge | accepted | accepted |
| Unrelated context | inactive | inactive |
| Withdraw transport permission | accepted | unsupported |
| Withdraw report | inactive | unsupported |
| Merge reviewer objection | accepted | defeated |
| Withdraw objection hypothetically | accepted | accepted |
| Return to the stored base after that hypothetical | accepted | defeated |

Printed dependencies come from the engine's argument tree. Propstore preserves
the source report, inference licence, contextual scope and rival reviewer
assertion while changing the rendered answer. Withdrawing evidence removes the
support it supplied; a hypothetical query leaves the stored base intact.

Successful execution ends with `All transitions verified against computed
arguments.` and exit code 0. [run-output.txt](run-output.txt) records an execution.
Repeated fresh-store runs produced the same states, dependencies and promoted
report ID. Git merge commit IDs vary with commit timestamps.

The example has exactly one challenged inference licence. It does not
demonstrate generic targeting among multiple licences, migrate the historical
aspirin corpus or evaluate net clinical benefit.
