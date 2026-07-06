import { useCallback, useRef, useState } from "react";
import "./App.css";
import ResultPanel from "./components/ResultPanel";
import Topbar from "./components/Topbar";
import UploadPanel from "./components/UploadPanel";
import { API_BASE } from "./constants/app";
import { fileToBase64 } from "./utils/file";

export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragover, setDragover] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [imgSize, setImgSize] = useState({ w: 0, h: 0 });
  const inputRef = useRef(null);
  const resultImgRef = useRef(null);

  const handleFile = useCallback((nextFile) => {
    if (!nextFile || !nextFile.type.startsWith("image/")) {
      setError("Only image files are supported.");
      return;
    }

    setFile(nextFile);
    setPreviewUrl(URL.createObjectURL(nextFile));
    setResult(null);
    setError(null);
    setImgSize({ w: 0, h: 0 });
  }, []);

  const onInputChange = (event) => {
    const nextFile = event.target.files[0];
    if (nextFile) handleFile(nextFile);
  };

  const onDragOver = (event) => {
    event.preventDefault();
    setDragover(true);
  };

  const onDrop = (event) => {
    event.preventDefault();
    setDragover(false);
    const nextFile = event.dataTransfer.files[0];
    if (nextFile) handleFile(nextFile);
  };

  const onClear = (event) => {
    event?.stopPropagation();
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setImgSize({ w: 0, h: 0 });
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
      setResult({ corners: data.corners });
    } catch (err) {
      setError(err.message || "Detection failed. Is the server running?");
    } finally {
      setLoading(false);
    }
  };

  const onResultImgLoad = () => {
    if (!resultImgRef.current) return;

    setImgSize({
      w: resultImgRef.current.naturalWidth,
      h: resultImgRef.current.naturalHeight,
    });
  };

  const pinPosition = (x, y) => {
    if (!imgSize.w || !imgSize.h) return { left: "0%", top: "0%" };

    return {
      left: `${(x / imgSize.w) * 100}%`,
      top: `${(y / imgSize.h) * 100}%`,
    };
  };

  return (
    <div className="app-shell">
      <Topbar hasResult={Boolean(result)} />
      <main className="workspace">
        <UploadPanel
          file={file}
          previewUrl={previewUrl}
          dragover={dragover}
          loading={loading}
          error={error}
          inputRef={inputRef}
          onInputChange={onInputChange}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={() => setDragover(false)}
          onClear={onClear}
          onDetect={onDetect}
        />
        <ResultPanel
          result={result}
          previewUrl={previewUrl}
          resultImgRef={resultImgRef}
          imgSize={imgSize}
          onResultImgLoad={onResultImgLoad}
          pinPosition={pinPosition}
        />
      </main>
    </div>
  );
}
