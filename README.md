# DigiDoc 📄🚀

DigiDoc is a feature-rich, responsive web-based document scanner application inspired by the mobile ClearScanner app. It bridges the gap between phone scanning conveniences and powerful web interfaces, optimized seamlessly for both mobile touchscreens and desktop viewports. 

Users can capture or upload images, auto-detect document edges via computer vision, apply high-quality scanning filters, manage multi-page layout orders, and export finalized PDFs using granular compression layers.

---

## ✨ Features

- **Smart Ingestion:** Snap direct photos via the HTML5 Camera API or drop local files (`JPEG`, `PNG`).
- **Auto Edge & Corner Detection:** Intelligent computer vision overlays that snap straight onto the document boundaries with adjustable 4-point manual correction.
- **Interactive Multi-Page Management:** Drag, drop, and scroll intuitively to reorder, append, or delete individual pages seamlessly inside a unified document context.
- **Clarity Enhancements:** Premium custom-tailored OpenCV non-destructive adjustments (Original, Magic Color, Crisp B&W, Laser Scan Simulator).
- **Flexible PDF Compressions:** Variable-size export options tailored for high-fidelity archival prints, standard emails, or size-constrained web portals.

---

## 🛠️ Tech Stack

- **Frontend:** ReactJS + Vite + TailwindCSS (or modular styles), HTML5 Canvas/WebGL for interactive warping matrices.
- **Backend:** Python (FastAPI framework) utilizing asynchronous background tasks for intensive processing.
- **Image Processing Engine:** OpenCV (`opencv-python-headless`) + NumPy.
- **Database Engine:** PostgreSQL (Handles authentication mappings and page serialization state).
- **Blob Engine:** Cloudflare R2 object storage (Low-latency ingestion uploads and pre-signed output delivery).
- **Dependency Management:** `uv` (Fast Python packaging) + `npm`.
- **Identity Provider:** Google OAuth 2.0.

---

## 📂 Project Architecture & Structure

```text
.
├── SRS.md                         # Detailed Software Requirements Specifications
├── backend                        # FastAPI computational engine
└── frontend
    └── digidoc-app                # Modern React Client application
```
---

## ⚡ Quick Start & Local Setup

### Prerequisites

Ensure you have the following installed locally:

* Python 3.11+ (and `uv` package manager)
* Node.js (v18+) & `npm`
* PostgreSQL instance running

### 1. Environment Configurations

Create an `.env` file in the root of the `/backend` directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/digidoc
```

### 2. Backend Bootstrapping (FastAPI)

Using `uv` for modern, blindingly fast dependency coordination:

```bash
# Navigate to backend workspace
cd backend

# Synchronize virtual environment dependencies using uv
uv sync

# Fire up the asynchronous development backend
uv run uvicorn src.app.main:app --reload --port 8000

```

Your OpenAPI interactive documentation page will go live immediately at `http://localhost:8000/docs`.

### 3. Frontend Bootstrapping (React + Vite)

```bash
# Navigate to frontend workspace
cd frontend/digidoc-app

# Install client-side node assets
npm install

# Initialize responsive engine development preview
npm run dev

```

Open up your local development browser view at `http://localhost:5173`.

---

## ⚙️ Core Processing Workflows

1. **Direct Cloud Ingestion Optimization:** To maximize throughput, the React layout negotiates direct upload agreements directly to **Cloudflare R2** via pre-signed uniform resource tokens.
2. **Normalized Poly Coordinate Conversions:** The client canvas framework serializes boundary coordinates mapping scales from `0.0` to `1.0` (relative percentages). This avoids frame-rate breakage when editing a large raw phone photograph on a small browser viewport size.
3. **Lossless Document Assemblies:** Finalization structures leverage internal Python libraries (such as `img2pdf`) to bind transformed document assets natively without introducing secondary compression layers until specified by user quality sliders.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

```

```