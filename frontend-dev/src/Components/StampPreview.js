import React from "react";
// Assuming EosLogo and AldLogo are used elsewhere in your project
import EosLogo from "../Assets/eos-logo.png";
import AldLogo from "../Assets/ald-logo.png";

function StampPreview({
  project,
  projectNumber,
  preparedFor,
  preparedBy,
  issueDate,
  revisionDate,
  revisionNumber,
  jobPhase,
  dateFormat,
  showRevision,
}) {
  const formatDate = (date) => {
    if (!date) return "N/A"; // Default text for empty dates
    const { day, month, year } = date;
    switch (dateFormat) {
      case "YYYY/MM/DD":
        return `${year}/${month}/${day}`;
      case "MM/DD/YYYY":
        return `${month}/${day}/${year}`;
      case "DD/MM/YYYY":
        return `${day}/${month}/${year}`;
      default:
        return `${month} ${day}, ${year}`;
    }
  };

  return (
    <div className="stamp-preview-div">
      <h2>Stamp Preview</h2>
      <div className="stamp-preview-content">
        <div className="stamp-preview-column">
          <p>
            <span className="label">Project:</span> {project || "N/A"}
          </p>
          <p>
            <span className="label">Project #:</span> {projectNumber || "N/A"}
          </p>
          <p>
            <span className="label">Prepared for:</span> {preparedFor || "N/A"}
          </p>
          <p>
            <span className="label">Prepared by:</span> {preparedBy || "N/A"}
          </p>
        </div>
        <div className="stamp-preview-column">
          <p>
            <span className="label">Issue Date:</span> {formatDate(issueDate)}
          </p>
          {showRevision && (
            <>
              <p>
                <span className="label">Revision Number:</span>{" "}
                {revisionNumber || "N/A"}
              </p>
              <p>
                <span className="label">Revision Date:</span>{" "}
                {formatDate(revisionDate)}
              </p>
            </>
          )}
          <p>
            <span className="label">Job Phase:</span> {jobPhase || "N/A"}
          </p>
        </div>
        <div className="stamp-preview-column">
          <p className="type-title">type</p>
          <p className="type-number">aCD02</p>
          <p className="page-number">page x of x</p>
        </div>
      </div>
    </div>
  );
}

export default StampPreview;
