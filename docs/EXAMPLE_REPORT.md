# Example mismatch excerpt

After running the main demo, open `contractlens-reports/contractlens-report-create-project-upload-file.md`.

You should see mismatches along these lines:

- Path drift: frontend **`/api/projects/{id}/files`** vs backend **`/api/projects/{projectId}/models`**
- Fields: frontend **`id`** / **`thumbnailUrl`** vs backend **`projectId`** / **`thumbnail_path`**
- Detail: frontend **`name`** vs backend **`title`** (plus **`created_at`** naming drift vs typical camelCase expectations)

Full traces for MCP, LangGraph, and the deterministic agent layer are embedded in the report.
