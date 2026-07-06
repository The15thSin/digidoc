import Panel from "./Panel";
import { IconAlert, IconFile, IconScan, IconUpload, IconX } from "./Icons";
import { formatBytes } from "../utils/file";

export default function UploadPanel({
  file,
  previewUrl,
  dragover,
  loading,
  error,
  inputRef,
  onInputChange,
  onDrop,
  onDragOver,
  onDragLeave,
  onClear,
  onDetect,
}) {
  return (
    <Panel label="Input">
      <div
        className={`upload-zone ${dragover ? "dragover" : ""} ${file ? "has-image" : ""}`}
        onClick={() => !file && inputRef.current?.click()}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        {file ? (
          <>
            <img src={previewUrl} alt="Preview" className="preview-img" />
            <button className="clear-btn" onClick={onClear} title="Remove image">
              <IconX />
            </button>
          </>
        ) : (
          <>
            <div className="upload-icon"><IconUpload /></div>
            <div className="upload-text">
              <strong>Drop an image here</strong>
              <span>or click to browse - JPG, PNG, WEBP</span>
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

      {file && (
        <div className="file-meta">
          <IconFile />
          <span className="file-meta-name">{file.name}</span>
          <span className="file-meta-size">{formatBytes(file.size)}</span>
        </div>
      )}

      {error && (
        <div className="error-banner">
          <IconAlert />
          <span>{error}</span>
        </div>
      )}

      <button
        className={`detect-btn ${loading ? "loading" : ""}`}
        onClick={onDetect}
        disabled={!file || loading}
      >
        {loading ? (
          <>
            <div className="spinner" />
            Detecting corners...
          </>
        ) : (
          <>
            <IconScan />
            Detect Corners
          </>
        )}
      </button>
    </Panel>
  );
}
