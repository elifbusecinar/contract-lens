# Sample project API (documentation drift demo)

This document intentionally diverges from `ProjectsController.cs` and the frontend client so ContractLens can surface **documentation drift**.

## Upload

Call **`POST /api/projects/upload`** with multipart field `file`.

Example JSON response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "thumbnailUrl": "https://cdn.example/thumb.png"
}
```

## Local frontend

From the `frontend/` directory run:

```text
npm run dev
```

(This sample `package.json` does not define a `dev` script—docs are stale on purpose.)
