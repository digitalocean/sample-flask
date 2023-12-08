import React from "react";

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
}) {
  const formatDate = (date) => {
    if (!date) return "";
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
            <span className="label">Project:</span> {project}
          </p>
          <p>
            <span className="label">Project #:</span> {projectNumber}
          </p>
          <p>
            <span className="label">Prepared for:</span> {preparedFor}
          </p>
        </div>
        <div className="stamp-preview-column">
          <p>
            <span className="label">Prepared by:</span> {preparedBy}
          </p>
          <p>
            <span className="label">Issue Date:</span> {formatDate(issueDate)}
          </p>
          <p>
            <span className="label">Revision Number:</span> {revisionNumber}
          </p>
          {revisionDate && (
            <p>
              <span className="label">Revision Date:</span>{" "}
              {formatDate(revisionDate)}
            </p>
          )}
          <p>
            <span className="label">Job Phase:</span> {jobPhase}
          </p>
        </div>
        <div className="stamp-preview-column">{/* Reserved for logo */}</div>
      </div>
    </div>
  );
}

export default StampPreview;
