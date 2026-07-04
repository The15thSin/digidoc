import { useState, useRef, useCallback } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "https://digidoc-backend-api.onrender.com";

const CORNER_LABELS = ["Top-left", "Top-right", "Bottom-right", "Bottom-left"];

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ── Icons ──────────────────────────────────────
const IconScan = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="4 7 4 4 7 4" /><polyline points="17 4 20 4 20 7" />
    <polyline points="20 17 20 20 17 20" /><polyline points="7 20 4 20 4 17" />
    <rect x="8" y="8" width="8" height="8" rx="1" />
  </svg>
);

const IconUpload = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const IconFile = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
);

const IconX = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

const IconResult = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
    <line x1="8" y1="11" x2="14" y2="11" /><line x1="11" y1="8" x2="11" y2="14" />
  </svg>
);

const IconAlert = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

const IconCheck = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

// ── App ────────────────────────────────────────
export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragover, setDragover] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // { overlayB64, corners }
  const [error, setError] = useState(null);
  const inputRef = useRef(null);
  const resultImgRef = useRef(null);
  const [imgSize, setImgSize] = useState({ w: 0, h: 0 });

  const handleFile = useCallback((f) => {
    if (!f || !f.type.startsWith("image/")) {
      setError("Only image files are supported.");
      return;
    }
    setFile(f);
    setPreviewUrl(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }, []);

  const onInputChange = (e) => {
    const f = e.target.files[0];
    if (f) handleFile(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragover(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const onClear = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const onDetect = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const imageData = await fileToBase64(file);
      const res = await fetch(`${API_BASE}/digidoc/api/v1/corners`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_data: imageData }),
      });

      if (!res.ok) {
        const msg = await res.text().catch(() => `HTTP ${res.status}`);
        throw new Error(msg || `Server returned ${res.status}`);
      }

      const data = await res.json();
      // Expected: { overlay_image: "<base64>", corners: [[x,y], [x,y], [x,y], [x,y]] }
      setResult({
        overlayB64: data.overlay_img_base64,
        corners: data.corners,
      });
    } catch (err) {
      setError(err.message || "Detection failed. Is the server running?");
    } finally {
      setLoading(false);
    }
  };

  const onResultImgLoad = () => {
    if (resultImgRef.current) {
      setImgSize({
        w: resultImgRef.current.naturalWidth,
        h: resultImgRef.current.naturalHeight,
      });
    }
  };

  // Convert absolute pixel coords → percentage positions relative to the displayed image
  const pinPosition = (x, y) => {
    if (!imgSize.w || !imgSize.h) return { left: "0%", top: "0%" };
    return {
      left: `${(x / imgSize.w) * 100}%`,
      top: `${(y / imgSize.h) * 100}%`,
    };
  };

  return (
    <div className="app-shell">
      {/* ── Topbar ── */}
      <header className="topbar">
        <div className="topbar-logo">
          <div className="logo-icon">
            <IconScan />
          </div>
          <span className="logo-name">Digi<span>Doc</span></span>
        </div>
        <span className="topbar-badge">BETA</span>
        <div className="topbar-spacer" />
        <div className="topbar-status">
          <div className={`status-dot ${result ? "live" : ""}`} />
          {result ? "corners detected" : "awaiting scan"}
        </div>
      </header>

      {/* ── Workspace ── */}
      <main className="workspace">

        {/* Left: Input panel */}
        <section className="panel">
          <div className="panel-header">
            <span className="panel-label">Input</span>
          </div>
          <div className="panel-body">

            {/* Drop zone */}
            <div
              className={`upload-zone ${dragover ? "dragover" : ""} ${file ? "has-image" : ""}`}
              onClick={() => !file && inputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
              onDragLeave={() => setDragover(false)}
              onDrop={onDrop}
            >
              {file ? (
                <>
                  <img src={previewUrl} alt="Preview" className="preview-img" />
                  <button className="clear-btn" onClick={(e) => { e.stopPropagation(); onClear(); }} title="Remove image">
                    <IconX />
                  </button>
                </>
              ) : (
                <>
                  <div className="upload-icon"><IconUpload /></div>
                  <div className="upload-text">
                    <strong>Drop an image here</strong>
                    <span>or click to browse &mdash; JPG, PNG, WEBP</span>
                  </div>
                </>
              )}
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={onInputChange}
              />
            </div>

            {/* File meta */}
            {file && (
              <div className="file-meta">
                <IconFile />
                <span className="file-meta-name">{file.name}</span>
                <span className="file-meta-size">{formatBytes(file.size)}</span>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="error-banner">
                <IconAlert />
                <span>{error}</span>
              </div>
            )}

            {/* CTA */}
            <button
              className={`detect-btn ${loading ? "loading" : ""}`}
              onClick={onDetect}
              disabled={!file || loading}
            >
              {loading ? (
                <>
                  <div className="spinner" />
                  Detecting corners…
                </>
              ) : (
                <>
                  <IconScan />
                  Detect Corners
                </>
              )}
            </button>

          </div>
        </section>

        {/* Right: Result panel */}
        <section className="panel">
          <div className="panel-header">
            <span className="panel-label-accent">Result</span>
          </div>
          <div className="panel-body">
            {!result ? (
              <div className="result-empty">
                <div className="result-empty-icon"><IconResult /></div>
                <p>overlay will appear here</p>
              </div>
            ) : (
              <>
                <div className="success-strip">
                  <IconCheck />
                  4 corners detected successfully
                </div>

                {/* Overlay image with animated corner pins */}
                <div className="result-image-wrap">
                  <img
                    ref={resultImgRef}
                    src={`data:image/jpeg;base64,${result.overlayB64}`}
                    alt="Corner detection overlay"
                    className="result-img"
                    onLoad={onResultImgLoad}
                  />
                  {result.corners?.map((pt, i) => (
                    <div
                      key={i}
                      className="corner-pin"
                      style={pinPosition(pt[0], pt[1])}
                      title={`${CORNER_LABELS[i]}: (${pt[0]}, ${pt[1]})`}
                    />
                  ))}
                </div>

                {/* Coords */}
                {result.corners?.length === 4 && (
                  <div className="coords-section">
                    <p className="coords-title">Corner Coordinates</p>
                    <div className="coords-grid">
                      {result.corners.map((pt, i) => (
                        <div className="coord-card" key={i}>
                          <div className="coord-label">{CORNER_LABELS[i]}</div>
                          <div className="coord-values">
                            <span className="coord-val"><span>X</span>{pt[0]}</span>
                            <span className="coord-val"><span>Y</span>{pt[1]}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </section>

      </main>
    </div>
  );
}
