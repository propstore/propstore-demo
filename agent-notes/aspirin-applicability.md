# Aspirin applicability demo publication

## Goal and state
Publish the reviewed disposable demonstration in propstore/propstore-demo.
The public repository starts from a clean root containing the demo, README,
output evidence, ignore rules and this task note. Earlier local review history
is preserved separately and is not part of this repository's history.

## Decisions
- Keep the reviewed demo.py implementation unchanged.
- Pin published Propstore commit d62a9736cd47e4c952ff34622a6257fc79bec257
  from draft PR https://github.com/propstore/propstore/pull/311.
- That owner fix remains unmerged at initial publication.
- Install the owner's locked dependencies into a fresh checkout environment.
- Preserve the paper report separately from reviewer modelling assumptions.
- The runner creates only a disposable store and checks actual argument output.
- One challenged licence is demonstrated; generic targeting remains separate.

## Evidence and next step
The owner integration includes merged #307/#308/#309/#310. Its full suite passed
1896 tests with one skip; the equation/justification interaction passed both
render policies, and all nine demo transitions passed.
Fresh GitHub owner clone at the pinned commit and locked setup succeeded:
53 packages were installed into its own new environment using CPython 3.13.5
and uv 0.8.8. Import assertions confirmed that Propstore came from that clone
and Quire/argumentation came from its environment, with user-site imports
excluded. All nine demo transitions passed with exit 0. run-output.txt records
that execution. The clean owner checkout remained unchanged.

The reviewed demo.py blob remains 9451134db218e67cd6b0ae496419ab12b362ab7d.
Keep the owner and plugin PRs as drafts and retain the exact published dependency
pin while the owner fix is under review.
