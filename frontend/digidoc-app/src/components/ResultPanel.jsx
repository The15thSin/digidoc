import { useMemo } from "react";
import Panel from "./Panel";
import { CORNER_LABELS } from "../constants/app";
import { IconCheck, IconResult } from "./Icons";

export default function ResultPanel({
  result,
  previewUrl,
  resultImgRef,
  imgSize,
  onResultImgLoad,
  pinPosition,
}) {
  const cornerPathPoints = useMemo(() => {
    if (!result?.corners?.length || result.corners.length < 4) return "";
    return result.corners.map(([x, y]) => `${x},${y}`).join(" ");
  }, [result]);

  return (
    <Panel label="Result" accent>
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

          <div className="result-image-wrap">
            <img
              ref={resultImgRef}
              src={previewUrl}
              alt="Corner detection overlay"
              className="result-img"
              onLoad={onResultImgLoad}
            />
            {cornerPathPoints && imgSize.w > 0 && imgSize.h > 0 && (
              <svg
                className="corner-lines"
                viewBox={`0 0 ${imgSize.w} ${imgSize.h}`}
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                <polygon points={cornerPathPoints} />
              </svg>
            )}
            {result.corners?.map((pt, i) => (
              <div
                key={i}
                className="corner-pin"
                style={pinPosition(pt[0], pt[1])}
                title={`${CORNER_LABELS[i]}: (${pt[0]}, ${pt[1]})`}
              />
            ))}
          </div>

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
    </Panel>
  );
}
