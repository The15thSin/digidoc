# Software Requirements Specification (SRS)

## For Project: DigiDoc (Web-Based Document Scanner)

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for **DigiDoc**, a cross-platform, responsive web application inspired by ClearScanner. DigiDoc enables users to capture or upload images, automatically detect document edges, enhance visual clarity, manage multi-page documents seamlessly, and export them into optimized PDF files.

### 1.2 Scope

DigiDoc will bridge the gap between mobile scanning apps and desktop document management. It provides a seamless browser-based experience optimized for both mobile touchscreens (for scanning/capturing) and desktop interfaces (for organizing and managing multi-page documents).

### 1.3 Tech Stack Overview

* **Frontend:** ReactJS (Responsive design, HTML5 Canvas/WebGL for interactive cropping).
* **Backend:** Python (FastAPI) for high-performance, asynchronous API routing.
* **Image Processing Engine:** OpenCV / NumPy (integrated into the FastAPI backend).
* **Persistent Database:** PostgreSQL (User data, document metadata, layout states).
* **Blob Storage:** Cloudflare R2 (Object storage for raw uploaded images and final generated PDFs).
* **Authentication:** Google OAuth 2.0.

---

## 2. Overall Description

### 2.1 Product Perspective

DigiDoc operates as a distributed web application. The React frontend handles user interactions and UI-bound image transformations (like UI cropping overlays). The FastAPI backend serves as the heavy-lifting computational engine that handles advanced image processing (edge adjustment, filters) and PDF generation.

```
[React Frontend] <---> [FastAPI Backend] <---> [PostgreSQL] (Metadata)
                              |
                              +--------------> [Cloudflare R2] (Blobs/PDFs)

```

### 2.2 User Classes and Characteristics

* **Unauthenticated Users:** Can view the landing page but must log in to access the scanning workbench, history, or processing features.
* **Registered Users:** Can scan documents, manage multi-page projects, apply enhancements, save history, and export PDFs.

---

## 3. System Features & Functional Requirements

### 3.1 User Authentication & Session Management

* **FR-1.1:** The system shall allow users to log in securely using Google OAuth 2.0.
* **FR-1.2:** The system shall maintain user sessions securely using JWT (JSON Web Tokens) or secure HTTP-only cookies.
* **FR-1.3:** User metadata (Name, Email, Profile Picture) must be persisted in PostgreSQL upon the first login.

### 3.2 Document Ingestion & Edge Detection

* **FR-2.1:** The frontend shall allow users to upload images (JPEG, PNG) from local storage or trigger the device camera via the HTML5 Camera API.
* **FR-2.2:** Upon ingestion, the FastAPI backend (or client-side WASM if optimized) shall automatically compute page boundaries and detect corners using OpenCV (e.g., Canny Edge Detection + Contour Approximation).
* **FR-2.3:** The React frontend shall render an interactive, draggable 4-point polygon overlay on top of the image, allowing the user to manually adjust the detected corners.
* **FR-2.4:** The backend shall perform a Perspective Transform (warping) based on the final 4-point coordinates to output a flat, rectangular document view.

### 3.3 Multi-Page Document Workspace

* **FR-3.1:** The system shall support a "Project/Document" model where a single document can contain multiple pages.
* **FR-3.2:** The UI shall feature a vertical scroll-based workspace or a drag-and-drop thumbnail panel allowing users to reorder pages (moving pages up or down).
* **FR-3.3:** Users shall be able to append new pages to an existing document via camera capture or file upload at any time before final export.
* **FR-3.4:** Users shall be able to delete individual pages within a multi-page document workspace.

### 3.4 Image Enhancement Filters

* **FR-4.1:** The system shall provide visual enhancement filters, including:
* **Original:** Unprocessed warped image.
* **Magic Color/Clear:** Adaptive thresholding/contrast adjustment to make text pop while preserving color details.
* **B&W / Document Mode:** Strict binary or grayscale adaptive thresholding to eliminate shadows and background noise (simulating a clean laser scan).


* **FR-4.2:** Filter applications must be non-destructive during editing; the system should preserve the raw warped image in Cloudflare R2 and apply filters dynamically or preview them on the fly.

### 3.5 Flexible PDF Generation & Variable Compression Export

* **FR-5.1:** The system shall compile the processed pages into a single standard PDF file.
* **FR-5.2:** The system shall offer at least three compression tiers for export:
* **Low (High Quality):** Minimal image compression, optimized for archiving and printing.
* **Medium (Balanced):** Moderate JPEG compression within the PDF container, balanced for email sharing.
* **High (Smallest Size):** Aggressive downscaling and image compression, optimized for web uploads with strict size limits.


* **FR-5.3:** The final generated PDF shall be stored in Cloudflare R2, and a downloadable pre-signed URL shall be delivered to the client.

---

## 4. Non-Functional Requirements

### 4.1 Performance & Scalability

* **FastAPI Asynchrony:** Heavy CPU-bound image processing tasks (OpenCV warping and PDF compilation) should ideally be offloaded to a background task worker (like Celery or FastAPI's native `BackgroundTasks`) to prevent blocking the main event loop.
* **Latency:** Edge detection and preview updates should return a response within < 1.5 seconds under standard network conditions.

### 4.2 UI/UX & Responsiveness

* **Mobile First vs. Desktop Optimized:** * On mobile layouts, the capture and edge-dragging interfaces must support touch gestures (touch targets minimum 48x48px).
* On desktop layouts, the multi-page manager should utilize the expanded screen real estate for a multi-column view (sidebar thumbnails + main preview).



### 4.3 Data Storage & Security

* **Data Isolation:** Users must only be able to view, edit, or delete documents associated with their specific authenticated User ID.
* **Storage Lifespans:** Temporary/incomplete scans can be cleaned up via automated lifecycle policies in Cloudflare R2 if not finalized within 48 hours.

---

## 5. System Architecture & Entity Relationship (Database Design)

### 5.1 Simplified Database Schema (PostgreSQL)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'Untitled Document',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    page_number INT NOT NULL,
    raw_image_url VARCHAR(512) NOT NULL, -- Points to Cloudflare R2
    processed_image_url VARCHAR(512),   -- Points to Cloudflare R2
    corner_coordinates JSONB,            -- Stores {'tl': [x,y], 'tr': [x,y], ...}
    applied_filter VARCHAR(50) DEFAULT 'original',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

---

## 6. Implementation Notes & Technical Recommendations

1. **Optimizing Image Transfers:** To avoid hitting payload size limits on your FastAPI endpoints, consider uploading raw images directly from the React frontend to **Cloudflare R2** via pre-signed URLs, then passing the R2 key to your FastAPI backend for OpenCV processing.
2. **Corner Detection Rendering:** Use a responsive `<canvas>` element in React to handle the edge-detection overlay. When resizing from desktop to phone, map the normalized coordinates (percentages ranging from `0.0` to `1.0`) instead of absolute pixel values, ensuring the crop box scales perfectly across device breakpoints.
3. **PDF Compilation:** Use libraries like `reportlab` or `img2pdf` in your Python backend. `img2pdf` is highly recommended because it packs images into a PDF wrapper without re-encoding them unnecessarily, making compression control predictable.
