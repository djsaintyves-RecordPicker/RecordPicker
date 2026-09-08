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

## Isolated recheck, 8 September at 21:10 UTC

The application's deployed-endpoint validator still reports an expired feed
(`/tmp/rp25-today-pick-endpoint-2306.log`). A fresh editorial-only diagnostic
is running on this isolated branch, bounded to 20 minutes, with the original
minimum of six contributing publishers. Artist verification is still enabled;
only the separate release, live-event, anniversary and credentialed concert
providers are excluded from this diagnostic. It cannot qualify a production
feed on its own and does not publish anything.

Output directory: `/tmp/rp25-editorial-recovery.mAHsRQ`.
Run log: `/tmp/rp25-editorial-recovery-live.log`. Result: rejected, exit 2;
only two fresh contributing publishers, below the unchanged requirement of six.
No candidate feed was written and no production file was changed.

The failed run exposed a diagnostic gap: per-source health and lookup warnings
were discarded by the source gate. Health is now written to its separate path
before that gate, with explicit required/effective counts and a source-gate
result. Warnings are printed on rejection as well. Feed/editorial/health output
paths must differ, preventing diagnostics from overwriting the feed. Three new
offline tests cover failed-feed preservation, success and output aliases;
all ten tests on this isolated branch pass. Still not deployed.
