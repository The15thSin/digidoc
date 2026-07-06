export default function Panel({ label, accent = false, children }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <span className={accent ? "panel-label-accent" : "panel-label"}>{label}</span>
      </div>
      <div className="panel-body">{children}</div>
    </section>
  );
}
