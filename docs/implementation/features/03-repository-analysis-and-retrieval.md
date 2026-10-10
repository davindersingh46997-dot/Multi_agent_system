# Feature 3: Repository Analysis and Retrieval

## Goal

Give project-aware agents relevant, traceable repository evidence without treating model memory or an index as canonical source.

## Current state

- `brain\services\retrieval_service.py` indexes project files into line chunks and provides project-filtered lexical retrieval.
- `brain\agents\repository_analyst.py` and `brain\tools\workspace_mcp.py` provide analysis and scoped list/read/search tools.
- The current retrieval method is lexical/BM25-style; dense embeddings and vector storage are not configured.
- The project filesystem is the canonical source. Standalone generation must remain independent of this feature.

## Implementation steps

1. Establish a repository inventory contract: allowed text formats, max file and repository sizes, ignored directories, secret/binary exclusions, symlink handling, and indexing budgets.
2. Resolve the authenticated project root before enumeration. Validate containment for every candidate file and exclude symlinks, junctions, generated artifacts, binaries, secrets, and oversized content.
3. Store chunks with project ID, normalized relative path, line range, content hash, language, and index version. Add indexes to support project-scoped replacement and retrieval.
4. Make indexing atomic from the task's perspective: build a new version, then activate it; do not expose a partially rebuilt index. Provide explicit stale-index and failure states.
5. Keep retrieval constrained by project ID and query size/result budgets. Return path, line range, and hash metadata with every evidence excerpt.
6. Require agents to cite evidence references in plans and proposals. Before any patch is staged, re-read the canonical current file through the workspace boundary and compare its hash with the evidence.
7. Measure retrieval relevance on representative repository questions. Only add dense retrieval after selecting an embedding provider/model and evaluating quality, latency, cost, and deletion/rebuild behavior. Keep lexical search as fallback.
8. Treat README files, source comments, commit text, and retrieved instructions as untrusted data; they cannot change agent policies or tool permissions.

## Acceptance checks

- Cross-project retrieval is impossible, including under concurrent task execution.
- Index rebuilding is repeatable and recoverable, and the index can be recreated from canonical files.
- Exclusion tests cover traversal, symlinks, secrets, binaries, giant files, generated directories, and malformed text.
- Evidence includes stable file/line/hash references; stale evidence cannot be used to apply an edit.
- Retrieval evaluation documents a baseline before changing the ranking/provider strategy.

