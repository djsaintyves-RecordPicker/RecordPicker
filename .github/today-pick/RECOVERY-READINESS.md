# Today Pick resolver recovery — 2026-09-08

This branch is isolated from existing uncommitted editorial-summary and site
work. No production feed, freshness threshold, identity score or six-publisher
requirement is changed.

Confirmed defects corrected:

- A temporary lookup failure disabled artist verification for the entire run.
  The circuit now permits at most two recovery probes, spaced by at least
  60 seconds. Each HTTP lookup keeps its existing bounded retries and rate limit.
- Previously verified artist names became inaccessible during an outage.
  Verified in-memory results remain usable; no identity is fabricated.
- A headline examined during an outage could be permanently cached as having
  no artist. Incomplete headline results are no longer cached as definitive.

Five new offline tests cover recovery, sustained-outage request limits, use of
verified results, rejection of nonmatching artists and retry of interrupted
headlines. Seven tests pass on this isolated branch (two existing plus five new).

Live diagnostics: a direct Radiohead lookup succeeded, but a full editorial
pass downloaded recent articles from 46 publishers without a verified event.
A subsequent BBC-only pass yielded one event then HTTP 503. These observations
show intermittent identity-service failure, not a restored production feed.
The live passes were made in the original worktree with its existing summary
changes and the recovery patch; the isolated branch has only offline proof.

Not deployed. The published feed must still be renewed by a fully validated
production run; do not extend expired dates or lower the source threshold.
