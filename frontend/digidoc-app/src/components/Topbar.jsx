import { IconScan } from "./Icons";

export default function Topbar({ hasResult }) {
  return (
    <header className="topbar">
      <div className="topbar-logo">
        <div className="logo-icon">
          <IconScan />
        </div>
        <span className="logo-name">
          Digi<span>Doc</span>
        </span>
      </div>
      <span className="topbar-badge">BETA</span>
      <div className="topbar-spacer" />
      <div className="topbar-status">
        <div className={`status-dot ${hasResult ? "live" : ""}`} />
        {hasResult ? "corners detected" : "awaiting scan"}
      </div>
    </header>
  );
}
