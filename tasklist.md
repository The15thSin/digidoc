# DigiDoc Task List

This task list is derived from `README.md` and `SRS.md`. It is grouped by implementation area so backend, frontend, database, and DevOps work can be planned independently.

## Current Baseline

- [x] Set up FastAPI backend structure.
- [x] Set up Vite + React frontend structure.
- [x] Implement image upload in the React client.
- [x] Implement backend `/scan` endpoint for base64 image-to-PDF conversion.
- [x] Implement backend `/corners` endpoint for corner detection.
- [x] Add local backend startup through `main.py`.
- [x] Add Docker Compose support for backend and frontend.

## Backend

- [ ] Standardize backend startup around a direct Uvicorn command.
- [ ] Document expected request and response payloads for scanner endpoints.
- [ ] Support JPEG and PNG image ingestion.
- [ ] Automatically compute page boundaries and detect corners with OpenCV.
- [ ] Accept final 4-point crop coordinates from the frontend.
- [ ] Perform perspective transform/warping from final crop coordinates.
- [ ] Return a warped rectangular document preview.
- [ ] Add original/unprocessed filter mode.
- [ ] Add Magic Color/Clear enhancement using contrast or adaptive thresholding.
- [ ] Add B&W / Document Mode enhancement for clean grayscale or binary scans.
- [ ] Apply selected page filters consistently during PDF export.
- [ ] Compile multiple processed pages into a single PDF.
- [ ] Add Low compression export for high-quality archival output.
- [ ] Add Medium compression export for balanced sharing.
- [ ] Add High compression export for smallest file size.
- [ ] Evaluate `img2pdf` or `reportlab` for predictable PDF generation.
- [ ] Return a downloadable PDF response or URL to the client.
- [ ] Add Google OAuth 2.0 backend integration.
- [ ] Implement secure session management with JWT or HTTP-only cookies.
- [ ] Add logout/session invalidation support.
- [ ] Measure edge detection latency for typical mobile image sizes.
- [ ] Keep edge detection and preview responses under the SRS target of 1.5 seconds where practical.
- [ ] Offload CPU-bound image processing from the main FastAPI event loop.
- [ ] Evaluate FastAPI `BackgroundTasks`, Celery, or a worker queue for PDF generation.
- [ ] Add image size limits or downscaling before expensive processing.
- [ ] Add structured logging around scan and export jobs.

## Frontend

- [ ] Confirm frontend `VITE_API_BASE_URL` handling in local and Docker workflows.
- [ ] Support JPEG and PNG uploads from local storage.
- [ ] Add camera capture support through browser camera APIs.
- [ ] Introduce a document/project model in client state.
- [ ] Allow a single document to contain multiple pages.
- [ ] Append new pages to an existing document via upload.
- [ ] Append new pages to an existing document via camera capture.
- [ ] Normalize detected corner coordinates so they scale across screen sizes.
- [ ] Render a responsive image preview with a 4-point crop polygon overlay.
- [ ] Make crop polygon handles draggable with mouse input.
- [ ] Make crop polygon handles touch-friendly on mobile with minimum 48x48px targets.
- [ ] Submit final corner coordinates to the backend for perspective correction.
- [ ] Display warped document previews returned by the backend.
- [ ] Display page thumbnails in a sidebar or vertical workspace.
- [ ] Support page reordering.
- [ ] Support deleting individual pages.
- [ ] Keep page order stable through editing and export.
- [ ] Preview filters without destroying the raw warped image.
- [ ] Store the selected filter per page in UI state.
- [ ] Add PDF export controls with compression tier selection.
- [ ] Add export error states.
- [ ] Add progress or loading states for long-running exports.
- [ ] Gate scanning workbench access behind authentication.
- [ ] Gate document history access behind authentication.
- [ ] Add Google login and logout UI.
- [ ] Build a mobile-first scanning flow.
- [ ] Build a desktop-optimized document management layout.
- [ ] Use a sidebar thumbnail layout on wider screens.
- [ ] Ensure crop editing works across mobile and desktop breakpoints.
- [ ] Add clear empty states for new documents.
- [ ] Add clear failure states for upload, detection, processing, and export errors.
- [ ] Verify text and controls do not overlap on small screens.

## Database

- [ ] Add PostgreSQL database configuration.
- [ ] Add migrations for database schema changes.
- [ ] Create `users` table.
- [ ] Store user Google ID, email, name, and profile picture metadata.
- [ ] Create `documents` table.
- [ ] Store document title, owner, creation time, and update time.
- [ ] Create `pages` table.
- [ ] Store page order for multi-page documents.
- [ ] Persist raw image storage references per page.
- [ ] Persist processed image storage references per page.
- [ ] Persist corner coordinates as structured JSON data.
- [ ] Persist selected filter per page.
- [ ] Persist final generated PDF metadata.
- [ ] Add update timestamp handling for documents.
- [ ] Add cascade delete behavior for user documents and document pages.

## Storage

- [ ] Add Cloudflare R2 configuration.
- [ ] Store raw uploaded images in R2.
- [ ] Store processed images in R2.
- [ ] Store final generated PDFs in R2.
- [ ] Generate pre-signed URLs for direct uploads where useful.
- [ ] Generate pre-signed URLs for PDF downloads.
- [ ] Avoid exposing long-lived R2 object URLs.
- [ ] Add cleanup policy or job for unfinished scans older than 48 hours.

## Security

- [ ] Ensure users can only access documents belonging to their own user ID.
- [ ] Validate all document operations against authenticated ownership.
- [ ] Validate all page operations against authenticated ownership.
- [ ] Validate all export operations against authenticated ownership.
- [ ] Validate uploaded file type and size.
- [ ] Avoid trusting client-provided storage keys without ownership checks.
- [ ] Review CORS configuration for local and production environments.
- [ ] Store session tokens or cookies securely.
- [ ] Protect authenticated routes from unauthenticated access.

## DevOps

- [ ] Confirm backend environment loading for `dev` and `prod`.
- [ ] Review Docker Compose configuration for backend, frontend, database, and storage dependencies.
- [ ] Add PostgreSQL service to local Docker Compose if needed.
- [ ] Add environment variable documentation for backend, frontend, database, OAuth, and R2.
- [ ] Add production Docker configuration review.
- [ ] Add deployment environment documentation.
- [ ] Add observability for processing failures and export failures.
- [ ] Add lifecycle or scheduled cleanup execution for stale temporary scans.