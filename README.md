# DigiDoc

DigiDoc is a FastAPI + React document scanning project.

## Current

What is implemented right now:

- Image upload in the React client.
- Corner detection for uploaded images.
- Base64 image-to-PDF conversion in the backend.
- A FastAPI API with `/scan` and `/corners` endpoints.
- Local development startup through `main.py`.
- Docker Compose for running the backend and frontend together.

## Planned

These are described in the original product direction, but are not fully implemented in the current codebase:

- Multi-page document management.
- Manual corner correction and page reordering.
- Scan enhancement modes such as B&W and color filters.
- Cloud storage integration.
- Authentication and account management.
- Database-backed document persistence.
- Production PDF export workflows.

## Architecture

```text
.
├── backend
│   └── src/app
│       ├── api
│       ├── config
│       ├── controllers
│       ├── models
│       ├── services
│       └── utils
├── frontend/digidoc-app
└── docker-compose.yml
```

### Backend

- FastAPI app entrypoint: `backend/src/app/main.py`
- API routes: `backend/src/app/api/routes.py`
- Request and response models: `backend/src/app/models`
- Image processing services: `backend/src/app/services`

### Frontend

- Vite + React app in `frontend/digidoc-app`
- Main UI entrypoint: `frontend/digidoc-app/src/App.jsx`
- Global bootstrapping: `frontend/digidoc-app/src/main.jsx`

## Local Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- `uv` and `npm`

### Backend

From `backend/`:

```bash
uv sync
ENV=dev PYTHONPATH=src uv run python src/app/main.py
```

The backend exposes:

- API: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`

### Frontend

From `frontend/digidoc-app/`:

```bash
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

### Docker Compose

Start both services from the repository root:

```bash
docker compose up --build
```

This brings up:

- Backend on `http://localhost:8000`
- Frontend on `http://localhost:5173`

## Notes

- The frontend reads its API base from `VITE_API_BASE_URL`.
- The backend config is selected with `ENV` (`dev` or `prod`).
- The current backend script entrypoint works, but it is still a temporary launch style until the project is standardized around a direct Uvicorn command.
